# MCP Client — Streamlit + LangChain Integration

A Streamlit-based chat application that connects to multiple MCP (Model Context Protocol) servers and orchestrates tool calls through Azure OpenAI's GPT-4o-mini model.

## Purpose

This project demonstrates:
- How to build a Streamlit chat UI that integrates MCP servers
- Using `langchain-mcp-adapters` to connect local and remote MCP servers
- Orchestrating tool execution with LLM decision-making
- Message ordering: assistant messages with tool_calls are hidden; only final answers render

## Architecture

### Components

1. **Streamlit UI** (`client_v2.py`)
   - Interactive chat interface
   - Session state management for conversation history
   - Tool execution and result rendering

2. **MCP Servers (Multi-server integration)**
   - **Arithmetic MCP**: Local server via stdio transport (runs `uv run python main.py`)
   - **Expense Tracker MCP**: Remote FastMCP Cloud instance via HTTP transport

3. **LangChain Integration**
   - `AzureChatOpenAI` — LLM that decides when to call tools
   - `langchain-mcp-adapters` — bridges MCP servers to LangChain tools
   - Tool binding and invocation

### Message Flow

```
User Input
    ↓
LLM (decide: call tools or reply?)
    ↓
  ├─ No tools needed → Direct response (rendered)
  │
  └─ Tools needed →
      ├─ Store: AIMessage with tool_calls (not rendered)
      ├─ Execute: Each tool → ToolMessage (not rendered)
      ├─ LLM: Generate final answer using tool outputs
      └─ Store & Render: Final AIMessage with answer
```

This ordering ensures clean chat history without intermediate "fetching..." messages.

## Repository Layout

- `client_v2.py` — Main Streamlit app
- `pyproject.toml` — Dependencies and project metadata
- `airthmetic_mcp_server.py` — (Optional) Local arithmetic server for testing
- `.env` — Environment variables (see setup below)

## Setup with `uv`

### Prerequisites

- `uv` installed (`python -m pip install uv` or `pipx install uv`)
- Python 3.13+ (see `.python-version` if present)
- Azure OpenAI API key (for GPT-4o-mini model)

### Step 1: Sync Dependencies

From the `mcp-client` project root:

```powershell
uv sync
```

This creates a uv-managed virtual environment and installs all dependencies from `pyproject.toml` and `uv.lock`.

### Step 2: Configure Environment

Create a `.env` file in the project root with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
OPENAI_API_VERSION=2024-10-21
```

(Adjust the API version if your Azure instance uses a different version.)

### Step 3: Run the App with `uv`

```powershell
uv run streamlit run .\client_v2.py
```

This executes Streamlit inside the uv-managed environment. The app will start and display:

```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open that URL in your browser to start chatting.

## How It Works

### 1. Server Configuration (SERVERS dict)

```python
SERVERS = { 
    "arithmetic": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "--project", "C:\\D\\MCP\\learn-mcp\\arithmetic-mcp-server",
            "python", "main.py"
        ],
    },
    "expense": {
        "transport": "streamable_http",
        "url": "https://your-fastmcp-instance.fastmcp.app/mcp",
    },
}
```

- **Arithmetic server** (local): Uses stdio to spawn a Python process via `uv run`, pointing to the arithmetic MCP server project.
- **Expense server** (remote): Connects via HTTP to a FastMCP Cloud instance.

### 2. Initialization

When the Streamlit app starts:

```python
st.session_state.client = MultiServerMCPClient(SERVERS)
tools = asyncio.run(st.session_state.client.get_tools())
```

This connects to all servers and retrieves available tools (e.g., `add`, `subtract`, `list_expenses`).

### 3. Chat Loop

For each user message:

1. **First LLM call**: Decides which tools (if any) to invoke
2. **Tool execution**: Runs each requested tool and collects results
3. **Second LLM call**: Generates final answer using tool results
4. **Render**: Only the final answer is shown in chat

### 4. Message Handling

```python
# Skip rendering if AI message has tool_calls (intermediate fetch)
if getattr(msg, "tool_calls", None):
    continue

# Only render final AI messages without tool_calls
with st.chat_message("assistant"):
    st.markdown(msg.content)
```

## Running Without `uv` (Alternative)

If you prefer Python + venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt  # (if available)
# or install from pyproject.toml manually
pip install altair fastmcp langchain langchain-mcp-adapters langchain-openai python-dotenv streamlit

streamlit run .\client_v2.py
```

However, using `uv` is recommended for reproducible dependency pinning (via `uv.lock`).

## Troubleshooting

### Error: "Cannot find uv" or "FileNotFoundError"

**Solution**: Reload your PowerShell PATH or restart the terminal:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
uv --version
```

### Error: "Azure OpenAI API key not found"

**Solution**: Ensure `.env` is in the project root with correct credentials:

```powershell
# Check if .env exists
Test-Path .\.env

# Verify it contains AZURE_OPENAI_API_KEY
Get-Content .\.env | Select-String "AZURE_OPENAI"
```

### Error: "Cannot connect to MCP server"

**Solution**: Verify the server is running and the path is correct. For the arithmetic server:

```powershell
# Test the arithmetic server directly
Set-Location C:\D\MCP\learn-mcp\arithmetic-mcp-server
uv run python .\main.py
```

If it starts without errors, the server is healthy. Stop it (Ctrl+C) and try running the Streamlit app again.

### Error: "Tool not found" in chat

**Solution**: The LLM may not recognize tool names. Check:

1. Server is running and tools are loaded (check `st.session_state.tools`)
2. Tool names are correctly spelled in server implementations
3. LLM model has sufficient context to invoke the right tools

## Example Usage

1. Start the app: `uv run streamlit run .\client_v2.py`
2. In the chat, type: **"What is 15 plus 27?"**
3. LLM decides to call `add(15, 27)`
4. Tool executes and returns `42`
5. LLM composes a final message: **"15 plus 27 equals 42."**

## Extending the Project

### Add a new MCP server

1. Define it in `SERVERS`:

```python
SERVERS = {
    # ... existing servers ...
    "myserver": {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "--project", "/path/to/myserver", "python", "main.py"],
    },
}
```

2. Restart the app; new tools will be auto-loaded.

### Switch to a different LLM

Replace `AzureChatOpenAI` with any LangChain LLM (e.g., `ChatOpenAI`, `ChatAnthropic`):

```python
from langchain_openai import ChatOpenAI
st.session_state.llm = ChatOpenAI(model="gpt-4o-mini")
```

## Dependencies

- **streamlit** — Chat UI framework
- **langchain** — LLM orchestration
- **langchain-mcp-adapters** — MCP ↔ LangChain bridge
- **langchain-openai** — Azure OpenAI integration
- **fastmcp** — MCP protocol support
- **python-dotenv** — Environment variable loading
- **altair** — Charting (optional, included in deps)

See `pyproject.toml` for pinned versions.

## Development Tips

- **Hot reload**: Streamlit auto-reloads when you edit `client_v2.py`. Press `R` in the app to manually reload.
- **Debug mode**: Add `print()` statements in the code; output appears in the terminal running `uv run streamlit run`.
- **Async debugging**: Use `asyncio.run()` for testing async functions in isolation.

## Next Steps

- Add a `docker-compose.yml` to run Streamlit + MCP servers in containers
- Add authentication/API key validation in the chat UI
- Persist conversation history to a database
- Add multi-session support for concurrent users

---
Generated on: 2025-11-26
