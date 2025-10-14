FROM python:3.13-slim

WORKDIR /app

# Copy project files early so uv can install from pyproject/lock
COPY pyproject.toml uv.lock /app/
COPY . /app

# Install uv and let uv manage the environment and dependencies inside the container
RUN python -m pip install --upgrade pip \
    && python -m pip install uv

EXPOSE 8000

# Sync the environment and run via uv so the container uses the same managed env as a dev machine
CMD ["sh", "-c", "uv sync && uv run fastmcp dev ./main.py"]
