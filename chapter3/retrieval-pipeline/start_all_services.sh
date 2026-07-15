#!/bin/bash

# Start all services for the retrieval pipeline

echo "========================================="
echo "Starting Retrieval Pipeline Services"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill existing services on ports
echo -e "${YELLOW}Checking for existing services...${NC}"
for port in 4240 4241 4242; do
    if check_port $port; then
        echo -e "${YELLOW}Killing existing service on port $port${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
    fi
done

# Start dense embedding service
echo -e "\n${GREEN}Starting Dense Embedding Service (port 8000)...${NC}"
cd ../dense-embedding
python main.py --port 8000 > dense.log 2>&1 &
DENSE_PID=$!
echo "Dense service PID: $DENSE_PID"

# Wait for dense service to start
echo "Waiting for dense service to initialize..."
for i in {1..30}; do
    if check_port 8000; then
        echo -e "${GREEN}✓ Dense service ready${NC}"
        break
    fi
    sleep 1
done

# Start sparse embedding service
echo -e "\n${GREEN}Starting Sparse Embedding Service (port 8001)...${NC}"
cd ../sparse-embedding
python server.py --port 8001 > sparse.log 2>&1 &
SPARSE_PID=$!
echo "Sparse service PID: $SPARSE_PID"

# Wait for sparse service to start
echo "Waiting for sparse service to initialize..."
for i in {1..30}; do
    if check_port 8001; then
        echo -e "${GREEN}✓ Sparse service ready${NC}"
        break
    fi
    sleep 1
done

# Start retrieval pipeline
echo -e "\n${GREEN}Starting Retrieval Pipeline (port 4242)...${NC}"
cd ../retrieval-pipeline
python main.py --port 4242 > pipeline.log 2>&1 &
PIPELINE_PID=$!
echo "Pipeline service PID: $PIPELINE_PID"

# Wait for pipeline to start
echo "Waiting for pipeline to initialize (loading reranker model)..."
for i in {1..60}; do
    if check_port 4242; then
        echo -e "${GREEN}✓ Pipeline ready${NC}"
        break
    fi
    sleep 1
done

# Check all services
echo -e "\n========================================="
echo "Service Status:"
echo "========================================="

if check_port 8000; then
    echo -e "${GREEN}✓ Dense Embedding Service: http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Dense Embedding Service failed to start${NC}"
fi

if check_port 8001; then
    echo -e "${GREEN}✓ Sparse Embedding Service: http://localhost:8001${NC}"
else
    echo -e "${RED}✗ Sparse Embedding Service failed to start${NC}"
fi

if check_port 4242; then
    echo -e "${GREEN}✓ Retrieval Pipeline: http://localhost:4242${NC}"
    echo -e "${GREEN}✓ API Documentation: http://localhost:4242/docs${NC}"
else
    echo -e "${RED}✗ Retrieval Pipeline failed to start${NC}"
fi

echo -e "\n========================================="
echo "All services started!"
echo "========================================="
echo ""
echo "To test the pipeline:"
echo "  python test_client.py"
echo ""
echo "To run the demo:"
echo "  python demo.py"
echo ""
echo "To stop all services:"
echo "  ./stop_all_services.sh"
echo ""
echo "Service logs:"
echo "  Dense: dense.log"
echo "  Sparse: sparse.log"
echo "  Pipeline: pipeline.log"
