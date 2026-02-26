# Gebeya ERP — Admin & Installation Guide

*For IT administrators and developers installing or maintaining Gebeya ERP.*

---

## 1. Requirements

| Component | Minimum version |
|---|---|
| Operating System | Ubuntu 22.04 LTS (recommended) or Debian 12 |
| Python | 3.10+ |
| Node.js | 18+ |
| Frappe Framework | v15 |
| ERPNext | v15 |
| MariaDB | 10.6+ |
| Redis | 6+ |
| bench CLI | latest |

> Gebeya ERP is a Frappe app that **extends ERPNext**. ERPNext must be installed on the same bench before installing Gebeya ERP.

---

## 2. Installation

### Step 1 — Set up a bench (if not already done)

```bash
# Install bench
pip install frappe-bench

# Create a new bench with Frappe v15
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# Create a site
bench new-site your-site.local --install-app frappe

# Get and install ERPNext
bench get-app --branch version-15 erpnext
bench --site your-site.local install-app erpnext
```

### Step 2 — Install Gebeya ERP

```bash
bench get-app https://github.com/haroncomputer/gebeyaerp
bench --site your-site.local install-app gebeyaerp
bench --site your-site.local migrate
bench restart
```

`migrate` applies all fixtures:
- Custom Fields (item reorder point, payment method on sales invoices, etc.)
- Property Setters (field visibility simplifications)
- Walk-in Customer
- Gebeya Receipt print format

### Step 3 — Verify installation

Open the site in a browser. Log in as Administrator. You should be redirected to the **Gebeya ERP Setup Wizard** on first login.

---

## 3. First-Time Setup

1. Log in as **Administrator**.
2. The setup wizard launches automatically (4 stages: Shop Profile, Tax Setup, Opening Stock, Finish).
3. Complete all stages. On finish, Shop Settings is created with `setup_complete = 1` and a tax template is created.
4. The landing page becomes the **Gebeya Dashboard**.

If the wizard does not appear, set `setup_complete = 0` in the Shop Settings document via the database console (see Troubleshooting).

---

## 4. Claude API Key (for PulseCheck AI)

PulseCheck AI requires an Anthropic Claude API key. There are two ways to configure it:

### Option A — Via the UI (recommended for non-technical users)

1. Go to **Gebeya > Shop Settings**.
2. Scroll to the **PulseCheck AI** section.
3. Paste the API key into the **Claude API Key** field.
4. Click **Save**.

The key is stored encrypted in the Frappe database (Password field type).

### Option B — Via site_config.json (recommended for self-hosted / multi-site)

```bash
bench --site your-site.local set-config claude_api_key "sk-ant-api03-..."
# Optionally override the default model:
bench --site your-site.local set-config claude_model "claude-sonnet-4-6"
```

This writes the key to `sites/your-site.local/site_config.json`. The API layer checks `site_config.json` first, then falls back to Shop Settings.

> **Security:** Never commit your API key to version control. The `site_config.json` file is in `.gitignore` by default in bench.

---

## 5. Fixtures

Gebeya ERP ships fixtures that are applied automatically on `bench migrate`. The fixture set is filtered by `module = "Gebeyaerp"` so it only touches Gebeya-owned records.

To re-export fixtures after making changes in the UI:

```bash
bench --site your-site.local export-fixtures --app gebeyaerp
```

This overwrites the JSON files in `gebeyaerp/fixtures/`. Commit the updated files to version control.

Fixture files:
- `gebeyaerp/fixtures/custom_field.json` — custom fields on standard doctypes
- `gebeyaerp/fixtures/property_setter.json` — field visibility settings
- `gebeyaerp/fixtures/customer.json` — Walk-in Customer record
- `gebeyaerp/fixtures/print_format.json` — Gebeya Receipt thermal print format

---

## 6. Backup

Use the standard bench backup. This covers the full database (all documents, settings, fixtures) and uploaded files.

```bash
bench --site your-site.local backup --with-files
```

Backups are stored in `sites/your-site.local/private/backups/`. Schedule automated backups using cron or the Frappe Scheduler.

---

## 7. Upgrading

```bash
cd frappe-bench
bench get-app gebeyaerp  # pulls latest from the default branch
bench --site your-site.local migrate
bench build --app gebeyaerp
bench restart
```

Always run `migrate` after an upgrade — it applies any new fixtures or schema changes.

---

## 8. Running Tests

### Automated tests (requires a running bench)

```bash
bench --site your-site.local run-tests --app gebeyaerp
```

This runs all `FrappeTestCase` classes found in the app.

### Pure KPI unit tests (no bench required)

```bash
# From the bench root, with the virtualenv active:
python -m pytest apps/gebeyaerp/gebeyaerp/tests/test_pulsecheck_kpis.py -v
```

These tests have no database dependency and run in seconds.

### Syntax check

```bash
py -3 -m py_compile apps/gebeyaerp/gebeyaerp/tests/test_pulsecheck_kpis.py
py -3 -m py_compile apps/gebeyaerp/gebeyaerp/services/pulsecheck_kpis.py
```

---

## 9. Troubleshooting

### "Claude API key not configured"

PulseCheck cannot find the API key.

- **Check Shop Settings** → Gebeya > Shop Settings → Claude API Key field is populated.
- **Check site_config.json**: `bench --site <site> get-config claude_api_key` — should return the key.
- Confirm the key starts with `sk-ant-api03-` and has not been revoked at [console.anthropic.com](https://console.anthropic.com).

---

### PulseCheck Report shows "Error" status

1. Go to **Gebeya > PulseCheck Report**.
2. Open the failed report.
3. Read the **Error Log** field — it contains the full Python traceback.
4. Common causes:
   - API key invalid or quota exceeded → verify key at Anthropic console
   - Network timeout → increase server outbound timeout or check firewall
   - Missing company data → run analysis on a date range with at least some invoice data

---

### Setup wizard not showing on first login

Shop Settings may already have `setup_complete = 1`.

To re-trigger the wizard:

```bash
bench --site your-site.local execute "frappe.db.set_value('Shop Settings', 'Shop Settings', 'setup_complete', 0)"
bench --site your-site.local execute "frappe.db.commit()"
```

Then log out and log back in.

---

### Fixtures not applying after migrate

1. Confirm the fixture files exist: `ls apps/gebeyaerp/gebeyaerp/fixtures/`
2. Check `hooks.py` — the `fixtures` list must reference the correct doctypes.
3. Run `bench --site <site> migrate` and look for fixture output in the log.
4. Verify `module = "Gebeyaerp"` is set on each fixture record (required for the `filters` in `hooks.py`).

---

### Low stock alerts not appearing

- Confirm the item has `custom_reorder_point` set to a value greater than 0.
- Confirm the item is a stock item (`is_stock_item = 1`) and not disabled.
- Check that the `tabBin` table has stock records for the item (submit at least one Purchase Receipt).

---

### Dashboard shows "…" permanently (data not loading)

1. Open the browser developer console (F12) → check for JavaScript errors.
2. Open **Frappe > Error Log** → look for entries from `gebeyaerp.services.dashboard`.
3. Confirm the whitelisted methods are accessible: the user must have at least **Sales User** role.

---

*Gebeya ERP — Built for Ethiopian Retail by Haron Computer PLC*
