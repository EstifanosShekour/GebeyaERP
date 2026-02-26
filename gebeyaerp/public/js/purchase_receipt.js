frappe.ui.form.on("Purchase Receipt", {
    onload: function (frm) {
        if (!frm.is_new()) return;

        // Pre-fill company from Shop Settings if not already set
        if (!frm.doc.company) {
            frappe.db.get_single_value("Shop Settings", "company").then(function (company) {
                if (company) {
                    frm.set_value("company", company);
                }
            });
        }
    },

    after_submit: function (frm) {
        var total_items = (frm.doc.items || []).reduce(function (sum, row) {
            return sum + (row.qty || 0);
        }, 0);

        frappe.msgprint({
            title: __("Stock Updated"),
            indicator: "green",
            message: __(
                "Stock receipt recorded. {0} item line(s) added to inventory.",
                [frm.doc.items ? frm.doc.items.length : 0]
            ),
        });
    },
});
