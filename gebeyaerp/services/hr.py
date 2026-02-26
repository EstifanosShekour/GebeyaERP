"""HR helpers for Gebeya ERP.

Provides whitelisted methods for simplified attendance management.
"""

import frappe
from frappe import _
from frappe.utils import today as get_today


@frappe.whitelist()
def mark_bulk_attendance(attendance_date, status):
    """Mark attendance for all active employees on a given date.

    Skips employees who already have an Attendance record (docstatus != 2)
    for the given date.

    Args:
        attendance_date: Date string (YYYY-MM-DD).
        status: 'Present', 'Absent', or 'Half Day'.

    Returns:
        dict with key 'created' = number of records created.
    """
    allowed_statuses = {"Present", "Absent", "Half Day"}
    if status not in allowed_statuses:
        frappe.throw(_("Invalid status. Must be Present, Absent, or Half Day."))

    company = frappe.db.get_single_value("Shop Settings", "company")

    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active", "company": company},
        fields=["name", "employee_name", "company"],
    )

    if not employees:
        return {"created": 0}

    # Find employees who already have attendance for this date
    already_marked = set(
        frappe.db.sql_list(
            """
            SELECT employee
            FROM `tabAttendance`
            WHERE attendance_date = %s
              AND docstatus != 2
            """,
            (attendance_date,),
        )
    )

    created = 0
    for emp in employees:
        if emp.name in already_marked:
            continue

        try:
            doc = frappe.get_doc(
                {
                    "doctype": "Attendance",
                    "employee": emp.name,
                    "employee_name": emp.employee_name,
                    "attendance_date": attendance_date,
                    "status": status,
                    "company": emp.company or company,
                }
            )
            doc.insert(ignore_permissions=True)
            doc.submit()
            created += 1
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Gebeya ERP: failed to mark attendance for {emp.name}",
            )

    frappe.db.commit()
    return {"created": created}
