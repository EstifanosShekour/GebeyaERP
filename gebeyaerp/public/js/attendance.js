frappe.ui.form.on("Attendance", {
    onload: function (frm) {
        if (!frm.is_new()) return;

        // Default date to today
        if (!frm.doc.attendance_date) {
            frm.set_value("attendance_date", frappe.datetime.get_today());
        }

        // Default status to Present
        if (!frm.doc.status) {
            frm.set_value("status", "Present");
        }

        // Pre-fill company from Shop Settings
        if (!frm.doc.company) {
            frappe.db.get_single_value("Shop Settings", "company").then(function (company) {
                if (company && !frm.doc.company) {
                    frm.set_value("company", company);
                }
            });
        }
    },

    status: function (frm) {
        // Visual indicator based on status
        var indicators = {
            "Present": "green",
            "Absent": "red",
            "Half Day": "orange",
            "On Leave": "blue",
            "Work From Home": "purple",
        };
        var color = indicators[frm.doc.status] || "gray";
        frm.page.set_indicator(frm.doc.status || __("Draft"), color);
    },
});

// ── Attendance list view: quick-mark bulk attendance ────────────────────────
frappe.listview_settings["Attendance"] = {
    onload: function (listview) {
        listview.page.add_inner_button(__("Mark Bulk Attendance"), function () {
            _show_bulk_attendance_dialog();
        });
    },
};

function _show_bulk_attendance_dialog() {
    var today = frappe.datetime.get_today();

    var d = new frappe.ui.Dialog({
        title: __("Mark Bulk Attendance"),
        fields: [
            {
                fieldname: "attendance_date",
                fieldtype: "Date",
                label: __("Date"),
                default: today,
                reqd: 1,
            },
            {
                fieldname: "status",
                fieldtype: "Select",
                label: __("Status for All"),
                options: "Present\nAbsent\nHalf Day",
                default: "Present",
                reqd: 1,
                description: __("This will mark all active employees with this status."),
            },
        ],
        primary_action_label: __("Mark Attendance"),
        primary_action: function (values) {
            frappe.call({
                method: "gebeyaerp.services.hr.mark_bulk_attendance",
                args: {
                    attendance_date: values.attendance_date,
                    status: values.status,
                },
                freeze: true,
                freeze_message: __("Marking attendance..."),
                callback: function (r) {
                    if (!r.exc && r.message) {
                        d.hide();
                        frappe.show_alert({
                            message: __("{0} attendance record(s) created.", [r.message.created]),
                            indicator: "green",
                        });
                        cur_list && cur_list.refresh();
                    }
                },
            });
        },
    });
    d.show();
}
