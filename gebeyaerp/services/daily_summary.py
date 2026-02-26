"""Auto-generate Daily Summary records from Sales Invoice data.

Called by the scheduler at end of each day.
"""

import frappe
from frappe.utils import add_days, today, getdate


def generate_daily_summary():
    """Generate a Daily Summary for yesterday's sales.

    Creates a Daily Summary DocType record with aggregated data
    from all submitted Sales Invoices for the previous day.

    Called via scheduler_events -> daily_long in hooks.py
    """
    target_date = add_days(today(), -1)

    companies = frappe.get_all("Company", fields=["name"], filters={"is_group": 0})
    for row in companies:
        _generate_for_company(target_date, row.name)


def _generate_for_company(target_date, company):
    """Generate (or regenerate) a Daily Summary for a single company."""
    # Skip if already generated
    existing = frappe.db.exists(
        "Daily Summary",
        {"date": target_date, "company": company},
    )
    if existing:
        return

    invoices = frappe.db.sql(
        """
        SELECT
            name,
            grand_total,
            outstanding_amount,
            custom_payment_method
        FROM `tabSales Invoice`
        WHERE docstatus = 1
          AND company = %s
          AND posting_date = %s
        """,
        (company, target_date),
        as_dict=True,
    )

    if not invoices:
        return

    total_sales = sum(inv.grand_total or 0 for inv in invoices)
    total_invoices = len(invoices)

    payment_totals = {
        "Cash": 0.0,
        "Mobile Money": 0.0,
        "Bank Transfer": 0.0,
        "Credit": 0.0,
    }
    for inv in invoices:
        method = inv.custom_payment_method or "Cash"
        amount = inv.grand_total or 0
        if method in payment_totals:
            payment_totals[method] += amount
        else:
            payment_totals["Cash"] += amount

    total_items_sold, top_selling_item = _get_items_summary(company, target_date)
    new_customers = _count_new_customers(company, target_date)

    doc = frappe.get_doc(
        {
            "doctype": "Daily Summary",
            "date": target_date,
            "company": company,
            "total_sales": total_sales,
            "total_invoices": total_invoices,
            "total_items_sold": total_items_sold,
            "top_selling_item": top_selling_item,
            "new_customers": new_customers,
            "cash_collected": payment_totals["Cash"],
            "mobile_money_collected": payment_totals["Mobile Money"],
            "bank_collected": payment_totals["Bank Transfer"],
            "credit_given": payment_totals["Credit"],
        }
    )
    doc.insert(ignore_permissions=True)
    frappe.db.commit()


def _get_items_summary(company, target_date):
    """Return (total_items_sold, top_selling_item_name) for the date."""
    rows = frappe.db.sql(
        """
        SELECT sii.item_name, SUM(sii.qty) AS total_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND si.company = %s
          AND si.posting_date = %s
        GROUP BY sii.item_code
        ORDER BY total_qty DESC
        """,
        (company, target_date),
        as_dict=True,
    )

    total_qty = int(sum(r.total_qty or 0 for r in rows))
    top_item = rows[0].item_name if rows else None
    return total_qty, top_item


def _count_new_customers(company, target_date):
    """Count customers created on the target date for this company."""
    result = frappe.db.sql(
        """
        SELECT COUNT(*)
        FROM `tabCustomer`
        WHERE DATE(creation) = %s
        """,
        (target_date,),
    )
    return result[0][0] if result else 0
