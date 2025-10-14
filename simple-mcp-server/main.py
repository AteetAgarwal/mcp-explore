import os
import json
import asyncio
import aiosqlite
import aiofiles
from fastmcp import FastMCP

DB_PATH = os.path.join(os.getenv("MCP_DATA_DIR", "/tmp"), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP(name="Expense Tracker")


async def get_connection():
    conn = await aiosqlite.connect(DB_PATH)
    await conn.execute("PRAGMA journal_mode=WAL;")
    return conn


async def init_db():
    async with await get_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT (datetime('now')),
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)
        await conn.commit()


@mcp.tool
async def add_expense(date: str, amount: float, category: str, subcategory: str = "", notes: str = "") -> str:
    """Add an expense entry to the database."""
    try:
        async with await get_connection() as conn:
            await conn.execute("""
                INSERT INTO expenses (date, amount, category, subcategory, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (date, amount, category, subcategory, notes))
            await conn.commit()
        return f"✅ Added expense: {amount} to {category}"
    except Exception as e:
        return f"❌ Failed to add expense: {e}"


@mcp.tool
async def list_expenses(startdate: str = None, enddate: str = None, category: str = None, limit: int = 10) -> list[dict]:
    """List expenses filtered by optional parameters."""
    sql = """
        SELECT id, date, amount, category, subcategory, notes
        FROM expenses
    """
    conditions, params = [], []
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

    async with await get_connection() as conn:
        async with conn.execute(sql, tuple(params)) as cursor:
            rows = await cursor.fetchall()
            cols = [column[0] for column in cursor.description]
    return [dict(zip(cols, row)) for row in rows]


@mcp.resource("expense://categories", mime_type="application/json")
async def categories():
    """Return the list of available categories as JSON."""
    try:
        async with aiofiles.open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            content = await f.read()
        return content
    except FileNotFoundError:
        return json.dumps([])


async def main():
    await init_db()
    await mcp.run_async(transport="http", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(main())
