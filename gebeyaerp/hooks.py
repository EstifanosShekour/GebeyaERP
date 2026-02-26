app_name = "gebeyaerp"
app_title = "Gebeya ERP"
app_publisher = "Haron Computer PLC"
app_description = "A simple ERP for Ethiopian retail businesses"
app_email = "info@haroncomputer.com"
app_license = "mit"
app_logo_url = "/assets/gebeyaerp/images/logo.png"

# ─── Required Apps ───
required_apps = ["frappe", "erpnext"]

# ─── Module ───
# The module name must match modules.txt
# DocTypes, Pages, Reports are registered under this module

# ─── Assets ───
# app_include_css = ["gebeyaerp.bundle.css"]
# app_include_js = ["gebeyaerp.bundle.js"]

# ─── Website ───
website_context = {
    "favicon": "/assets/gebeyaerp/images/logo.png",
    "splash_image": "/assets/gebeyaerp/images/logo.png",
}

# ─── Home Page ───
home_page = "gebeya-dashboard"

# ─── Setup Wizard ───
setup_wizard_stages = "gebeyaerp.gebeyaerp.setup.setup_wizard.setup_wizard.get_setup_stages"
setup_wizard_complete = "gebeyaerp.gebeyaerp.setup.setup_wizard.setup_wizard.setup_complete"

# ─── Installation Hooks ───
before_install = "gebeyaerp.install.before_install"
after_install = "gebeyaerp.install.after_install"

# ─── Fixtures ───
# Fixtures are loaded on bench migrate
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Gebeyaerp"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Gebeyaerp"]]},
    {"dt": "Customer", "filters": [["name", "=", "Walk-in Customer"]]},
    {"dt": "Print Format", "filters": [["name", "=", "Gebeya Receipt"]]},
]

# ─── DocType JS (Client Scripts) ───
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Item": "public/js/item.js",
    "Purchase Receipt": "public/js/purchase_receipt.js",
    "Customer": "public/js/customer.js",
    "Employee": "public/js/employee.js",
    "Attendance": "public/js/attendance.js",
}

# ─── DocType List JS (List View Client Scripts) ───
doctype_list_js = {
    "Customer": "public/js/customer_list.js",
    "Attendance": "public/js/attendance.js",
}

# ─── Document Events ───
# doc_events = {
#     "Sales Invoice": {
#         "on_submit": "gebeyaerp.gebeyaerp.overrides.sales_invoice.on_submit",
#     },
# }

# ─── Scheduled Tasks ───
scheduler_events = {
    "daily_long": [
        "gebeyaerp.services.daily_summary.generate_daily_summary",
    ],
}

# ─── Whitelisted Methods (called from frontend via frappe.call) ───
# override_whitelisted_methods = {}

# ─── Jinja Methods (available in print formats) ───
# jinja = {
#     "methods": [],
# }
