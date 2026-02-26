frappe.ui.form.on("Employee", {
    refresh: function (frm) {
        if (frm.is_new()) return;

        // ── View Attendance button ───────────────────────────────────────
        frm.add_custom_button(__("Attendance"), function () {
            frappe.set_route("List", "Attendance", { employee: frm.doc.name });
        }, __("View"));

        // ── Mark Today's Attendance shortcut ────────────────────────────
        frm.add_custom_button(__("Mark Today's Attendance"), function () {
            var today = frappe.datetime.get_today();

            frappe.db.exists("Attendance", {
                employee: frm.doc.name,
                attendance_date: today,
                docstatus: ["!=", 2],
            }).then(function (existing) {
                if (existing) {
                    frappe.msgprint({
                        title: __("Already Marked"),
                        indicator: "blue",
                        message: __("Attendance for {0} has already been recorded today.", [frm.doc.employee_name]),
                    });
                    return;
                }

                var d = new frappe.ui.Dialog({
                    title: __("Mark Attendance — {0}", [frm.doc.employee_name]),
                    fields: [
                        {
                            fieldname: "status",
                            fieldtype: "Select",
                            label: __("Status"),
                            options: "Present\nAbsent\nHalf Day",
                            default: "Present",
                            reqd: 1,
                        },
                        {
                            fieldname: "attendance_date",
                            fieldtype: "Date",
                            label: __("Date"),
                            default: today,
                            reqd: 1,
                        },
                    ],
                    primary_action_label: __("Save"),
                    primary_action: function (values) {
                        frappe.call({
                            method: "frappe.client.insert",
                            args: {
                                doc: {
                                    doctype: "Attendance",
                                    employee: frm.doc.name,
                                    employee_name: frm.doc.employee_name,
                                    attendance_date: values.attendance_date,
                                    status: values.status,
                                    company: frm.doc.company,
                                },
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    d.hide();
                                    frappe.show_alert({
                                        message: __("Attendance marked as {0}", [values.status]),
                                        indicator: "green",
                                    });
                                }
                            },
                        });
                    },
                });
                d.show();
            });
        });
    },
});
