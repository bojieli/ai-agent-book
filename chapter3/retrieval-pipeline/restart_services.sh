#!/bin/bash

# Script to restart all services for the retrieval pipeline
# Run this from the retrieval-pipeline directory

echo "Restarting all retrieval pipeline services..."
echo "============================================"

# Kill existing services if running
echo "Stopping existing services..."
pkill -f "python.*server.py" 2>/dev/null
pkill -f "python.*main.py" 2>/dev/null
# Kill old ports if any still running
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "uvicorn.*8001" 2>/dev/null
pkill -f "uvicorn.*4242" 2>/dev/null
pkill -f "uvicorn.*8003" 2>/dev/null
# Kill new ports
pkill -f "uvicorn.*4240" 2>/dev/null
pkill -f "uvicorn.*4241" 2>/dev/null
pkill -f "uvicorn.*4242" 2>/dev/null

sleep 2

# Start dense embedding service
echo ""
echo "Starting Dense Embedding Service (port 4240)..."
cd ../dense-embedding
python main.py --port 4240 > dense.log 2>&1 &
DENSE_PID=$!
echo "Dense service started with PID: $DENSE_PID"

sleep 3

# Start sparse embedding service
echo ""
echo "Starting Sparse Embedding Service (port 4241)..."
cd ../sparse-embedding
python server.py 4241 > sparse.log 2>&1 &
SPARSE_PID=$!
echo "Sparse service started with PID: $SPARSE_PID"

sleep 3

# Start retrieval pipeline service
echo ""
echo "Starting Retrieval Pipeline Service (port 4242)..."
cd ../retrieval-pipeline
python main.py --port 4242 > pipeline.log 2>&1 &
PIPELINE_PID=$!
echo "Pipeline service started with PID: $PIPELINE_PID"

sleep 5

echo ""
echo "All services started!"
echo "====================="
echo "Dense service:    http://localhost:4240 (PID: $DENSE_PID)"
echo "Sparse service:   http://localhost:4241 (PID: $SPARSE_PID)"
echo "Pipeline service: http://localhost:4242 (PID: $PIPELINE_PID)"
echo ""
echo "Logs are being written to:"
echo "  - dense.log (in dense-embedding/)"
echo "  - sparse.log (in sparse-embedding/)"
echo "  - pipeline.log (in retrieval-pipeline/)"
echo ""
echo "To test the pipeline, run: python test_pipeline.py"
echo "To stop all services, run: pkill -f 'python.*server.py|python.*main.py'"
