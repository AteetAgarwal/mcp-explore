import asyncio
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import ToolMessage

load_dotenv()

SERVERS = {
    "math": {
        "transport":"stdio",
        "command": "uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "airthmetic_mcp_server.py",
        ],
    },
    "expense":{
        "transport": "streamable_http",
        "url": "https://ateet-blush-marten.fastmcp.app/mcp",
    },
}

async def main():
    client = MultiServerMCPClient(SERVERS)
    tools=await client.get_tools()
    named_tools={}
    for tool in tools:
        named_tools[tool.name]=tool
    llm = AzureChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    prompt = "Any expense on this month? Please list them. Also, what is 15% of 2500?"
    response = await llm_with_tools.ainvoke(prompt)
    
    if not getattr(response, "tool_calls", None):
        print(response.content)
        return
    
    tool_messages=[]
    for tc in response.tool_calls:
        selected_tool=tc["name"]
        selected_tool_args=tc["args"]
        selected_tool_id=tc["id"]
        
        tool_result=await named_tools[selected_tool].ainvoke(selected_tool_args)
        tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(tool_result)))
        
    final_response=await llm_with_tools.ainvoke([prompt, response, *tool_messages])
    print(final_response.content)
    
if __name__ == "__main__":
    asyncio.run(main())