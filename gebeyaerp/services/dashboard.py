"""Dashboard data aggregation for Gebeya ERP.

Provides whitelisted methods to fetch dashboard metrics:
- Today's sales total
- Monthly sales total
- Invoice count
- Low stock items
- Outstanding credit
- Employee count
"""

import frappe
from frappe.utils import today, getdate, get_first_day, get_last_day


@frappe.whitelist()
def get_dashboard_data(company=None):
    """Fetch all dashboard metrics in a single call.

    Args:
        company: Company name. If None, uses the default company.

    Returns:
        dict with keys: todays_sales, monthly_sales, invoices_today,
        low_stock_count, outstanding_credit, employee_count, top_item
    """
    if not company:
        company = frappe.defaults.get_user_default("Company")

    date_today = today()
    month_start = get_first_day(date_today)
    month_end = get_last_day(date_today)

    todays_sales = frappe.db.sql(
        """
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND company = %s
          AND posting_date = %s
        """,
        (company, date_today),
    )[0][0] or 0

    monthly_sales = frappe.db.sql(
        """
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND company = %s
          AND posting_date BETWEEN %s AND %s
        """,
        (company, month_start, month_end),
    )[0][0] or 0

    invoices_today = frappe.db.sql(
        """
        SELECT COUNT(*)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND company = %s
          AND posting_date = %s
        """,
        (company, date_today),
    )[0][0] or 0

    low_stock_count = frappe.db.sql(
        """
        SELECT COUNT(DISTINCT b.item_code)
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.disabled = 0
          AND i.is_stock_item = 1
          AND i.custom_reorder_point > 0
          AND b.actual_qty <= i.custom_reorder_point
        """
    )[0][0] or 0

    outstanding_credit = frappe.db.sql(
        """
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND company = %s
          AND outstanding_amount > 0
        """,
        (company,),
    )[0][0] or 0

    employee_count = frappe.db.sql(
        """
        SELECT COUNT(*)
        FROM `tabEmployee`
        WHERE status = 'Active'
          AND company = %s
        """,
        (company,),
    )[0][0] or 0

    top_item_row = frappe.db.sql(
        """
        SELECT sii.item_name, SUM(sii.qty) AS total_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND si.company = %s
          AND si.posting_date = %s
        GROUP BY sii.item_code
        ORDER BY total_qty DESC
        LIMIT 1
        """,
        (company, date_today),
    )
    top_item = top_item_row[0][0] if top_item_row else None

    return {
        "todays_sales": float(todays_sales),
        "monthly_sales": float(monthly_sales),
        "invoices_today": int(invoices_today),
        "low_stock_count": int(low_stock_count),
        "outstanding_credit": float(outstanding_credit),
        "employee_count": int(employee_count),
        "top_item": top_item,
    }


@frappe.whitelist()
def get_low_stock_items(company=None):
    """Return items whose actual stock is at or below their reorder point.

    Args:
        company: Company name. If None, uses the default company.

    Returns:
        list of dicts with keys: item_code, item_name, actual_qty,
        reorder_point, warehouse
    """
    if not company:
        company = frappe.defaults.get_user_default("Company")

    rows = frappe.db.sql(
        """
        SELECT
            b.item_code,
            i.item_name,
            b.actual_qty,
            i.custom_reorder_point AS reorder_point,
            b.warehouse
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.disabled = 0
          AND i.is_stock_item = 1
          AND i.custom_reorder_point > 0
          AND b.actual_qty <= i.custom_reorder_point
        ORDER BY (b.actual_qty - i.custom_reorder_point) ASC
        LIMIT 50
        """,
        as_dict=True,
    )

    return rows
