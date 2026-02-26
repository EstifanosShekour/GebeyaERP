"""PulseCheck KPI calculation engine.

Ported from PulseCheck's JavaScript kpi.js.
All formulas are identical to the original implementation.
"""


def safe_div(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is 0."""
    try:
        if denominator == 0 or denominator is None:
            return default
        return round(numerator / denominator, 2)
    except (TypeError, ZeroDivisionError):
        return default


def pct(value):
    """Format a ratio as a percentage string, e.g. 0.153 → '15.3%'."""
    try:
        return f"{round(value * 100, 1)}%"
    except (TypeError, ValueError):
        return "0.0%"


def _g(d, key, default=0):
    """Get a numeric value from dict d, defaulting to 0 on None/missing."""
    v = d.get(key, default)
    return v if v is not None else default


def calc_financial_kpis(d):
    """Calculate 17 financial KPIs.

    Categories: Liquidity (3), Solvency (4), Profitability (4),
    DuPont Analysis (3), Market Valuation (3).

    Args:
        d: dict with financial data fields

    Returns:
        Nested dict of KPI categories and metrics
    """
    cash        = _g(d, "cash_equivalents")
    ar          = _g(d, "accounts_receivable")
    inventory   = _g(d, "inventory")
    ppe         = _g(d, "fixed_assets_ppe")
    intangibles = _g(d, "intangible_assets")
    ap          = _g(d, "accounts_payable")
    accrued     = _g(d, "accrued_expenses")
    se          = _g(d, "shareholders_equity")
    revenue     = _g(d, "Revenue")
    gross_profit= _g(d, "Gross_Profit")
    net_income  = _g(d, "Net_Income")
    ebit        = _g(d, "EBIT")
    ebitda      = _g(d, "EBITDA")
    interest    = _g(d, "Interest_Expense")
    price       = _g(d, "stock_price")
    shares      = _g(d, "shares_outstanding")
    ltd         = _g(d, "long_term_debt")

    ca = cash + ar + inventory
    ta = ca + ppe + intangibles
    cl = ap + accrued

    eps = safe_div(net_income, shares)

    return {
        "Liquidity": {
            "Current_Ratio":  safe_div(ca, cl),
            "Quick_Ratio":    safe_div(ca - inventory, cl),
            "Cash_Ratio":     safe_div(cash, cl),
        },
        "Solvency": {
            "Debt_Ratio":        safe_div(ta - se, ta),
            "Equity_Multiplier": safe_div(ta, se),
            "TIE":               safe_div(ebit, interest),
            "Cash_Coverage":     safe_div(ebitda, interest),
        },
        "Profitability": {
            "Gross_Margin":      pct(safe_div(gross_profit, revenue)),
            "Net_Profit_Margin": pct(safe_div(net_income, revenue)),
            "ROA":               pct(safe_div(net_income, ta)),
            "ROE":               pct(safe_div(net_income, se)),
        },
        "DuPont": {
            "Profit_Margin":  pct(safe_div(net_income, revenue)),
            "Asset_Turnover": safe_div(revenue, ta),
            "Leverage":       safe_div(ta, se),
        },
        "Market": {
            "PE_Ratio":       safe_div(price, eps) if eps else 0,
            "Market_to_Book": safe_div(price * shares, se),
            "EV_EBITDA":      safe_div((price * shares) + ltd - cash, ebitda),
        },
    }


def calc_marketing_kpis(d):
    """Calculate 10 marketing KPIs.

    Categories: Acquisition (3), Retention (3), Unit Economics (4).

    Args:
        d: dict with marketing data fields

    Returns:
        Nested dict of KPI categories and metrics
    """
    revenue           = _g(d, "revenue")
    gross_margin      = _g(d, "gross_margin")
    marketing_spend   = _g(d, "marketing_spend")
    customers_start   = _g(d, "customers_start")
    customers_end     = _g(d, "customers_end")
    new_customers     = _g(d, "new_customers")
    arpu              = _g(d, "arpu")
    expansion_revenue = _g(d, "expansion_revenue")

    cac      = safe_div(marketing_spend, new_customers)
    lost     = (customers_start + new_customers) - customers_end
    churn    = safe_div(lost, customers_start)
    retention = 1 - churn

    start_rev = customers_start * arpu
    nrr = safe_div(start_rev + expansion_revenue - (lost * arpu), start_rev)

    ltv     = safe_div(arpu * gross_margin, churn) if churn > 0 else 0
    ltv_cac = safe_div(ltv, cac)
    payback = safe_div(cac, arpu * gross_margin) if (arpu * gross_margin) > 0 else 0

    return {
        "Acquisition": {
            "CAC":                  f"ETB {round(cac, 2)}",
            "Marketing_Spend_Pct":  pct(safe_div(marketing_spend, revenue)),
            "Marketing_Efficiency": safe_div(revenue, marketing_spend),
        },
        "Retention": {
            "Retention_Rate":        pct(retention),
            "Churn_Rate":            pct(churn),
            "Net_Revenue_Retention": pct(nrr),
        },
        "Unit_Economics": {
            "LTV":                   f"ETB {round(ltv, 2)}",
            "LTV_CAC_Ratio":         round(ltv_cac, 2),
            "Payback_Period_Months": round(payback, 2),
            "Status": "Healthy" if ltv_cac >= 3 else "Needs Optimization",
        },
    }


def calc_operating_kpis(d):
    """Calculate 10 operating KPIs.

    Categories: Cash Conversion Cycle (5), Workforce (2), Quality (3).

    Args:
        d: dict with operating data fields

    Returns:
        Nested dict of KPI categories and metrics
    """
    revenue    = _g(d, "Revenue")
    cogs       = _g(d, "COGS")
    net_income = _g(d, "Net_Income")
    inventory  = _g(d, "inventory")
    ar         = _g(d, "accounts_receivable")
    ap         = _g(d, "accounts_payable")
    employees  = _g(d, "employees")
    produced   = _g(d, "units_produced")
    capacity   = _g(d, "total_capacity")
    defective  = _g(d, "defective_units")
    on_time    = _g(d, "orders_on_time")
    total_ord  = _g(d, "orders_total")

    inv_t = safe_div(cogs, inventory)
    rec_t = safe_div(revenue, ar)
    pay_t = safe_div(cogs, ap)
    dsi   = safe_div(365, inv_t) if inv_t else 0
    dso   = safe_div(365, rec_t) if rec_t else 0
    dpo   = safe_div(365, pay_t) if pay_t else 0

    return {
        "Cash_Conversion": {
            "Inventory_Turnover":       round(inv_t, 2),
            "Days_Sales_Inventory":     round(dsi, 2),
            "Days_Sales_Outstanding":   round(dso, 2),
            "Days_Payable_Outstanding": round(dpo, 2),
            "Cash_Conversion_Cycle":    round(dsi + dso - dpo, 2),
        },
        "Workforce": {
            "Revenue_Per_Employee": f"ETB {round(safe_div(revenue, employees)):,}",
            "Profit_Per_Employee":  f"ETB {round(safe_div(net_income, employees)):,}",
        },
        "Quality": {
            "Capacity_Utilization": pct(safe_div(produced, capacity)),
            "Defect_Rate":          pct(safe_div(defective, produced)),
            "On_Time_Delivery":     pct(safe_div(on_time, total_ord)),
        },
    }
