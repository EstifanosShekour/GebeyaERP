frappe.ui.form.on("Customer", {
    refresh: function (frm) {
        if (frm.is_new()) return;

        // ── Purchase History button ──────────────────────────────────────
        frm.add_custom_button(__("Purchase History"), function () {
            frappe.set_route("List", "Sales Invoice", { customer: frm.doc.name });
        }, __("View"));

        // ── Customer Summary report button ───────────────────────────────
        frm.add_custom_button(__("Customer Summary"), function () {
            frappe.set_route("query-report", "Gebeya Customer Summary");
        }, __("View"));

        // ── Credit & purchase stats ──────────────────────────────────────
        frappe.call({
            method: "gebeyaerp.services.customer.get_customer_credit",
            args: { customer: frm.doc.name },
            callback: function (r) {
                if (!r.message) return;
                var d = r.message;

                var total = frappe.format(d.total_purchases, { fieldtype: "Currency" });
                var outstanding = frappe.format(d.outstanding, { fieldtype: "Currency" });

                if (d.outstanding > 0) {
                    frm.set_intro(
                        __("Total Purchases: ETB {0} &nbsp;|&nbsp; Outstanding Credit: ETB {1} ({2} unpaid invoice(s))", [
                            total,
                            outstanding,
                            d.invoice_count,
                        ]),
                        "orange"
                    );
                } else if (d.total_purchases > 0) {
                    frm.set_intro(
                        __("Total Purchases: ETB {0} &nbsp;|&nbsp; No outstanding credit.", [total]),
                        "green"
                    );
                }
            },
        });
    },
});
