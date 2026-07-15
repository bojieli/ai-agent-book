# Perception Tools MCP Server Dockerfile
# Supports document processing, web search, and data retrieval
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
    # For image processing
    libgl1-mesa-glx \
    libglib2.0-0 \
    # For PDF processing
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-chi-sim \
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
ENV DATA_DIR=/data
RUN mkdir -p /data && chmod 777 /data

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app /data

# Switch to non-root user
USER mcpuser

# Run the MCP server
CMD ["python3", "src/main.py"]
