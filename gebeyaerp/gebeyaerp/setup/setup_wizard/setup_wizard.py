"""Gebeya ERP Setup Wizard.

Provides a simplified onboarding flow for shop owners.
Our stages are appended after ERPNext's own wizard stages (Company, etc.).
`setup_complete` is called after ALL stages finish, so the Company created
by ERPNext's wizard is already in the database when we run.

Stages delivered by this module:
1. Your Shop    — shop_type, owner_name, owner_phone, location
2. Tax Setup    — tax_type, vat_tin
3. Starter Products — up to 5 items (name, price, opening stock)
4. PulseCheck AI    — optional Claude API key
"""

import re

import frappe
from frappe import _


# ─── Stage definitions ────────────────────────────────────────────────────────

def get_setup_stages(args=None):
    """Return Gebeya ERP's wizard stages.

    Called by Frappe via hooks.setup_wizard_stages.
    Returns an empty list if Shop Settings already has setup_complete = 1.
    """
    if frappe.db.get_single_value("Shop Settings", "setup_complete"):
        return []

    return [
        {
            "name": "gebeya_shop",
            "icon": "fa fa-store",
            "title": _("Your Shop"),
            "fields": _shop_fields(),
        },
        {
            "name": "gebeya_tax",
            "icon": "fa fa-file-invoice",
            "title": _("Tax Setup"),
            "fields": _tax_fields(),
        },
        {
            "name": "gebeya_products",
            "icon": "fa fa-box-open",
            "title": _("Starter Products"),
            "fields": _product_fields(),
        },
        {
            "name": "gebeya_ai",
            "icon": "fa fa-magic",
            "title": _("PulseCheck AI"),
            "fields": _ai_fields(),
        },
    ]


def _shop_fields():
    return [
        {
            "fieldname": "shop_name",
            "fieldtype": "Data",
            "label": _("Shop Name"),
            "placeholder": _("e.g., Abebe's Electronics"),
            "description": _(
                "Leave blank to use your company name."
            ),
        },
        {
            "fieldname": "shop_type",
            "fieldtype": "Select",
            "label": _("Type of Shop"),
            "options": "\nGrocery\nElectronics\nClothing\nHardware\nPharmacy\nRestaurant\nGeneral",
            "reqd": 1,
        },
        {
            "fieldname": "owner_name",
            "fieldtype": "Data",
            "label": _("Owner / Manager Name"),
        },
        {
            "fieldname": "owner_phone",
            "fieldtype": "Data",
            "label": _("Phone Number"),
            "placeholder": "+251 9xx xxx xxx",
        },
        {
            "fieldname": "location",
            "fieldtype": "Data",
            "label": _("Location"),
            "placeholder": _("City, Kebele, or Area"),
        },
    ]


def _tax_fields():
    return [
        {
            "fieldname": "tax_type",
            "fieldtype": "Select",
            "label": _("Tax Type"),
            "options": "\nVAT\nTOT\nNone",
            "reqd": 1,
            "description": _(
                "VAT (15%) applies to businesses with annual turnover above 1,000,000 ETB. "
                "TOT (Turnover Tax, 2%) applies to smaller businesses. "
                "Select None if not registered for tax."
            ),
        },
        {
            "fieldname": "vat_tin",
            "fieldtype": "Data",
            "label": _("TIN / VAT Registration Number"),
            "description": _("Your Tax Identification Number issued by ERCA. Required for VAT-registered shops."),
        },
    ]


def _product_fields():
    fields = [
        {
            "fieldname": "products_intro",
            "fieldtype": "HTML",
            "options": (
                "<p style='color:#6b7280;margin:0 0 20px;'>"
                "Add up to 5 products to get started. "
                "Leave all fields blank to skip — you can add products later from the Items list."
                "</p>"
            ),
        },
    ]

    for i in range(1, 6):
        fields.append({
            "fieldname": f"item_{i}_name",
            "fieldtype": "Data",
            "label": _("Product {0}").format(i),
            "placeholder": _("Product name") if i == 1 else "",
        })
        fields.append({
            "fieldname": f"item_{i}_price",
            "fieldtype": "Float",
            "label": _("Selling Price (ETB)"),
            "default": 0,
        })
        fields.append({
            "fieldname": f"item_{i}_qty",
            "fieldtype": "Int",
            "label": _("Opening Stock (units)"),
            "default": 0,
        })

    return fields


