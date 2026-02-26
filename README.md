# Gebeya ERP

A simple ERP for Ethiopian retail businesses, built on Frappe + ERPNext.

**Gebeya** (ገበያ) means "market" in Amharic.

## Features

- **Invoicing & Payments** — Quick sales invoices with Ethiopian VAT/TOT compliance
- **Inventory / Stock** — Product tracking, stock levels, low-stock alerts
- **Customer Management** — Customer database, purchase history, credit tracking
- **Employee / HR Basics** — Employee records, attendance, salary tracking
- **PulseCheck AI** — AI-powered business analysis from your ERP data

## Installation

```bash
bench get-app gebeyaerp /path/to/gebeyaerp
bench --site your-site install-app gebeyaerp
bench --site your-site migrate
```

## Requirements

- Frappe >= 15.0.0
- ERPNext >= 15.0.0
- Python >= 3.10

## Configuration

Add your Claude API key for PulseCheck:
```bash
bench --site your-site set-config claude_api_key "sk-ant-..."
```

## License

MIT
