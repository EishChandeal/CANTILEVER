import sqlite3

def initialize_db(conn: sqlite3.Connection):
    """Initializes SQLite database tables and default initial seed data."""
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            color TEXT DEFAULT '#3b82f6',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
    """)

    # 2. Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
    """)

    # 3. Budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            year INTEGER NOT NULL,
            limit_amount REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(category_id, month, year),
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );
    """)

    # 4. Savings Goals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0.0,
            deadline TEXT,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed')),
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
    """)

    # 5. Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    # Seed Default Categories if categories table is empty
    cursor.execute("SELECT COUNT(*) FROM categories;")
    if cursor.fetchone()[0] == 0:
        default_categories = [
            # Income
            ("Salary", "income", "#22c55e"),
            ("Freelance", "income", "#10b981"),
            ("Investment", "income", "#06b6d4"),
            ("Other Income", "income", "#64748b"),
            # Expenses
            ("Food", "expense", "#ef4444"),
            ("Transport", "expense", "#f97316"),
            ("Rent", "expense", "#eab308"),
            ("Entertainment", "expense", "#a855f7"),
            ("Healthcare", "expense", "#ec4899"),
            ("Shopping", "expense", "#3b82f6"),
            ("Utilities", "expense", "#14b8a6"),
            ("Education", "expense", "#8b5cf6"),
            ("Other", "expense", "#64748b")
        ]
        cursor.executemany(
            "INSERT INTO categories (name, type, color) VALUES (?, ?, ?);",
            default_categories
        )

    # Seed Default Settings if settings table is empty
    default_settings = [
        ("currency_symbol", "₹"),
        ("currency_code", "INR"),
        ("theme", "dark")
    ]
    for key, value in default_settings:
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);",
            (key, value)
        )

    conn.commit()
