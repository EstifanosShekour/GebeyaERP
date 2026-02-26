# Gebeya ERP — User Guide

*For shop owners, cashiers, and daily operators. No technical background required.*

---

## 1. Getting Started

### Logging In

1. Open your browser and go to your shop's Gebeya ERP address (e.g. `http://myshop.gebeya.et`).
2. Enter your **Username** and **Password**, then click **Login**.
3. The first time you log in, a short setup wizard will guide you through entering your shop name, tax type, and opening stock. This takes about 5 minutes.

### The Dashboard

After logging in you land on the **Gebeya Dashboard**. It shows 7 live numbers for your shop:

| Card | What it shows |
|---|---|
| Today's Sales | Total revenue (ETB) from today's submitted invoices |
| This Month | Total revenue for the current calendar month |
| Invoices Today | Number of sales completed today |
| Low Stock Items | Count of items at or below their reorder point |
| Outstanding Credit | Total unpaid amount owed by credit customers |
| Active Employees | Number of staff currently marked Active |
| Top Item Today | The best-selling item by quantity today |

Click any card to jump to the related list or report. Use the **Refresh** link (top right) to update all numbers at any time.

---

## 2. Making a Sale

1. Click **+ New Sale** on the dashboard (or go to **Selling > Sales Invoice > New**).
2. The **Customer** field is pre-set to *Walk-in Customer* for cash sales. For a named customer, type their name and select from the list.
3. Under **Items**, click **Add Row** and type the item name or barcode. The price fills in automatically.
4. Add more items as needed. The totals update live.
5. Check the **Grand Total** at the bottom.
6. Click **Submit** (blue button) to finalise the sale.

> **Tip:** You can change the quantity or price before submitting. Once submitted, the sale is locked.

---

## 3. Accepting Payment

On the Sales Invoice, use the **Payment Method** field to record how the customer paid:

| Option | When to use |
|---|---|
| Cash | Physical notes and coins |
| Mobile Money | Telebirr, CBEBirr, M-Pesa, etc. |
| Bank Transfer | Direct bank transfer or cheque |
| Credit | Customer pays later (adds to outstanding credit) |

For **Credit** sales, the outstanding amount appears on the customer's record and in the Outstanding Credit card on the dashboard.

---

## 4. Printing a Receipt

After submitting a sale:

1. Look for the **Print** button at the top of the invoice.
2. Click **Print Receipt** from the dropdown.
3. A thermal-style receipt opens in a new tab. Use your browser's print function (Ctrl+P) to print.

> **Tip:** The receipt header shows your shop name, address, and tax registration number from Shop Settings.

---

## 5. Managing Stock

### Adding Products

1. Go to **Stock > Item > New** (or use the **Products** button on the dashboard).
2. Fill in **Item Name**, **Item Code** (optional — auto-generated), and **Unit of Measure** (e.g. Pcs, Kg).
3. Tick **Is Stock Item** if you want to track quantities.
4. Set **Reorder Point** to the quantity at which you want a low-stock alert.
5. Click **Save**.

### Setting Reorder Points

Open any Item → scroll to the **Reorder Point** field → enter the minimum quantity you want to keep in stock. When stock drops to or below this number, the Low Stock Items card on the dashboard turns amber and an alert appears after each sale.

### Receiving Stock (Stock In)

1. Click **Stock In** on the dashboard (or go to **Stock > Purchase Receipt > New**).
2. Select the **Supplier**.
3. Under **Items**, add each product and its received quantity.
4. Click **Submit** to confirm. Stock levels update immediately.

---

## 6. Customers

### Adding a Named Customer

1. Go to the **Customers** list (dashboard button or **Selling > Customer**).
2. Click **New**.
3. Enter **Customer Name**, **Phone**, and any other details.
4. Click **Save**.

### Viewing Purchase History

Open a Customer record → click **Purchase History**. You will see all invoices for this customer with dates, amounts, and payment methods.

### Checking Outstanding Credit

Open a Customer record → a banner at the top shows the total outstanding amount in orange (or green if the account is clear). You can also click **Customer Summary** to see a full report for all customers.

---

## 7. Employees & Attendance

### Adding an Employee

1. Go to **HR > Employee > New**.
2. Enter the employee's name, designation, and join date.
3. Leave **Status** as *Active*.
4. Click **Save**.

### Marking Daily Attendance

**For one employee:**

1. Open the Employee record.
2. Click **Mark Today's Attendance**.
3. Select the **Status** (Present, Absent, On Leave, Half Day).
4. Click **Submit**.

**For all staff at once:**

1. Open the **Attendance** list.
2. Click **Mark Bulk Attendance** in the toolbar.
3. Choose the date and status.
4. Click **Mark Attendance**. All active employees receive an attendance record.

---

## 8. Understanding the Dashboard

**Today's Sales / This Month** — these are net sales (before tax) from submitted invoices only. Draft invoices are not counted.

**Invoices Today** — the number of separate transactions, not items sold.

**Low Stock Items** — click this card to see which items need restocking. The list shows the current stock qty and the reorder point. Items appear here only when stock is at or below the reorder point.

**Outstanding Credit** — total unpaid balances across all credit customers. Click to open the Customer Summary report and see who owes what.

**Active Employees** — based on the Employee record's Status field.

**Top Item Today** — the item with the highest quantity sold in today's invoices. Shows "—" if no sales today.

---

## 9. PulseCheck AI

PulseCheck analyses your ERPNext data and produces four specialist reports — CFO, CMO, COO, and a Board-level summary — using artificial intelligence.

### Running an Analysis

1. Click **PulseCheck AI** on the dashboard.
2. Select your **Company** and set the **From Date** and **To Date** for the analysis period.
3. Click **Run Analysis**.
4. Wait 60–120 seconds while the system gathers data and generates reports.

### Reading the Reports

Use the tabs at the top of the results panel:

| Tab | Content |
|---|---|
| Board Report | Executive summary and strategic recommendation |
| CFO | Financial health, red flags, 3 CFO directives |
| CMO | Growth engine score, retention health, 3 marketing strategies |
| COO | Operational health, bottlenecks, 30/60/90-day roadmap |
| KPIs | Raw financial, marketing, and operational metrics in a grid |
| Market Intel | Live industry trends and competitor intelligence |

### Past Reports

All completed analyses are saved. Use the **Past Reports** dropdown to revisit any previous report without running a new analysis.

> **Note:** PulseCheck requires a Claude API key to be configured by your administrator.

---

## 10. Shop Settings

Go to **Gebeya > Shop Settings** to update:

| Setting | Description |
|---|---|
| Shop Name | Shown on the dashboard header and receipts |
| Shop Type / Industry | Used by PulseCheck for industry benchmarking |
| Tax Type | VAT (15%) or TOT (2%) — affects all new invoices |
| VAT TIN | Tax registration number, shown on receipts |
| Claude API Key | Required for PulseCheck AI — ask your administrator |

Changes take effect immediately (no restart required).

---

*Gebeya ERP — Built for Ethiopian Retail by Haron Computer PLC*
