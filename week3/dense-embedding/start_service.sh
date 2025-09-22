#!/bin/bash

# Vector Similarity Search Service Startup Script

echo "========================================"
echo "Vector Similarity Search Service"
echo "========================================"

# Default values
INDEX_TYPE=${1:-hnsw}
PORT=${2:-8000}
DEBUG=${3:-true}

echo ""
echo "Configuration:"
echo "  Index Type: $INDEX_TYPE"
echo "  Port: $PORT"
echo "  Debug: $DEBUG"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip list | grep -q "FlagEmbedding" || {
    echo "Installing dependencies..."
    pip install -r requirements.txt
}

# Start the service
echo ""
echo "Starting service..."
echo "========================================"

if [ "$DEBUG" = "true" ]; then
    python main.py --index-type $INDEX_TYPE --port $PORT --debug
else
    python main.py --index-type $INDEX_TYPE --port $PORT
fi
