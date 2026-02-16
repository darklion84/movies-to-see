#!/bin/bash

set -e

cd "$(dirname "$0")"

# Check for .env file
if [ ! -f "backend/.env" ]; then
    echo "Error: backend/.env file not found!"
    echo "Copy backend/.env.example to backend/.env and fill in your values:"
    echo "  cp backend/.env.example backend/.env"
    exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt -q

# Install frontend dependencies and build
echo "Installing frontend dependencies..."
cd frontend
npm install --silent 2>/dev/null
echo "Building frontend..."
npm run build --silent
cd ..

# Start the server
echo ""
echo "Starting server at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
cd backend
python main.py