def _ai_fields():
    return [
        {
            "fieldname": "ai_intro",
            "fieldtype": "HTML",
            "options": (
                "<div style='margin-bottom:24px;'>"
                "<p><strong>PulseCheck AI</strong> gives you board-level business analysis powered by Claude.</p>"
                "<p style='color:#6b7280;margin-top:8px;'>"
                "It reads your sales, customer, and inventory data and delivers advice from four "
                "expert perspectives: CFO, CMO, COO, and Business Consultant."
                "</p>"
                "<p style='color:#6b7280;margin-top:8px;'>"
                "You can add your API key now or skip and configure it later in "
                "<strong>Shop Settings</strong>."
                "</p>"
                "</div>"
            ),
        },
        {
            "fieldname": "claude_api_key",
            "fieldtype": "Password",
            "label": _("Claude API Key"),
            "placeholder": "sk-ant-...",
            "description": _("Get your free key at console.anthropic.com"),
        },
    ]


# ─── Completion handler ───────────────────────────────────────────────────────

def setup_complete(args=None):
    """Called by Frappe after all wizard stages are submitted.

    At this point ERPNext's own setup_complete has already run, so:
    - A Company record exists (created by ERPNext's wizard)
    - Chart of Accounts is in place
    - Standard UOMs, Customer Groups, and Territories exist

    We: create tax templates, save Shop Settings, ensure Walk-in Customer,
    and create any starter items the user entered.
    """
    if not args:
        return

    try:
        company, company_abbr = _get_company()
        tax_template = _create_tax_template(company, company_abbr, args.get("tax_type"))
        _setup_shop_settings(company, args, tax_template)
        _ensure_walk_in_customer()
        _create_starter_items(company, args)
    except Exception:
        # Log but don't let wizard completion fail.
        # Shop Settings will already have setup_complete=1 if _setup_shop_settings ran.
        frappe.log_error(frappe.get_traceback(), "Gebeya ERP setup_complete error")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_company():
    """Return (company_name, abbr) for the first company in the system.

    If ERPNext's wizard created a company, we use it.
    If somehow no company exists (edge case), raise so the caller can log it.
    """
    rows = frappe.get_all(
        "Company",
        fields=["name", "abbr"],
        limit=1,
        order_by="creation asc",
    )
    if rows:
        return rows[0].name, rows[0].abbr

    frappe.throw(_("No company found. Please complete the Company setup step first."))


def _create_tax_template(company, company_abbr, tax_type):
    """Create a Sales Taxes and Charges Template for VAT or TOT.

    Returns the template title (str) or None if tax_type is None/blank.
    """
    if not tax_type or tax_type == "None":
        return None

    if tax_type == "VAT":
        title = f"Ethiopian VAT 15% - {company_abbr}"
        rate = 15
        charge_description = "VAT @ 15%"
    else:  # TOT
        title = f"Ethiopian TOT 2% - {company_abbr}"
        rate = 2
        charge_description = "TOT (Turnover Tax) @ 2%"

    if frappe.db.exists("Sales Taxes and Charges Template", title):
        return title

    account_head = _find_tax_account(company, company_abbr)
    if not account_head:
        # Cannot create template without a valid tax account; user configures later.
        return None

    frappe.get_doc({
        "doctype": "Sales Taxes and Charges Template",
        "title": title,
        "company": company,
        "taxes": [
            {
                "charge_type": "On Net Total",
                "account_head": account_head,
                "rate": rate,
                "description": charge_description,
            }
        ],
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return title


def _find_tax_account(company, company_abbr):
    """Find an appropriate Output Tax account in the company's chart of accounts.

    Tries several common account names in order, then falls back to any
    Tax-type account in the company.
    """
    candidates = [
        f"Output Tax - {company_abbr}",
        f"VAT - {company_abbr}",
        f"Tax Payable - {company_abbr}",
        f"Sales Tax - {company_abbr}",
        f"Creditors - {company_abbr}",
    ]
    for name in candidates:
        if frappe.db.exists("Account", name):
            return name

    # Fallback: any non-group Tax account belonging to this company
    result = frappe.get_all(
        "Account",
        filters={"company": company, "account_type": "Tax", "is_group": 0},
        fields=["name"],
        limit=1,
    )
    return result[0].name if result else None


def _setup_shop_settings(company, args, default_tax_template):
    """Populate and save the Shop Settings singleton."""
    settings = frappe.get_single("Shop Settings")

    settings.shop_name = (args.get("shop_name") or "").strip() or company
    settings.shop_type = args.get("shop_type") or "General"
    settings.owner_name = (args.get("owner_name") or "").strip()
    settings.owner_phone = (args.get("owner_phone") or "").strip()
    settings.location = (args.get("location") or "").strip()
    settings.company = company
    settings.currency = "ETB"
    settings.fiscal_year_start = "July (Ethiopian)"
    settings.tax_type = args.get("tax_type") or "None"
    settings.vat_tin = (args.get("vat_tin") or "").strip()
    settings.setup_complete = 1

    if args.get("claude_api_key"):
        settings.claude_api_key = args.get("claude_api_key")

    settings.save(ignore_permissions=True)
    frappe.db.commit()


def _ensure_walk_in_customer():
    """Create Walk-in Customer if it doesn't already exist.

    This is also imported as a fixture, but may not have loaded yet
    (fixture import needs the Customer Group and Territory to exist first).
    """
    if frappe.db.exists("Customer", "Walk-in Customer"):
        return

    # Ensure Customer Group exists
    if not frappe.db.exists("Customer Group", "Individual"):
        root = frappe.db.get_value(
            "Customer Group", {"is_group": 1, "parent_customer_group": ""}, "name"
        ) or "All Customer Groups"
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "Individual",
            "parent_customer_group": root,
            "is_group": 0,
        }).insert(ignore_permissions=True)

    # Ensure Territory exists
    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 1,
        }).insert(ignore_permissions=True)

    frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "Walk-in Customer",
        "customer_type": "Individual",
        "customer_group": "Individual",
        "territory": "All Territories",
    }).insert(ignore_permissions=True)

    frappe.db.commit()


