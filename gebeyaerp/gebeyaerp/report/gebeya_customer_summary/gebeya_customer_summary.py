"""Gebeya Customer Summary — Script Report.

Shows all customers with their purchase totals, outstanding credit,
invoice count, and last purchase date.
"""

import frappe
from frappe import _


def execute(filters=None):
    columns = _get_columns()
    data = _get_data(filters or {})
    return columns, data


def _get_columns():
    return [
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200,
        },
        {
            "fieldname": "phone",
            "label": _("Phone"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "total_invoices",
            "label": _("Invoices"),
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "fieldname": "total_purchases",
            "label": _("Total Purchases (ETB)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 170,
        },
        {
            "fieldname": "outstanding_credit",
            "label": _("Outstanding Credit (ETB)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 185,
        },
        {
            "fieldname": "last_purchase",
            "label": _("Last Purchase"),
            "fieldtype": "Date",
            "width": 120,
        },
    ]


def _get_data(filters):
    company = filters.get("company")

    company_condition = ""
    values = {}

    if company:
        company_condition = "AND si.company = %(company)s"
        values["company"] = company

    rows = frappe.db.sql(
        f"""
        SELECT
            c.name                                    AS customer,
            c.custom_phone                            AS phone,
            COUNT(si.name)                            AS total_invoices,
            COALESCE(SUM(si.grand_total), 0)          AS total_purchases,
            COALESCE(SUM(si.outstanding_amount), 0)   AS outstanding_credit,
            MAX(si.posting_date)                      AS last_purchase,
            'ETB'                                     AS currency
        FROM `tabCustomer` c
        LEFT JOIN `tabSales Invoice` si
            ON si.customer = c.name
            AND si.docstatus = 1
            {company_condition}
        WHERE c.disabled = 0
        GROUP BY c.name, c.custom_phone
        ORDER BY total_purchases DESC
        """,
        values,
        as_dict=True,
    )
    return rows
