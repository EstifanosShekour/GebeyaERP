frappe.pages["gebeya-dashboard"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "Gebeya Dashboard",
        single_column: true,
    });

    $("<style>").text(`
        .gd-wrap { padding:20px; }
        .gd-header { margin-bottom:24px; }
        .gd-header h2 { font-size:22px; font-weight:700; color:#1f2937; margin:0 0 4px; }
        .gd-header p { color:#6b7280; font-size:13px; margin:0; }
        .gd-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));
            gap:16px;
            margin-bottom:28px;
        }
        .gd-card {
            background:#fff; border:1px solid #e5e7eb; border-radius:10px;
            padding:20px; text-align:center; cursor:pointer; transition:box-shadow .15s;
        }
        .gd-card:hover { box-shadow:0 4px 12px rgba(0,0,0,.08); }
        .gd-card.alert { border-color:#f59e0b; background:#fffbeb; }
        .gd-label { font-size:11px; color:#6b7280; text-transform:uppercase; letter-spacing:.6px; margin-bottom:8px; }
        .gd-value { font-size:26px; font-weight:700; color:#1f2937; margin-bottom:4px; }
        .gd-card.alert .gd-value { color:#b45309; }
        .gd-sub { font-size:11px; color:#9ca3af; }
        .gd-actions { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:28px; }
        .gd-actions .btn { font-size:13px; }
        .gd-section-title { font-size:14px; font-weight:600; color:#374151; margin:0 0 12px; }
        .gd-low-table { width:100%; border-collapse:collapse; font-size:13px; }
        .gd-low-table th {
            text-align:left; padding:8px 12px; background:#f9fafb;
            border:1px solid #e5e7eb; color:#6b7280; font-weight:500;
        }
        .gd-low-table td { padding:8px 12px; border:1px solid #e5e7eb; }
        .gd-low-table tr:nth-child(even) td { background:#fafafa; }
        .gd-refresh { float:right; margin-top:-4px; }
        .gd-onboarding {
            display:none; background:#eff6ff; border:1px solid #bfdbfe;
            border-radius:10px; padding:24px 28px; margin-bottom:20px;
        }
        .gd-onboarding h3 { font-size:16px; font-weight:700; color:#1d4ed8; margin:0 0 8px; }
        .gd-onboarding p { color:#1e40af; font-size:13px; margin:0 0 12px; }
        .gd-onboarding ol { color:#1e40af; font-size:13px; margin:0; padding-left:20px; }
        .gd-onboarding li { margin-bottom:6px; }
        .gd-onboarding li strong { color:#1d4ed8; }
    `).appendTo("head");

    page.main.html(`
        <div class="gd-wrap">
            <div class="gd-header">
                <span class="gd-refresh">
                    <a href="#" id="gd-refresh-link" style="font-size:12px;color:#9ca3af;">&#8635; Refresh</a>
                </span>
                <h2 id="gd-shop-name">Gebeya Dashboard</h2>
                <p id="gd-date"></p>
            </div>

            <div class="gd-grid">
                <div class="gd-card" id="card-todays-sales">
                    <div class="gd-label">Today&#39;s Sales</div>
                    <div class="gd-value" id="val-todays-sales">&#8230;</div>
                    <div class="gd-sub" id="sub-todays-sales">&nbsp;</div>
                </div>
                <div class="gd-card" id="card-monthly">
                    <div class="gd-label">This Month</div>
                    <div class="gd-value" id="val-monthly-sales">&#8230;</div>
                    <div class="gd-sub">&nbsp;</div>
                </div>
                <div class="gd-card" id="card-invoices">
                    <div class="gd-label">Invoices Today</div>
                    <div class="gd-value" id="val-invoices-today">&#8230;</div>
                    <div class="gd-sub">&nbsp;</div>
                </div>
                <div class="gd-card" id="card-low-stock">
                    <div class="gd-label">Low Stock Items</div>
                    <div class="gd-value" id="val-low-stock">&#8230;</div>
                    <div class="gd-sub" id="sub-low-stock">&nbsp;</div>
                </div>
                <div class="gd-card" id="card-outstanding">
                    <div class="gd-label">Outstanding Credit</div>
                    <div class="gd-value" id="val-outstanding">&#8230;</div>
                    <div class="gd-sub">&nbsp;</div>
                </div>
                <div class="gd-card" id="card-employees">
                    <div class="gd-label">Active Employees</div>
                    <div class="gd-value" id="val-employees">&#8230;</div>
                    <div class="gd-sub">&nbsp;</div>
                </div>
                <div class="gd-card" id="card-top-item">
                    <div class="gd-label">Top Item Today</div>
                    <div class="gd-value" id="val-top-item" style="font-size:16px;line-height:1.3;">&#8230;</div>
                    <div class="gd-sub">&nbsp;</div>
                </div>
            </div>

            <div class="gd-actions">
                <button class="btn btn-primary" id="btn-new-sale">+ New Sale</button>
                <button class="btn btn-default" id="btn-products">Products</button>
                <button class="btn btn-default" id="btn-customers">Customers</button>
                <button class="btn btn-default" id="btn-stock-in">Stock In</button>
                <button class="btn btn-default" id="btn-pulsecheck">PulseCheck AI</button>
            </div>

            <div class="gd-onboarding" id="gd-onboarding">
                <h3>Welcome to Gebeya ERP!</h3>
                <p>Your shop is set up and ready. Here&#39;s how to get started:</p>
                <ol>
                    <li><strong>+ New Sale</strong> &mdash; record your first transaction</li>
                    <li><strong>Products</strong> &mdash; add your items and set reorder points</li>
                    <li><strong>Stock In</strong> &mdash; receive your opening inventory</li>
                    <li><strong>PulseCheck</strong> &mdash; run an AI strategy analysis once you have data</li>
                </ol>
            </div>

            <div id="gd-low-stock-section" style="display:none;margin-top:8px;">
                <div class="gd-section-title">Low Stock Items</div>
                <table class="gd-low-table">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Warehouse</th>
                            <th style="text-align:right;">Stock</th>
                            <th style="text-align:right;">Reorder At</th>
                        </tr>
                    </thead>
                    <tbody id="gd-low-stock-rows"></tbody>
                </table>
            </div>
        </div>
    `);

    // ── Navigation bindings ───────────────────────────────────────────────────
    var today = frappe.datetime.get_today();

    $("#card-todays-sales,#card-invoices").on("click", function () {
        frappe.set_route("List", "Sales Invoice", { posting_date: today, docstatus: 1 });
    });
    $("#card-monthly").on("click", function () {
        frappe.set_route("List", "Sales Invoice", { docstatus: 1 });
    });
    $("#card-low-stock").on("click", function () {
        frappe.set_route("List", "Item");
    });
    $("#card-outstanding").on("click", function () {
        frappe.set_route("query-report", "Gebeya Customer Summary");
    });
    $("#card-employees").on("click", function () {
        frappe.set_route("List", "Employee", { status: "Active" });
    });
    $("#card-top-item").on("click", function () {
        frappe.set_route("List", "Sales Invoice", { posting_date: today, docstatus: 1 });
    });

    $("#btn-new-sale").on("click", function () { frappe.new_doc("Sales Invoice"); });
    $("#btn-products").on("click", function () { frappe.set_route("List", "Item"); });
    $("#btn-customers").on("click", function () { frappe.set_route("List", "Customer"); });
    $("#btn-stock-in").on("click", function () { frappe.new_doc("Purchase Receipt"); });
    $("#btn-pulsecheck").on("click", function () { frappe.set_route("app", "pulsecheck"); });

    // ── Format helpers ────────────────────────────────────────────────────────
    function etb(n) {
        return "ETB\u00a0" + parseFloat(n || 0).toLocaleString("en-US", {
            minimumFractionDigits: 2, maximumFractionDigits: 2,
        });
    }

    function setLoading() {
        $("#val-todays-sales,#val-monthly-sales,#val-invoices-today," +
          "#val-low-stock,#val-outstanding,#val-employees,#val-top-item").text("\u2026");
    }

    // ── Date header ───────────────────────────────────────────────────────────
    $("#gd-date").text(frappe.datetime.str_to_user(today));

    // ── Shop name ─────────────────────────────────────────────────────────────
    frappe.db.get_single_value("Shop Settings", "shop_name").then(function (name) {
        if (name) $("#gd-shop-name").text(name + " \u2014 Dashboard");
    });

    // ── Main data load ────────────────────────────────────────────────────────
    function loadDashboard() {
        var company = frappe.defaults.get_user_default("Company");

        frappe.call({
            method: "gebeyaerp.services.dashboard.get_dashboard_data",
            args: { company: company },
            callback: function (r) {
                if (!r.message) return;
                var d = r.message;

                $("#val-todays-sales").text(etb(d.todays_sales));
                $("#sub-todays-sales").text(d.invoices_today + " invoice(s)");
                $("#val-monthly-sales").text(etb(d.monthly_sales));
                $("#val-invoices-today").text(d.invoices_today);
                $("#val-low-stock").text(d.low_stock_count);
                $("#val-outstanding").text(etb(d.outstanding_credit));
                $("#val-employees").text(d.employee_count);
                $("#val-top-item").text(d.top_item || "\u2014");

                if (d.low_stock_count > 0) {
                    $("#card-low-stock").addClass("alert");
                    $("#sub-low-stock").text("action needed");
                } else {
                    $("#card-low-stock").removeClass("alert");
                    $("#sub-low-stock").text("all good");
                }

                // Show onboarding banner for fresh shops with no activity yet
                var isFreshShop = (
                    (!d.todays_sales || d.todays_sales === 0) &&
                    (!d.monthly_sales || d.monthly_sales === 0) &&
                    (!d.invoices_today || d.invoices_today === 0)
                );
                if (isFreshShop) {
                    $("#gd-onboarding").show();
                } else {
                    $("#gd-onboarding").hide();
                }
            },
        });

        frappe.call({
            method: "gebeyaerp.services.dashboard.get_low_stock_items",
            args: { company: company },
            callback: function (r) {
                if (!r.message || !r.message.length) {
                    $("#gd-low-stock-section").hide();
                    return;
                }
                var rows = r.message.map(function (item) {
                    return "<tr>" +
                        "<td>" + (item.item_name || item.item_code) + "</td>" +
                        "<td style='color:#6b7280;font-size:12px;'>" + (item.warehouse || "") + "</td>" +
                        "<td style='text-align:right;font-weight:600;color:#b45309;'>" + (item.actual_qty || 0) + "</td>" +
                        "<td style='text-align:right;'>" + (item.reorder_point || 0) + "</td>" +
                        "</tr>";
                }).join("");
                $("#gd-low-stock-rows").html(rows);
                $("#gd-low-stock-section").show();
            },
        });
    }

    loadDashboard();

    $("#gd-refresh-link").on("click", function (e) {
        e.preventDefault();
        setLoading();
        loadDashboard();
    });
};
