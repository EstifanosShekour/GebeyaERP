import frappe
from frappe.tests.utils import FrappeTestCase

from gebeyaerp.services.pulsecheck_kpis import (
    calc_financial_kpis,
    calc_marketing_kpis,
    calc_operating_kpis,
)


class TestPulseCheckReport(FrappeTestCase):
    """KPI integration tests — no Claude API calls required.

    Validates that the KPI calculation layer returns valid nested dicts
    with the expected category keys, and that data extraction from ERPNext
    returns a dict with the required keys even when there is no data.
    """

    # ── KPI structure tests (pure, no DB) ────────────────────────────────────

    def test_financial_kpis_returns_valid_structure(self):
        result = calc_financial_kpis({})
        self.assertIsInstance(result, dict)
        for category in ("Liquidity", "Solvency", "Profitability", "DuPont", "Market"):
            self.assertIn(category, result, f"Missing category: {category}")
            self.assertIsInstance(result[category], dict)

    def test_marketing_kpis_no_zero_division_with_zero_customers(self):
        result = calc_marketing_kpis({"customers_start": 0, "customers_end": 0})
        self.assertIsNotNone(result)
        for category in ("Acquisition", "Retention", "Unit_Economics"):
            self.assertIn(category, result)

    def test_operating_kpis_no_zero_division_with_zero_inventory(self):
        result = calc_operating_kpis({"inventory": 0, "accounts_receivable": 0, "accounts_payable": 0})
        self.assertIsNotNone(result)
        for category in ("Cash_Conversion", "Workforce", "Quality"):
            self.assertIn(category, result)
        self.assertEqual(result["Cash_Conversion"]["Cash_Conversion_Cycle"], 0)

    # ── Data extraction tests (require DB) ───────────────────────────────────

    def _get_company(self):
        companies = frappe.get_all("Company", pluck="name", limit=1)
        return companies[0] if companies else "_Test Company"

    def test_financial_snapshot_returns_required_keys(self):
        from gebeyaerp.services.pulsecheck import get_financial_snapshot

        company = self._get_company()
        data = get_financial_snapshot(company, "2099-01-01", "2099-01-31")

        required = {
            "Revenue", "COGS", "Gross_Profit", "operating_expenses",
            "EBIT", "EBITDA", "Net_Income", "cash_equivalents",
            "accounts_receivable", "inventory", "accounts_payable",
            "shareholders_equity",
        }
        for key in required:
            self.assertIn(key, data, f"Missing key in financial snapshot: {key}")

    def test_financial_snapshot_all_numeric_on_empty_data(self):
        from gebeyaerp.services.pulsecheck import get_financial_snapshot

        company = self._get_company()
        data = get_financial_snapshot(company, "2099-01-01", "2099-01-31")

        for key, val in data.items():
            self.assertIsInstance(
                val, (int, float),
                f"Non-numeric value for key '{key}': {val!r}",
            )

    def test_financial_kpis_from_empty_snapshot(self):
        from gebeyaerp.services.pulsecheck import get_financial_snapshot

        company = self._get_company()
        data = get_financial_snapshot(company, "2099-01-01", "2099-01-31")
        kpis = calc_financial_kpis(data)

        self.assertIsInstance(kpis, dict)
        self.assertIn("Liquidity", kpis)
