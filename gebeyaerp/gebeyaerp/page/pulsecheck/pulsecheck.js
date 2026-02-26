frappe.pages["pulsecheck"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "PulseCheck — AI Strategy Board",
        single_column: true,
    });

    // ── Styles ───────────────────────────────────────────────────────────────
    $("<style>").text(`
        .pc-form { background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:24px; margin-bottom:20px; }
        .pc-form .form-row { display:grid; grid-template-columns:1fr 1fr 1fr auto; gap:12px; align-items:flex-end; }
        .pc-form label { font-size:12px; color:#6b7280; display:block; margin-bottom:4px; }
        .pc-form select, .pc-form input[type=date] {
            width:100%; padding:6px 10px; border:1px solid #d1d5db; border-radius:6px; font-size:13px;
        }
        .pc-history { margin-bottom:20px; }
        .pc-history select { padding:6px 10px; border:1px solid #d1d5db; border-radius:6px; font-size:13px; width:320px; }
        .pc-status-banner { padding:12px 16px; border-radius:6px; margin-bottom:16px; font-size:13px; display:none; }
        .pc-status-banner.processing { background:#fef3c7; border:1px solid #f59e0b; color:#92400e; }
        .pc-status-banner.error { background:#fee2e2; border:1px solid #ef4444; color:#7f1d1d; }
        .pc-tabs { display:flex; gap:0; border-bottom:2px solid #e5e7eb; margin-bottom:20px; }
        .pc-tab {
            padding:10px 20px; cursor:pointer; font-size:13px; font-weight:500; color:#6b7280;
            border-bottom:2px solid transparent; margin-bottom:-2px; white-space:nowrap;
        }
        .pc-tab.active { color:#2563eb; border-bottom-color:#2563eb; }
        .pc-tab:hover:not(.active) { color:#374151; }
        .pc-panel { display:none; }
        .pc-panel.active { display:block; }
        .pc-report {
            background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:28px;
            line-height:1.7; font-size:14px;
        }
        .pc-report h1,.pc-report h2 { font-size:16px; font-weight:700; margin:20px 0 8px; color:#1f2937; }
        .pc-report h3 { font-size:14px; font-weight:600; margin:16px 0 6px; color:#374151; }
        .pc-report p { margin:0 0 10px; }
        .pc-report ul,.pc-report ol { margin:0 0 10px; padding-left:20px; }
        .pc-report li { margin-bottom:4px; }
        .pc-report strong { color:#111827; }
        .pc-kpi-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; }
        .pc-kpi-section { background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:16px; }
        .pc-kpi-section h4 { font-size:12px; text-transform:uppercase; letter-spacing:.5px; color:#6b7280; margin:0 0 10px; }
        .pc-kpi-row { display:flex; justify-content:space-between; font-size:13px; padding:3px 0; border-bottom:1px solid #f3f4f6; }
        .pc-kpi-row:last-child { border-bottom:none; }
        .pc-kpi-key { color:#374151; }
        .pc-kpi-val { font-weight:600; color:#1f2937; }
        .pc-meta { color:#6b7280; font-size:12px; margin-bottom:16px; }
        .pc-spinner { text-align:center; padding:60px; color:#6b7280; }
    `).appendTo("head");

    // ── HTML skeleton ────────────────────────────────────────────────────────
    page.main.html(`
        <div style="padding:20px;">
            <div class="pc-form">
                <div class="form-row">
                    <div>
                        <label>Company</label>
                        <select id="pc-company"></select>
                    </div>
                    <div>
                        <label>From Date</label>
                        <input type="date" id="pc-from">
                    </div>
                    <div>
                        <label>To Date</label>
                        <input type="date" id="pc-to">
                    </div>
                    <div>
                        <button class="btn btn-primary" id="pc-run-btn">Run Analysis</button>
                    </div>
                </div>
            </div>

            <div class="pc-history">
                <label style="font-size:12px;color:#6b7280;">Past Reports &nbsp;</label>
                <select id="pc-past-reports">
                    <option value="">— select a past report —</option>
                </select>
            </div>

            <div class="pc-status-banner" id="pc-banner"></div>

            <div id="pc-results" style="display:none;">
                <div class="pc-meta" id="pc-meta"></div>
                <div class="pc-tabs">
                    <div class="pc-tab active" data-panel="panel-consultant">Board Report</div>
                    <div class="pc-tab" data-panel="panel-cfo">CFO</div>
                    <div class="pc-tab" data-panel="panel-cmo">CMO</div>
                    <div class="pc-tab" data-panel="panel-coo">COO</div>
                    <div class="pc-tab" data-panel="panel-kpis">KPIs</div>
                    <div class="pc-tab" data-panel="panel-intel">Market Intel</div>
                </div>
                <div class="pc-panel active" id="panel-consultant">
                    <div class="pc-report" id="report-consultant"></div>
                </div>
                <div class="pc-panel" id="panel-cfo">
                    <div class="pc-report" id="report-cfo"></div>
                </div>
                <div class="pc-panel" id="panel-cmo">
                    <div class="pc-report" id="report-cmo"></div>
                </div>
                <div class="pc-panel" id="panel-coo">
                    <div class="pc-report" id="report-coo"></div>
                </div>
                <div class="pc-panel" id="panel-kpis">
                    <div class="pc-kpi-grid" id="kpi-grid"></div>
                </div>
                <div class="pc-panel" id="panel-intel">
                    <div class="pc-report" id="report-intel"></div>
                </div>
            </div>

            <div class="pc-spinner" id="pc-spinner" style="display:none;">
                <div style="font-size:32px;margin-bottom:16px;">&#8987;</div>
                <div style="font-size:16px;font-weight:600;margin-bottom:8px;">Analysing your business&hellip;</div>
                <div style="color:#9ca3af;">Gathering market intelligence and running 4 specialist AI reports.</div>
                <div style="color:#9ca3af;margin-top:4px;">This typically takes 60&ndash;120 seconds.</div>
            </div>
        </div>
    `);

    // ── Tab switching ────────────────────────────────────────────────────────
    page.main.on("click", ".pc-tab", function () {
        $(".pc-tab").removeClass("active");
        $(".pc-panel").removeClass("active");
        $(this).addClass("active");
        $("#" + $(this).data("panel")).addClass("active");
    });

    // ── Default dates (current month) ────────────────────────────────────────
    var today = frappe.datetime.get_today();
    var firstDay = frappe.datetime.month_start(today);
    $("#pc-from").val(firstDay);
    $("#pc-to").val(today);

    // ── Load companies ────────────────────────────────────────────────────────
    frappe.db.get_list("Company", { fields: ["name"], limit: 20 }).then(function (rows) {
        var sel = $("#pc-company");
        rows.forEach(function (r) {
            sel.append($("<option>").val(r.name).text(r.name));
        });
        var userCompany = frappe.defaults.get_user_default("Company");
        if (userCompany) sel.val(userCompany);
    });

    // ── Load past reports ────────────────────────────────────────────────────
    function loadPastReports() {
        frappe.db.get_list("PulseCheck Report", {
            fields: ["name", "company", "from_date", "to_date", "status", "run_duration"],
            filters: { status: ["in", ["Complete", "Error"]] },
            order_by: "creation desc",
            limit: 20,
        }).then(function (rows) {
            var sel = $("#pc-past-reports").empty().append('<option value="">— select a past report —</option>');
            rows.forEach(function (r) {
                var label = r.name + "  |  " + r.company + "  |  " +
                    r.from_date + " \u2192 " + r.to_date +
                    (r.status === "Error" ? "  [Error]" : "  (" + (r.run_duration || 0) + "s)");
                sel.append($("<option>").val(r.name).text(label));
            });
        });
    }
    loadPastReports();

    $("#pc-past-reports").on("change", function () {
        var name = $(this).val();
        if (name) fetchAndRender(name);
    });

    // ── Run Analysis ─────────────────────────────────────────────────────────
    $("#pc-run-btn").on("click", function () {
        var company   = $("#pc-company").val();
        var from_date = $("#pc-from").val();
        var to_date   = $("#pc-to").val();

        if (!company || !from_date || !to_date) {
            frappe.msgprint(__("Please select a company and date range."));
            return;
        }

        $("#pc-results").hide();
        $("#pc-spinner").show();
        hideBanner();
        $("#pc-run-btn").prop("disabled", true).text("Running\u2026");

        frappe.call({
            method: "gebeyaerp.services.pulsecheck_ai.run_pulsecheck_analysis",
            args: { company: company, from_date: from_date, to_date: to_date },
            timeout: 300,
            callback: function (r) {
                $("#pc-spinner").hide();
                $("#pc-run-btn").prop("disabled", false).text("Run Analysis");
                if (r.exc || !r.message) {
                    showBanner("Analysis failed. Check the PulseCheck Report list for details.", "error");
                    return;
                }
                loadPastReports();
                fetchAndRender(r.message);
            },
            error: function () {
                $("#pc-spinner").hide();
                $("#pc-run-btn").prop("disabled", false).text("Run Analysis");
                showBanner(
                    "Request timed out. The analysis may still be running \u2014 check PulseCheck Report list.",
                    "error"
                );
            },
        });
    });

    // ── Fetch & render a report ───────────────────────────────────────────────
    function fetchAndRender(reportName) {
        frappe.call({
            method: "gebeyaerp.services.pulsecheck_ai.get_pulsecheck_report",
            args: { report_name: reportName },
            callback: function (r) {
                if (r.message) renderReport(r.message);
            },
        });
    }

    function renderReport(data) {
        if (data.status === "Error") {
            showBanner("This report encountered an error. See PulseCheck Report list for the error log.", "error");
            return;
        }

        hideBanner();
        $("#pc-results").show();
        $("#pc-meta").text(
            "Report: " + data.name + "  \u2502  " +
            data.company + "  \u2502  " +
            data.from_date + " \u2192 " + data.to_date +
            "  \u2502  Model: " + (data.claude_model || "\u2014") +
            "  \u2502  Duration: " + (data.run_duration || 0) + "s"
        );

        $(".pc-tab").removeClass("active");
        $(".pc-panel").removeClass("active");
        $(".pc-tab[data-panel='panel-consultant']").addClass("active");
        $("#panel-consultant").addClass("active");

        renderMd("#report-consultant", data.consultant_report);
        renderMd("#report-cfo",        data.cfo_report);
        renderMd("#report-cmo",        data.cmo_report);
        renderMd("#report-coo",        data.coo_report);
        renderMd("#report-intel",      data.intelligence_brief);
        renderKpis(data);
    }

    function renderMd(selector, text) {
        if (!text) {
            $(selector).html("<p style='color:#9ca3af;padding:20px;text-align:center;'>No content.</p>");
            return;
        }
        var html;
        if (frappe.utils && frappe.utils.md_to_html) {
            html = frappe.utils.md_to_html(text);
        } else {
            html = _simpleMarkdown(text);
        }
        $(selector).html(html);
    }

    function _simpleMarkdown(text) {
        return text
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/^### (.+)$/gm, "<h3>$1</h3>")
            .replace(/^## (.+)$/gm, "<h2>$1</h2>")
            .replace(/^# (.+)$/gm, "<h1>$1</h1>")
            .replace(/^\- (.+)$/gm, "<li>$1</li>")
            .replace(/\n\n+/g, "</p><p>")
            .replace(/\n/g, "<br>");
    }

    function renderKpis(data) {
        var grid = $("#kpi-grid").empty();
        var sections = [];
        try { var fk = JSON.parse(data.financial_kpis || "{}"); _collectSections(sections, fk, "Financial"); } catch (e) {}
        try { var mk = JSON.parse(data.marketing_kpis || "{}"); _collectSections(sections, mk, "Marketing"); } catch (e) {}
        try { var ok = JSON.parse(data.operating_kpis || "{}"); _collectSections(sections, ok, "Operations"); } catch (e) {}

        if (!sections.length) {
            grid.html("<p style='color:#9ca3af;'>KPI data not available.</p>");
            return;
        }
        sections.forEach(function (s) {
            var rows = s.rows.map(function (r) {
                return "<div class='pc-kpi-row'><span class='pc-kpi-key'>" +
                    r.key.replace(/_/g, " ") + "</span><span class='pc-kpi-val'>" + r.val + "</span></div>";
            }).join("");
            grid.append("<div class='pc-kpi-section'><h4>" + s.title + "</h4>" + rows + "</div>");
        });
    }

    function _collectSections(out, obj, prefix) {
        Object.keys(obj || {}).forEach(function (cat) {
            var catObj = obj[cat];
            if (typeof catObj !== "object" || catObj === null) return;
            var rows = Object.keys(catObj).map(function (k) {
                return { key: k, val: catObj[k] };
            });
            if (rows.length) out.push({ title: prefix + " \u2014 " + cat.replace(/_/g, " "), rows: rows });
        });
    }

    function showBanner(msg, type) {
        $("#pc-banner").text(msg).removeClass("processing error").addClass(type).show();
    }
    function hideBanner() { $("#pc-banner").hide(); }
};
