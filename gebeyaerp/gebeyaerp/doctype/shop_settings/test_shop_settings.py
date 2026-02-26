import frappe
from frappe.tests.utils import FrappeTestCase


class TestShopSettings(FrappeTestCase):
    """Tests for ShopSettings.validate().

    validate() only calls frappe.msgprint (a warning) — it never raises.
    All three paths below must complete without an exception.
    """

    def _get_settings(self):
        """Return the singleton Shop Settings doc."""
        return frappe.get_single("Shop Settings")

    def test_vat_without_tin_shows_warning_not_exception(self):
        """VAT type + blank TIN → msgprint only, no exception raised."""
        doc = self._get_settings()
        doc.tax_type = "VAT"
        doc.vat_tin = ""
        # validate() calls frappe.msgprint — must not raise
        try:
            doc.validate()
        except Exception as exc:
            self.fail(f"validate() raised unexpectedly: {exc}")

    def test_vat_with_tin_no_exception(self):
        """VAT type + TIN present → no warning, no exception."""
        doc = self._get_settings()
        doc.tax_type = "VAT"
        doc.vat_tin = "TIN123456"
        try:
            doc.validate()
        except Exception as exc:
            self.fail(f"validate() raised unexpectedly: {exc}")

    def test_no_tax_no_exception(self):
        """Non-VAT tax type → validate() is effectively a no-op."""
        doc = self._get_settings()
        doc.tax_type = "None"
        doc.vat_tin = ""
        try:
            doc.validate()
        except Exception as exc:
            self.fail(f"validate() raised unexpectedly: {exc}")
