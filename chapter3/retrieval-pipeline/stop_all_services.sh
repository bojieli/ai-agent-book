#!/bin/bash

# Stop all retrieval pipeline services

echo "Stopping all retrieval pipeline services..."

# Kill processes on ports
for port in 4240 4241 4242; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "Stopping service on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
    fi
done

echo "All services stopped."
