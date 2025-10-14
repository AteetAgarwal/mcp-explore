#Create ExpenseTracker MCP server using sqlite
from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), 'categories.json')

mcp = FastMCP(name="Expense Tracker")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT CURRENT_DATE,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)
        
init_db()

@mcp.tool
def add_expense(date, amount, category: str, subcategory: str="", notes: str="") -> str:
    '''Add an expense entry to the database.'''
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO expenses (date, amount, category, subcategory, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (date, amount, category, subcategory, notes))
    return f"Added expense: {amount} to {category}"

@mcp.tool
def list_expenses(startdate: str = None, enddate: str = None, category: str = None, limit: int = 10) -> list[dict]:
    '''List expenses optionally filtered by startdate, enddate and (optional) category, limited to `limit` most recent.'''
    with sqlite3.connect(DB_PATH) as conn:
        sql = """
            SELECT id, date, amount, category, subcategory, notes
            FROM expenses
        """
        conditions = []
        params = []
        if startdate:
            conditions.append("date >= ?")
            params.append(startdate)
        if enddate:
            conditions.append("date <= ?")
            params.append(enddate)
        if category:
            conditions.append("category = ?")
            params.append(category)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        cursor = conn.execute(sql, tuple(params))
        rows = cursor.fetchall()
        cols = [column[0] for column in cursor.description]
    return [dict(zip(cols, row)) for row in rows]

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting the server
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()