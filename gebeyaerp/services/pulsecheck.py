"""PulseCheck data extraction from ERPNext.

Extracts financial, marketing, and operational data from ERPNext
and formats it for PulseCheck KPI calculations.
"""

import frappe
from frappe.utils import flt, cint


@frappe.whitelist()
def get_financial_snapshot(company, from_date, to_date):
    """Extract financial data from GL entries and Sales/Purchase Invoices.

    Returns:
        dict with keys matching PulseCheck's expected financial format.
    """
    # Revenue from Sales Invoices (net of tax)
    revenue = _sql1("""
        SELECT COALESCE(SUM(net_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s
          AND posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    # COGS from item valuation on Sales Invoice lines
    cogs = _sql1("""
        SELECT COALESCE(SUM(sii.valuation_rate * sii.qty), 0)
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1 AND si.company = %s
          AND si.posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    gross_profit = flt(revenue) - flt(cogs)

    # Operating expenses from GL Entry (Expense accounts, excluding COGS-type)
    op_expenses = _sql1("""
        SELECT COALESCE(SUM(gle.debit - gle.credit), 0)
        FROM `tabGL Entry` gle
        INNER JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.company = %s
          AND gle.is_cancelled = 0
          AND gle.posting_date BETWEEN %s AND %s
          AND acc.root_type = 'Expense'
          AND acc.account_type NOT IN ('Cost of Goods Sold', 'Stock Adjustment')
          AND acc.is_group = 0
    """, (company, from_date, to_date))

    ebit = flt(gross_profit) - flt(op_expenses)

    # Cash & Bank balances (running total, not period-scoped)
    cash = _sql1("""
        SELECT COALESCE(SUM(gle.debit - gle.credit), 0)
        FROM `tabGL Entry` gle
        INNER JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.company = %s
          AND gle.is_cancelled = 0
          AND acc.account_type IN ('Cash', 'Bank')
          AND acc.is_group = 0
    """, (company,))

    # Accounts Receivable — outstanding Sales Invoice balances
    ar = _sql1("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s AND outstanding_amount > 0
    """, (company,))

    # Inventory at current valuation
    inventory = _sql1("""
        SELECT COALESCE(SUM(b.actual_qty * i.valuation_rate), 0)
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.is_stock_item = 1 AND i.disabled = 0
    """)

    # Accounts Payable — outstanding Purchase Invoice balances
    ap = _sql1("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND company = %s AND outstanding_amount > 0
    """, (company,))

    # Simplified equity: assets we can easily measure minus liabilities
    equity = flt(cash) + flt(inventory) - flt(ap)

    return {
        "Revenue":             flt(revenue),
        "COGS":                flt(cogs),
        "Gross_Profit":        flt(gross_profit),
        "operating_expenses":  flt(op_expenses),
        "EBIT":                flt(ebit),
        "EBITDA":              flt(ebit),        # D&A not tracked separately in retail
        "Interest_Expense":    0,
        "Net_Income":          flt(ebit),        # simplified — no tax calc
        "cash_equivalents":    flt(cash),
        "accounts_receivable": flt(ar),
        "inventory":           flt(inventory),
        "accounts_payable":    flt(ap),
        "accrued_expenses":    0,
        "fixed_assets_ppe":    0,
        "intangible_assets":   0,
        "shareholders_equity": flt(equity),
        "long_term_debt":      0,
        "stock_price":         0,
        "shares_outstanding":  0,
    }


@frappe.whitelist()
def get_marketing_snapshot(company, from_date, to_date):
    """Extract marketing/customer data.

    Returns:
        dict with keys: revenue, gross_profit, gross_margin,
        marketing_spend, customers_start, customers_end,
        new_customers, arpu, expansion_revenue
    """
    revenue = _sql1("""
        SELECT COALESCE(SUM(net_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s
          AND posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    cogs = _sql1("""
        SELECT COALESCE(SUM(sii.valuation_rate * sii.qty), 0)
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1 AND si.company = %s
          AND si.posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    gross_profit = flt(revenue) - flt(cogs)
    gross_margin = flt(gross_profit) / flt(revenue) if flt(revenue) > 0 else 0

    # Unique customers who purchased in period
    customers_end = _sql1("""
        SELECT COUNT(DISTINCT customer)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s
          AND posting_date <= %s
          AND customer != 'Walk-in Customer'
    """, (company, to_date))

    customers_start = _sql1("""
        SELECT COUNT(DISTINCT customer)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s
          AND posting_date < %s
          AND customer != 'Walk-in Customer'
    """, (company, from_date))

    new_customers = max(0, cint(customers_end) - cint(customers_start))

    # ARPU for the period
    arpu = flt(revenue) / cint(customers_end) if cint(customers_end) > 0 else flt(revenue)

    return {
        "revenue":           flt(revenue),
        "gross_profit":      flt(gross_profit),
        "gross_margin":      flt(gross_margin),
        "marketing_spend":   0,           # not tracked separately in retail
        "customers_start":   cint(customers_start),
        "customers_end":     cint(customers_end),
        "new_customers":     new_customers,
        "arpu":              flt(arpu),
        "expansion_revenue": 0,
    }


@frappe.whitelist()
def get_operating_snapshot(company, from_date, to_date):
    """Extract operational data.

    Returns:
        dict with keys: Revenue, COGS, Net_Income, inventory,
        accounts_receivable, accounts_payable, employees,
        units_produced, total_capacity, defective_units,
        orders_on_time, orders_total
    """
    revenue = _sql1("""
        SELECT COALESCE(SUM(net_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s
          AND posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    cogs = _sql1("""
        SELECT COALESCE(SUM(sii.valuation_rate * sii.qty), 0)
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1 AND si.company = %s
          AND si.posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    net_income = flt(revenue) - flt(cogs)

    ar = _sql1("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s AND outstanding_amount > 0
    """, (company,))

    ap = _sql1("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND company = %s AND outstanding_amount > 0
    """, (company,))

    inventory = _sql1("""
        SELECT COALESCE(SUM(b.actual_qty * i.valuation_rate), 0)
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.is_stock_item = 1 AND i.disabled = 0
    """)

    employees = _sql1("""
        SELECT COUNT(*) FROM `tabEmployee`
        WHERE status = 'Active' AND company = %s
    """, (company,))

    # Units sold = proxy for production in retail
    units_sold = _sql1("""
        SELECT COALESCE(SUM(sii.qty), 0)
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1 AND si.company = %s
          AND si.posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    total_orders = _sql1("""
        SELECT COUNT(*)
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %s
          AND posting_date BETWEEN %s AND %s
    """, (company, from_date, to_date))

    return {
        "Revenue":           flt(revenue),
        "COGS":              flt(cogs),
        "Net_Income":        flt(net_income),
        "inventory":         flt(inventory),
        "accounts_receivable": flt(ar),
        "accounts_payable":  flt(ap),
        "employees":         cint(employees),
        "units_produced":    cint(units_sold),
        "total_capacity":    cint(units_sold),  # 100% utilization (retail)
        "defective_units":   0,                 # not tracked in retail
        "orders_on_time":    cint(total_orders),
        "orders_total":      cint(total_orders),
    }


# ─── Internal helpers ────────────────────────────────────────────────────────

def _sql1(query, values=None):
    """Run a SQL query and return the first column of the first row."""
    result = frappe.db.sql(query, values or ())
    return result[0][0] if result else 0
