frappe.listview_settings["Customer"] = {
    onload: function (listview) {
        listview.page.add_inner_button(__("Customer Summary"), function () {
            frappe.set_route("query-report", "Gebeya Customer Summary");
        });
    },
};
