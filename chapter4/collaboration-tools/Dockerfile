# Collaboration Tools MCP Server Dockerfile
# Supports browser automation, Excel processing, and human-in-the-loop interactions
# Uses latest stable versions (as of 2025)

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    ca-certificates \
    # For browser automation
    chromium-browser \
    chromium-chromedriver \
    # For GUI applications (headless)
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.13 (latest stable)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
        python3.13 \
        python3.13-dev \
        python3.13-venv \
        python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV DISPLAY=:99
ENV WORKSPACE_DIR=/workspace
RUN mkdir -p /workspace && chmod 777 /workspace

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app /workspace

# Switch to non-root user
USER mcpuser

# Run the MCP server (with xvfb for headless browser)
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & python3 src/main.py"]
