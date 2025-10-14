## Expense Tracker — MCP Server
Notes:
- Use uv to run and manage the project. Running the server inside the managed environment is recommended; e.g.:
    - uv run fastmcp dev .\main.py
    - or uv run python .\main.py

Primary workflow — use `uv` as the project manager (recommended)

This repository is configured for use with `uv` (the Python package / project manager). Using `uv` keeps dependency resolution, virtual environments, and runs reproducible and managed by the project metadata (`pyproject.toml` and `uv.lock`). The steps below assume you're in the project root (`\learn-mcp\expense-tracker-mcp-server`).

1. Ensure `uv` is installed on your machine (one-time). See the uv project docs for installation instructions.

2. Sync the project's environment from the lockfile (creates the managed environment and installs pinned deps):

```powershell
# from the project root
uv sync
```

3. Run the project through `uv` (this executes inside the managed environment):

```powershell
# run the app via the managed environment
uv run fastmcp dev .\main.py

# or run the Python entrypoint inside the managed environment
uv run python .\main.py
```

Project files
- `main.py` — MCP server and tool implementations.
- `expenses.db` — SQLite database (created and used by the app).
- `categories.json` — JSON resource served at `expense://categories`.
- `pyproject.toml` — project metadata (requires Python >= 3.13 and `fastmcp`).
- `uv.lock` — pinned dependencies for `uv`.

Requirements
- Development machine (recommended): Python 3.13+ (see `.python-version`).
- Runtime package: `fastmcp` (installed into the managed environment by `uv sync`).

Notes & troubleshooting
- Always run `uv` commands from the project root where `pyproject.toml` and `uv.lock` live. If you run from a different directory you may get errors like "Failed to canonicalize script path" because relative paths won't resolve.
- To get an interactive shell inside the managed environment, use `uv run` with your shell of choice (see uv docs).

Quick start — run locally with `uv` (recommended)
1. Ensure Python 3.13+ is installed on your machine.
2. Ensure `uv` is installed.
3. From the project root, create the managed environment and install deps:

```powershell
uv sync
```

4. Run the server:

```powershell
uv run fastmcp dev .\main.py
```

Notes:
- Running `uv run python .\main.py` will also start the FastMCP server via `mcp.run()` as implemented in `main.py`.
- You do not need to run `pip` directly when using the `uv` workflow; `uv sync` installs the pinned runtime dependencies into the managed environment.

Running on a machine that does NOT have Python or `uv` installed

Option A — Use Docker (recommended for hosts without Python):

Prerequisites: Docker Desktop or another Docker engine installed on the host.

1. Build the image from the project root:

```powershell
# build an image named expense-mcp
docker build -t expense-mcp .
```

2. Run the container (bind-mount the data file to persist the DB locally):

```powershell
# create a data dir and mount it
mkdir .\data
# run container and mount the project to /app and the local data dir for DB persistence
docker run --rm -it -v ${PWD}:/app -v ${PWD}:/app expense-mcp
```

Notes about Docker: the included `Dockerfile` installs Python 3.13 in the container, installs `fastmcp`, copies the project and runs `python main.py`. This avoids needing Python/uv on the host.

Option B — Portable Python / Standalone binary
- You can create a standalone executable (Windows .exe) with PyInstaller or similar, but building the binary requires Python on the build machine. If you need a pre-built standalone binary, I can add a simple PyInstaller spec and build instructions.

Development tips
- If you want to iterate on `categories.json` while the server is running, the resource loader reads the file each time so edits become visible immediately.
- Persist the `expenses.db` file between runs by mounting it out of the container (if using Docker) or keeping it in the project folder on disk.

Security & production notes
- This project is an example/demo; it does not implement authentication, backup, or production-grade configuration. For production you should:
    - Add authentication/authorization to MCP endpoints.
    - Use a managed database or backups for `expenses.db`.
    - Run behind a reverse proxy or in a supervised service manager.

Help / next steps
- If you'd like, I can:
    - Add a `requirements.txt` and a `make` / `PowerShell` script to automate setup (still driven by `uv` sync/run).
    - Add a PyInstaller recipe to produce a Windows executable.
    - Add a small docker-compose file showing how to persist the DB.

---
Generated on: 2025-10-14
