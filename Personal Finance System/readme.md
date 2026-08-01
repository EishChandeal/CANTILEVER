# 💰 Personal Finance System

A modern, offline-first desktop application for managing personal income, expenses, monthly budgets, and long-term savings goals.

![Dashboard](assets/screenshot.png)

## Features

- 📋 **Income & Expense Tracking**: Log transactions, filter by date/type/category, and search descriptions in real-time.
- 🎯 **Budget Manager**: Set monthly limits per category with progress bars and automated overspending alerts (>80%).
- 💰 **Savings Goals**: Track targeted savings progress, record deposits, and track completion statuses.
- 📊 **Visual Reports**: Embedded interactive Matplotlib charts for multi-month trends, category expense breakdowns (donut chart), and monthly income vs. expense comparisons.
- 📥 **Data Export**: Export your complete transaction history to CSV format anytime.
- ⚙️ **Settings & Customization**: Configure local currency symbols (₹, $, €, £), appearance themes (Dark/Light), and custom income/expense categories.
- 🔒 **Privacy First**: 100% offline data stored safely in a local SQLite database (`data/finance.db`).

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **GUI Framework** | CustomTkinter |
| **Database** | SQLite (with DAO pattern) |
| **Visualizations** | Matplotlib |
| **Testing** | Pytest (In-Memory SQLite) |
| **Packaging** | PyInstaller |

## Getting Started

### Prerequisites
- Python 3.10 or higher installed.

### Installation & Launch

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd "Personal Finance System"
   ```

2. Setup virtual environment & dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   python src/main.py
   ```

> **Windows Users**: You can also double-click `run.bat` in the root folder to automatically set up the virtual environment and launch the app!

## Project Structure

```text
Personal Finance System/
├── assets/                  # App icons and graphics
├── data/                    # SQLite database storage (data/finance.db)
├── src/                     # Application source code
│   ├── database/            # Database schema & Data Access Objects (DAOs)
│   │   ├── dao/             # Transaction, Category, Budget, and Savings DAOs
│   │   ├── db_manager.py    # Database connection manager
│   │   └── schema.py        # DDL tables & default seed data
│   ├── gui/                 # CustomTkinter interface
│   │   ├── components/      # Sidebar & Header bar components
│   │   ├── pages/           # Dashboard, Transactions, Budget, Savings, Reports, Settings
│   │   └── app.py           # Main window shell & page router
│   ├── services/            # Core business logic layer
│   │   ├── finance_service.py
│   │   ├── budget_service.py
│   │   ├── savings_service.py
│   │   └── settings_service.py
│   ├── utils/               # Indian currency & date formatting helpers
│   ├── config.py            # Global app constants & UI palette definitions
│   └── main.py              # Application entry point
├── tests/                   # In-memory SQLite unit test suite
├── .gitignore               # Git exclusion rules
├── requirements.txt         # Project dependencies
├── run.bat                  # One-click Windows runner script
└── README.md                # Project documentation
```

## Running Tests

Run the full automated test suite using Pytest:

```bash
python -m pytest tests/ -v
```

## License

This project is licensed under the MIT License.
