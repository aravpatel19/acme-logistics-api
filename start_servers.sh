#!/bin/bash

# Start servers for Acme Logistics Demo

echo "🚀 Starting Acme Logistics Demo Servers..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Kill any existing servers
echo "Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
sleep 2

# Start API server
echo "Starting API server on port 8000..."
cd "$SCRIPT_DIR/api" && python main.py &
API_PID=$!
echo "API server PID: $API_PID"

# Wait for API to start
sleep 3

# Start dashboard server
echo -e "\nStarting dashboard server on port 8001..."
cd "$SCRIPT_DIR/dashboard" && python -m http.server 8001 &
DASHBOARD_PID=$!
echo "Dashboard server PID: $DASHBOARD_PID"

echo ""
echo "✅ Servers started successfully!"
echo ""
echo "🌐 Access points:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Dashboard: http://localhost:8001"
echo ""
echo "🛑 To stop servers, run:"
echo "  lsof -ti:8000,8001 | xargs kill -9"
echo ""
echo "Press Ctrl+C to stop servers..."

# Keep script running
wait