def _create_starter_items(company, args):
    """Create up to 5 Items from the Starter Products wizard step.

    Each item gets:
    - An Item record with retail_category mapped from shop_type
    - An Item Price in the Standard Selling price list (if price > 0)
    - An opening stock Stock Entry (if qty > 0 and a Stores warehouse exists)
    """
    warehouse = _get_stores_warehouse(company)
    price_list = (
        frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name")
        or "Standard Selling"
    )
    item_group = (
        "Products"
        if frappe.db.exists("Item Group", "Products")
        else frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ""}, "name")
        or "All Item Groups"
    )
    retail_category = _map_retail_category(args.get("shop_type") or "")

    for i in range(1, 6):
        item_name = (args.get(f"item_{i}_name") or "").strip()
        if not item_name:
            continue

        price = frappe.utils.flt(args.get(f"item_{i}_price") or 0)
        qty = frappe.utils.cint(args.get(f"item_{i}_qty") or 0)

        try:
            item = frappe.get_doc({
                "doctype": "Item",
                "item_name": item_name,
                "item_group": item_group,
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "custom_retail_category": retail_category,
            })
            item.insert(ignore_permissions=True, ignore_if_duplicate=True)

            if price > 0:
                _create_item_price(item.name, price_list, price)

            if qty > 0 and warehouse:
                _create_opening_stock(item.name, qty, warehouse, company)

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Gebeya ERP: failed to create starter item '{item_name}'",
            )

    frappe.db.commit()


def _get_stores_warehouse(company):
    """Return the name of the Stores warehouse for the company, or None."""
    result = frappe.get_all(
        "Warehouse",
        filters={"company": company, "is_group": 0, "disabled": 0},
        or_filters=[
            ["warehouse_name", "like", "Stores%"],
            ["warehouse_name", "like", "Main%"],
        ],
        fields=["name"],
        limit=1,
    )
    return result[0].name if result else None


def _create_item_price(item_code, price_list, rate):
    """Insert an Item Price record."""
    frappe.get_doc({
        "doctype": "Item Price",
        "item_code": item_code,
        "price_list": price_list,
        "selling": 1,
        "price_list_rate": rate,
        "currency": "ETB",
    }).insert(ignore_permissions=True, ignore_if_duplicate=True)


def _create_opening_stock(item_code, qty, warehouse, company):
    """Submit a Material Receipt Stock Entry for opening stock."""
    se = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt",
        "company": company,
        "items": [
            {
                "item_code": item_code,
                "qty": qty,
                "t_warehouse": warehouse,
                "basic_rate": 0,
            }
        ],
    })
    se.insert(ignore_permissions=True)
    se.submit()


def _map_retail_category(shop_type):
    """Map wizard shop_type to the custom_retail_category Select options."""
    mapping = {
        "Grocery": "Food",
        "Electronics": "Electronics",
        "Clothing": "Clothing",
        "Hardware": "Household",
        "Pharmacy": "Medicine",
        "Restaurant": "Food",
        "General": "Other",
    }
    return mapping.get(shop_type, "Other")


def _make_abbr(name):
    """Generate a short company abbreviation (max 4 uppercase letters)."""
    words = re.split(r"[^a-zA-Z]+", name)
    abbr = "".join(w[0].upper() for w in words if w)[:4]
    if not abbr:
        abbr = re.sub(r"[^A-Za-z]", "", name)[:4].upper()
    return abbr or "SHOP"
