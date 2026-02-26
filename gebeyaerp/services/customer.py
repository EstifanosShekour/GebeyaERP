"""Customer data aggregation for Gebeya ERP.

Provides whitelisted methods for customer purchase history,
credit tracking, and the Customer Summary report backend.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_credit(customer):
    """Return outstanding credit and purchase totals for a single customer.

    Args:
        customer: Customer name (primary key).

    Returns:
        dict with keys: outstanding, invoice_count, total_purchases, last_purchase
    """
    result = frappe.db.sql(
        """
        SELECT
            COALESCE(SUM(outstanding_amount), 0)    AS outstanding,
            COUNT(*)                                 AS invoice_count,
            COALESCE(SUM(grand_total), 0)            AS total_purchases,
            MAX(posting_date)                        AS last_purchase
        FROM `tabSales Invoice`
        WHERE customer = %s
          AND docstatus = 1
        """,
        (customer,),
        as_dict=True,
    )
    return result[0] if result else {
        "outstanding": 0,
        "invoice_count": 0,
        "total_purchases": 0,
        "last_purchase": None,
    }


@frappe.whitelist()
def get_customer_invoices(customer, limit=50):
    """Return recent Sales Invoices for a customer.

    Args:
        customer: Customer name.
        limit: Maximum rows to return (default 50).

    Returns:
        list of dicts with invoice details.
    """
    rows = frappe.db.sql(
        """
        SELECT
            name,
            posting_date,
            grand_total,
            outstanding_amount,
            custom_payment_method,
            status
        FROM `tabSales Invoice`
        WHERE customer = %s
          AND docstatus = 1
        ORDER BY posting_date DESC, creation DESC
        LIMIT %s
        """,
        (customer, int(limit)),
        as_dict=True,
    )
    return rows


@frappe.whitelist()
def get_customer_summary(company=None, search=None, limit=100):
    """Return all customers with aggregated purchase and credit totals.

    Used by the Gebeya Customer Summary report and the customer list view.

    Args:
        company: Filter by company (optional).
        search: Filter customer name by search string (optional).
        limit: Maximum rows (default 100).

    Returns:
        list of dicts: customer, phone, total_invoices, total_purchases,
        outstanding_credit, last_purchase
    """
    conditions = []
    values = {}

    if company:
        conditions.append("si.company = %(company)s")
        values["company"] = company

    where_clause = ("AND " + " AND ".join(conditions)) if conditions else ""

    name_filter = ""
    if search:
        name_filter = "WHERE c.customer_name LIKE %(search)s"
        values["search"] = f"%{search}%"

    rows = frappe.db.sql(
        f"""
        SELECT
            c.name                                          AS customer,
            c.customer_name,
            c.custom_phone                                  AS phone,
            COUNT(si.name)                                  AS total_invoices,
            COALESCE(SUM(si.grand_total), 0)               AS total_purchases,
            COALESCE(SUM(si.outstanding_amount), 0)        AS outstanding_credit,
            MAX(si.posting_date)                            AS last_purchase
        FROM `tabCustomer` c
        LEFT JOIN `tabSales Invoice` si
            ON si.customer = c.name
            AND si.docstatus = 1
            {where_clause}
        {name_filter}
        GROUP BY c.name, c.customer_name, c.custom_phone
        ORDER BY total_purchases DESC
        LIMIT %(limit)s
        """,
        {**values, "limit": int(limit)},
        as_dict=True,
    )
    return rows
