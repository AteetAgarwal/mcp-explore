from fastmcp import FastMCP

mcp=FastMCP.as_proxy("https://ateet-blush-marten.fastmcp.app/mcp", name="Ateet's Proxy MCP")


if __name__ == "__main__":
    mcp.run()
