from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient

mcp=FastMCP.as_proxy(
    ProxyClient("https://ateet-blush-marten.fastmcp.app/mcp"), 
    name="Ateet's Proxy MCP")


if __name__ == "__main__":
    mcp.run()
