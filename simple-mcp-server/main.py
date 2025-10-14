from fastmcp import FastMCP
import random
import json

mcp=FastMCP("Simple MCP Server", "1.0.0")

#Tool: Add two numbers
@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers and return the result.
    :param a: First number
    :param b: Second number
    :return: Sum of a and b
    """
    return a + b

#Tools: Get a random number
@mcp.tool
def get_random_number(min: int=1, max: int=100) -> int:
    """
    Get a random number between min and max.
    :param min: Minimum number
    :param max: Maximum number
    :return: Random number between min and max
    """
    return random.randint(min, max)

#Resource: Server information
@mcp.resource("info://server")
def server_info() -> str:
    """
    Get server information.
    :return: JSON string with server information
    """
    info = {
        "server_name": "Simple MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server with basic tools and resources.",
        "tools": ["add_numbers", "get_random_number"]
    }
    return json.dumps(info, indent=4)

#Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
