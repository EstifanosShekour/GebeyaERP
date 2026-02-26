frappe.ui.form.on("Sales Invoice", {
    onload: function (frm) {
        if (!frm.is_new()) return;

        // Default to Walk-in Customer for new invoices
        if (!frm.doc.customer) {
            frm.set_value("customer", "Walk-in Customer");
        }

        // Auto-select the correct tax template from Shop Settings
        frappe.db.get_single_value("Shop Settings", "tax_type").then(function (tax_type) {
            if (!tax_type || tax_type === "None" || frm.doc.taxes_and_charges) return;

            frappe.db
                .get_list("Sales Taxes and Charges Template", {
                    filters: { title: ["like", "%" + tax_type + "%"] },
                    fields: ["name"],
                    limit: 1,
                })
                .then(function (results) {
                    if (results && results.length > 0) {
                        frm.set_value("taxes_and_charges", results[0].name);
                        frm.trigger("taxes_and_charges");
                    }
                });
        });
    },

    refresh: function (frm) {
        if (frm.doc.docstatus !== 1) return;

        frm.add_custom_button(__("Print Receipt"), function () {
            frappe.utils.print(
                frm.doctype,
                frm.docname,
                "Gebeya Receipt",
                frm.doc.letter_head,
                frm.doc.language
            );
        }, __("Print"));
    },

    after_submit: function (frm) {
        frappe.call({
            method: "gebeyaerp.services.dashboard.get_low_stock_items",
            callback: function (r) {
                if (!r.message || r.message.length === 0) return;

                var items = r.message.slice(0, 5);
                var rows = items.map(function (item) {
                    return (
                        "<tr>" +
                        "<td style='padding:4px 8px;'>" + item.item_name + "</td>" +
                        "<td style='padding:4px 8px;text-align:right;'>" + item.actual_qty + "</td>" +
                        "<td style='padding:4px 8px;text-align:right;'>" + item.reorder_point + "</td>" +
                        "</tr>"
                    );
                });

                var more = r.message.length > 5
                    ? "<p style='color:#6b7280;margin-top:8px;'>+ " + (r.message.length - 5) + " more items</p>"
                    : "";

                frappe.msgprint({
                    title: __("Low Stock Alert"),
                    indicator: "orange",
                    message:
                        "<p>The following items are at or below their reorder point:</p>" +
                        "<table style='width:100%;border-collapse:collapse;'>" +
                        "<thead><tr style='border-bottom:1px solid #e5e7eb;'>" +
                        "<th style='padding:4px 8px;text-align:left;'>Item</th>" +
                        "<th style='padding:4px 8px;text-align:right;'>Stock</th>" +
                        "<th style='padding:4px 8px;text-align:right;'>Reorder At</th>" +
                        "</tr></thead>" +
                        "<tbody>" + rows.join("") + "</tbody>" +
                        "</table>" + more,
                });
            },
        });
    },
});
