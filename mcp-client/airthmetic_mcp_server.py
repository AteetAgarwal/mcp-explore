"""
Simple arithmetic operations MCP server.
Provides basic math tools: add, subtract, multiply, divide, power, sqrt.
"""

from fastmcp import FastMCP
import math

mcp = FastMCP("Arithmetic")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> dict:
    """Divide a by b. Returns error if b is zero."""
    if b == 0:
        return {"error": "Division by zero", "result": None}
    return {"result": a / b}


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent


@mcp.tool()
def sqrt(value: float) -> dict:
    """Calculate square root of a value. Returns error if value is negative."""
    if value < 0:
        return {"error": "Cannot calculate square root of negative number", "result": None}
    return {"result": math.sqrt(value)}


@mcp.tool()
def modulo(a: float, b: float) -> dict:
    """Calculate remainder of a divided by b."""
    if b == 0:
        return {"error": "Division by zero", "result": None}
    return {"result": a % b}


if __name__ == "__main__":
    mcp.run()
