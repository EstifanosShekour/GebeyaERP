import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestDailySummary(FrappeTestCase):
    """Integration tests for the daily summary service.

    Uses a future date (2099-12-31) so no real invoices exist, making
    these tests safe to run on any site regardless of existing data.
    """

    FUTURE_DATE = "2099-12-31"

    def _get_company(self):
        """Return any company on the site, or create a test one."""
        companies = frappe.get_all("Company", pluck="name", limit=1)
        if companies:
            return companies[0]
        doc = frappe.get_doc({
            "doctype": "Company",
            "company_name": "_Test Gebeya Company",
            "abbr": "TGC",
            "default_currency": "ETB",
            "country": "Ethiopia",
        })
        doc.insert(ignore_permissions=True)
        return doc.name

    def _delete_summary(self, date, company):
        """Clean up any Daily Summary created during a test."""
        name = frappe.db.get_value(
            "Daily Summary",
            {"summary_date": date, "company": company},
            "name",
        )
        if name:
            frappe.delete_doc("Daily Summary", name, ignore_permissions=True, force=True)
            frappe.db.commit()

    def test_no_invoices_no_record_created(self):
        """_generate_for_company on a date with no invoices should not create a record."""
        from gebeyaerp.services.daily_summary import _generate_for_company

        company = self._get_company()
        self._delete_summary(self.FUTURE_DATE, company)

        _generate_for_company(self.FUTURE_DATE, company)

        exists = frappe.db.exists(
            "Daily Summary",
            {"summary_date": self.FUTURE_DATE, "company": company},
        )
        # No invoices → no record
        self.assertFalse(exists)

    def test_idempotent_when_no_data(self):
        """Calling _generate_for_company twice on a zero-data date is a no-op both times."""
        from gebeyaerp.services.daily_summary import _generate_for_company

        company = self._get_company()
        self._delete_summary(self.FUTURE_DATE, company)

        # First call
        _generate_for_company(self.FUTURE_DATE, company)
        # Second call — must not raise
        try:
            _generate_for_company(self.FUTURE_DATE, company)
        except Exception as exc:
            self.fail(f"Second call raised: {exc}")

        # Still no record
        count = frappe.db.count(
            "Daily Summary",
            {"summary_date": self.FUTURE_DATE, "company": company},
        )
        self.assertEqual(count, 0)
