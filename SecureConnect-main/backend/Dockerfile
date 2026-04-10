
# 2-Stage Multi-Architecture Build w/ Ubuntu 22.04 LTS
# We use Ubuntu 22.04 as requested, installing Python explicitly.

# --- Stage 1: Builder ---
FROM ubuntu:22.04 as builder
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    curl \
    build-essential \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (Real setup)
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# ENV PATH="/root/.cargo/bin:${PATH}"

# Install Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Source Code
COPY . .

# --- Stage 2: Production Image ---
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install runtime Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Copy artifacts from builder (site-packages)
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
# Just ensuring pip libs match system python version
# In production, we'd use virtualenvs, but copying globally for simplicity here.

COPY --from=builder /code /app

# Environment Variables
ENV PYTHONPATH=/app
ENV REDIS_URL=redis://redis:6379/0
ENV PINECONE_API_KEY=********
ENV GEMINI_API_KEY=********
ENV MCP_SERVER_MODE=stdio

EXPOSE 8000

# Start Uvicorn Server
# Also includes MCP Server logic hook (available via 'app.mcp_server')
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
