# Gebeya ERP — Manual QA Checklist

Use this checklist after every release to verify that the full workflow is functioning correctly.
Tick each item on a **fresh site** (bench new-site) unless noted otherwise.

---

## 1. Fresh Install

- [ ] `bench get-app https://github.com/haroncomputer/gebeyaerp` completes without errors
- [ ] `bench --site <site> install-app gebeyaerp` completes without errors
- [ ] `bench --site <site> migrate` applies all fixtures (Custom Fields, Property Setters, Walk-in Customer, Gebeya Receipt)
- [ ] `bench restart` and site loads at `http://localhost`
- [ ] Login as Administrator succeeds

---

## 2. Setup Wizard

- [ ] First login redirects to the Gebeya ERP setup wizard (not the default ERPNext wizard)
- [ ] All 4 stages appear: Shop Profile, Tax Setup, Opening Stock, Finish
- [ ] Completing all stages creates a **Shop Settings** document with `setup_complete = 1`
- [ ] **Walk-in Customer** exists in the Customer list after wizard
- [ ] Tax template is created matching the selected tax type (VAT 15% or TOT 2%)
- [ ] After wizard, landing page is **Gebeya Dashboard** (not desk)

---

## 3. Daily Selling Workflow

- [ ] Click **+ New Sale** → opens a new Sales Invoice
- [ ] Customer defaults to **Walk-in Customer**
- [ ] Tax template auto-populates from Shop Settings
- [ ] Add an item (with stock) → rate and amount populate correctly
- [ ] Submit the invoice → no errors
- [ ] **Print Receipt** button appears in the Print menu after submission
- [ ] Clicking Print Receipt opens the Gebeya Receipt print format (thermal-style layout)
- [ ] If an item's stock drops at or below its reorder point → orange low stock alert appears after submit

---

## 4. Stock Management

- [ ] Open a new **Purchase Receipt** → company pre-fills from Shop Settings
- [ ] Add supplier and items → submit successfully
- [ ] Open **Stock > Bin** (or Item list) → stock quantities have increased
- [ ] Dashboard → **Low Stock Items** section disappears if no items are below reorder point
- [ ] Set `custom_reorder_point` on an item, sell below that threshold → low stock alert appears

---

## 5. Customer Management

- [ ] Open a Customer record → **Purchase History** button is visible
- [ ] Click Purchase History → navigates to Sales Invoice list filtered by this customer
- [ ] Click **Customer Summary** button → Gebeya Customer Summary report renders
- [ ] Credit intro bar shows outstanding amount in orange when customer has unpaid invoices
- [ ] Credit bar shows green "No outstanding credit" when fully paid
- [ ] Open Customer list → **Customer Summary** button in toolbar → report opens

---

## 6. Employee & Attendance

- [ ] Create a new Employee → status defaults to Active
- [ ] Open Employee form → **Attendance** button navigates to filtered Attendance list
- [ ] Click **Mark Today's Attendance** → dialog appears with Status and Date fields
- [ ] Submit from dialog → Attendance record created and submitted; success message shown
- [ ] Open Attendance list → **Mark Bulk Attendance** toolbar button is visible
- [ ] Click Mark Bulk Attendance → dialog with date and status
- [ ] Submit → shows "X attendance records created" message
- [ ] On Attendance form: late_entry, early_exit, shift fields are hidden (simplified)

---

## 7. Dashboard

- [ ] Navigate to **Gebeya Dashboard**
- [ ] All 7 metric cards display values (not "…" loading state) after a brief pause
- [ ] **Today's Sales** shows correct ETB total for today
- [ ] **This Month** shows correct ETB total for the current month
- [ ] **Invoices Today** count matches actual submitted invoices for today
- [ ] **Low Stock Items** count is correct; card turns amber if count > 0
- [ ] **Outstanding Credit** matches total outstanding Sales Invoice amounts
- [ ] **Active Employees** count matches active employees
- [ ] **Top Item Today** shows the best-selling item name for today (or "—" if none)
- [ ] Clicking **Low Stock Items** card → low stock table appears/scrolls into view
- [ ] Low stock table shows: Item, Warehouse, Stock qty (amber), Reorder At
- [ ] Clicking each metric card navigates to the relevant list/report
- [ ] **Refresh** link reloads all 7 metrics
- [ ] Shop name appears in dashboard header (e.g. "My Shop — Dashboard")
- [ ] Date shows in localised format (e.g. "25-02-2026")
- [ ] Action buttons (+ New Sale, Products, Customers, Stock In, PulseCheck AI) all navigate correctly

---

## 8. PulseCheck AI

- [ ] Navigate to **PulseCheck AI** page
- [ ] Company dropdown pre-selects the user's default company
- [ ] From Date and To Date default to first day of current month → today
- [ ] Click **Run Analysis** with a valid Claude API key configured
- [ ] Spinner/loading message appears ("Analysing your business…")
- [ ] After 60–120 seconds, spinner hides and results appear
- [ ] All 6 tabs are present: Board Report, CFO, CMO, COO, KPIs, Market Intel
- [ ] Board Report tab shows formatted markdown content
- [ ] CFO / CMO / COO tabs each show their specialist reports
- [ ] KPIs tab shows Financial, Marketing, Operations metric grids
- [ ] Market Intel tab shows industry trends, competitor intel, market conditions
- [ ] Report metadata row shows: report name, company, date range, model, duration
- [ ] Past Reports dropdown lists the completed report
- [ ] Selecting a past report from the dropdown renders it immediately
- [ ] PulseCheck Report document is saved in ERPNext with status = Complete

---

## 9. Edge Cases — Zero Data Site

These tests should pass on a fresh site with no invoices.

- [ ] **Dashboard with no invoices** → onboarding banner "Welcome to Gebeya ERP!" appears; no JavaScript errors in console
- [ ] **Dashboard metric cards** show 0 / ETB 0.00 values, not errors
- [ ] **No customers** → Customer Summary report shows empty table, no traceback
- [ ] **No employees** → Mark Bulk Attendance returns "0 attendance records created"
- [ ] **No stock with reorder points** → Low Stock section on dashboard is hidden
- [ ] **PulseCheck on zero-data site** → analysis completes without crashing; all KPIs show 0; no 500 error
- [ ] **PulseCheck with no API key** → clicking Run Analysis shows Frappe error: "Claude API key not configured"

---

*Last updated: February 2026*
