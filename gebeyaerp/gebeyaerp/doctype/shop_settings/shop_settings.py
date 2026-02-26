import frappe
from frappe.model.document import Document


class ShopSettings(Document):
    def validate(self):
        if self.tax_type == "VAT" and not self.vat_tin:
            frappe.msgprint(
                "VAT registration number (TIN) is recommended for VAT-registered shops.",
                indicator="orange",
                alert=True,
            )
