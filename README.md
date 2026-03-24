# Hardware Shop Management System | پارڈویٹر دکان انتظام نظام

Desktop application for managing hardware shop inventory, customers, billing, transactions, and reports. Built with Python/Tkinter. Bilingual (English/Urdu).

## ✨ Features
- **Inventory**: Add/Edit/Delete items, update stock, price history tracking, search/filter by category.
- **Customers**: Add/Edit/Delete customer records (name, contact, address).
- **Billing**: Create bills with cart (stock validation), walk-in/new customers, save transactions.
- **Transactions**: View sales history, filter by customer.
- **Reports**: Low stock alerts, high-value items, total inventory value/sales KPIs.
- **Exports**: CSV/JSON inventory backups.
- **Data**: JSON-based (shop_data.json), sample data included.
- **UI**: Modern theme, responsive tables, modals.

## 📱 Screenshots
<img width="1219" height="332" alt="Screenshot 2026-03-24 205503" src="https://github.com/user-attachments/assets/79aaafdb-ff0e-433a-8c37-3c0ef15d8235" />
<img width="1219" height="289" alt="Screenshot 2026-03-24 205448" src="https://github.com/user-attachments/assets/1217974e-4d93-408d-b7ab-5f233ef77ad4" />
<img width="1224" height="280" alt="Screenshot 2026-03-24 205435" src="https://github.com/user-attachments/assets/5ad6c03a-6447-4193-b5ba-eafc57016b6c" />
<img width="1208" height="325" alt="Screenshot 2026-03-24 205416" src="https://github.com/user-attachments/assets/8bfd3bd7-bcfc-4373-9c0b-6b847accdd65" />
<img width="1185" height="404" alt="Screenshot 2026-03-24 205401" src="https://github.com/user-attachments/assets/2d7a723d-4600-4ff3-aad6-c856f8b7d98a" />
<img width="1165" height="580" alt="Screenshot 2026-03-24 205342" src="https://github.com/user-attachments/assets/44a20a34-1b8f-44fc-9c19-d365e56ae4cb" />
<img width="1198" height="731" alt="Screenshot 2026-03-24 205326" src="https://github.com/user-attachments/assets/99ef111c-124e-4060-a20d-f827344a2285" />
<img width="1217" height="854" alt="Screenshot 2026-03-24 044551" src="https://github.com/user-attachments/assets/6775d3a2-2eb7-40da-9a2d-fbd2f4822fea" />


## 🚀 Quick Start

### Prerequisites
- Python 3.8+

### Installation
```bash
pip install -r requirements.txt
```

### Run
**Windows:**
- Double-click `run.bat`
- Or: `python main.py`

**Linux/macOS:**
```bash
python main.py
```

Sample data loads automatically. Data saved to `shop_data.json`.

## 📂 Project Structure
```
.
├── main.py          # Core app
├── requirements.txt # Dependencies
├── shop_data.json   # Data (gitignored)
├── run.bat          # Windows launcher
├── README.md
└── .gitignore
```

## 🔧 Usage
1. **Inventory Tab**: Manage items (add, edit, stock/price updates).
2. **Customers**: Add customer details.
3. **Billing**: Select customer/items/Qty → Save bill (updates stock).
4. **Transactions/Reports**: View analytics.

**Hotkeys**: Double-click to edit rows.

## 🛠 Development
- Theme constants in `main.py` (C dict).
- Data model extensible (add fields).
- Future: PDF bills, SQLite migration.

## 🤝 Contributing
Fork, PR welcome!

## 📄 License
MIT
