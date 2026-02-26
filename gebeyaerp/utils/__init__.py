"""Shared utility functions for Gebeya ERP."""

import frappe


def get_shop_settings():
    """Get the Shop Settings singleton."""
    try:
        return frappe.get_single("Shop Settings")
    except Exception:
        return None


def get_default_company():
    """Get the default company for the current user."""
    return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
        "Shop Settings", "company"
    )
