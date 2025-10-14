from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.getenv("MCP_DATA_DIR", "/tmp"), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP(name="Expense Tracker")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (datetime('now')),
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)

init_db()

@mcp.tool
def add_expense(date, amount, category: str, subcategory: str = "", notes: str = "") -> str:
    '''Add an expense entry to the database.'''
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO expenses (date, amount, category, subcategory, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (date, amount, category, subcategory, notes))
        return f"✅ Added expense: {amount} to {category}"
    except Exception as e:
        return f"❌ Failed to add expense: {e}"

@mcp.tool
def list_expenses(startdate: str = None, enddate: str = None, category: str = None, limit: int = 10) -> list[dict]:
    '''List expenses filtered by optional parameters.'''
    with get_connection() as conn:
        sql = """
            SELECT id, date, amount, category, subcategory, notes
            FROM expenses
        """
        conditions, params = [], []
        if startdate:
            conditions.append("date >= ?"); params.append(startdate)
        if enddate:
            conditions.append("date <= ?"); params.append(enddate)
        if category:
            conditions.append("category = ?"); params.append(category)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        cursor = conn.execute(sql, tuple(params))
        rows = cursor.fetchall()
        cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in rows]

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    try:
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "[]"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
