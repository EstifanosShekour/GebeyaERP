import frappe


def before_install():
    """Validate environment before installing Gebeya ERP."""
    # Check Frappe version
    frappe_version = int(frappe.__version__.split(".")[0])
    if frappe_version < 15:
        frappe.throw(
            "Gebeya ERP requires Frappe version 15 or higher. "
            f"You are running Frappe v{frappe.__version__}."
        )

    # Check ERPNext is installed
    installed_apps = frappe.get_installed_apps()
    if "erpnext" not in installed_apps:
        frappe.throw(
            "Gebeya ERP requires ERPNext to be installed. "
            "Please install ERPNext first: bench get-app erpnext --branch version-15"
        )

    # Check ERPNext version
    try:
        import erpnext

        erpnext_version = int(erpnext.__version__.split(".")[0])
        if erpnext_version < 15:
            frappe.throw(
                "Gebeya ERP requires ERPNext version 15 or higher. "
                f"You are running ERPNext v{erpnext.__version__}."
            )
    except ImportError:
        frappe.throw("ERPNext is not installed.")


def after_install():
    """Post-installation setup for Gebeya ERP."""
    # Enable row-wise tax rounding (required for Ethiopian invoices).
    # Wrapped in try/except — field may not exist in all ERPNext v15 minor versions.
    try:
        frappe.db.set_single_value("Accounts Settings", "round_row_wise_tax", 1)
        frappe.db.commit()
    except Exception:
        pass

    print("Gebeya ERP installed successfully!")
