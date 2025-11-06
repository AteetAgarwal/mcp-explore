# Simple MCP Server — README

This repository contains a small FastMCP example server (`main.py`) intended for experimentation and for deploying to FastMCP Cloud via GitHub.

Purpose
- Provide an async example using `fastmcp` + `aiosqlite` that can be run locally and inspected with `uv`.

Repository layout
- `main.py` — MCP server (async tools using `aiosqlite`).
- `pyproject.toml` — project metadata and dependencies.

Inspect the MCP locally with `uv`

If you have `uv` installed, the most convenient way to run and inspect the MCP is to use `uv`'s managed environment. From the project root (where `pyproject.toml` and `uv.lock` live), run:

```powershell
# create uv-managed environment and install pinned deps
uv sync
# start the MCP in dev mode (fastmcp transport)
uv run fastmcp dev .\main.py
```

If you already have a running MCP and you want to run the same `main.py` inside the uv-managed environment, you can run Python directly inside uv's environment to avoid starting a duplicate service:

```powershell
# run the python entrypoint inside the uv-managed environment (does not create an extra service)
uv run .\main.py
```

Detecting if the MCP is already running
- If the process is listening on the configured transport (for example HTTP port 8000), `uv run fastmcp dev` will likely fail to bind the port. Check running processes or ports:

```powershell
# Windows: check if anything is listening on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
# or list Python processes and inspect command lines
Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
```

Deploying to FastMCP Cloud via GitHub

1. Push your repository to GitHub (a new repo or an existing one):

```powershell
git init
git add .
git commit -m "initial commit"
git remote add origin <your-git-url>
git push -u origin main
```

2. In the FastMCP Cloud dashboard (or CI integration), connect your GitHub repository and enable deployments. Typical steps:
- Choose the repository and branch to deploy (e.g., `main`).
- Configure any environment variables or secrets (if your `main.py` expects any).
- Configure resource limits (if offered by the platform).

3. When you push to the configured branch, FastMCP Cloud will build the project using `pyproject.toml` and should start the MCP server. In many setups, FastMCP Cloud will run the same command you use locally; check the dashboard for the exact command it runs (common: `uv run fastmcp dev main.py` or `uv run python main.py`).

Debugging remote deploys
- Use FastMCP Cloud's deployment logs to see build and runtime output.
- If the cloud build fails during dependency installation, ensure your `pyproject.toml` lists the correct dependencies and `requires-python` version.
- If your app binds to a port, ensure FastMCP Cloud allows that port or uses an HTTP transport expected by the platform.

Extras
- I can add a simple `.github/workflows/deploy.yml` that triggers on push and runs `uv` inside the workflow to validate the project before pushing to FastMCP Cloud. Tell me if you want that and I'll add a working CI example.

---
Generated on: 2025-10-14
