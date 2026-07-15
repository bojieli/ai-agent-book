# Execution Tools MCP Server Dockerfile
# Supports multi-language code execution with scientific computing packages
# Uses latest stable versions of all tools (as of 2025)

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
    gnupg \
    lsb-release \
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

# Install Node.js 22.x LTS for JavaScript/TypeScript support
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    npm install -g typescript@latest tsx@latest ts-node@latest

# Install common Node.js packages globally
RUN npm install -g \
    lodash \
    axios \
    chalk \
    commander \
    express \
    @types/node \
    @types/express

# Install Go 1.22 (latest stable)
RUN wget https://go.dev/dl/go1.22.10.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.10.linux-amd64.tar.gz && \
    rm go1.22.10.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:/root/go/bin:${PATH}"
ENV GOPATH="/root/go"

# Pre-download common Go modules (will be cached in module cache)
RUN go install github.com/go-delve/delve/cmd/dlv@latest

# Install Java 21 LTS (latest LTS)
RUN apt-get update && \
    apt-get install -y openjdk-21-jdk && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

# Install C++ compiler (GCC 13) with common libraries
RUN apt-get update && apt-get install -y \
    g++-13 \
    gcc-13 \
    libboost-all-dev \
    libssl-dev \
    libcrypto++-dev \
    cmake \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 100 \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (latest stable)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:${PATH}"

# Install PHP 8.3 with common extensions
RUN apt-get update && apt-get install -y \
    php8.3-cli \
    php8.3-curl \
    php8.3-mbstring \
    php8.3-xml \
    php8.3-zip \
    && rm -rf /var/lib/apt/lists/*

# Install Bash (already in base image, but ensure latest)
RUN apt-get update && apt-get install -y bash && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install -r requirements.txt

# Copy application files
COPY . .

# Expose default MCP stdio interface (no port needed for stdio)
# The server communicates via stdin/stdout

# Set environment variables
ENV WORKSPACE_DIR=/workspace
RUN mkdir -p /workspace && chmod 777 /workspace

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app /workspace

# Switch to non-root user
USER mcpuser

# Run the MCP server
CMD ["python3", "server.py"]
