#!/bin/bash

echo "Novel Task Manager Backend Development Setup"
echo "============================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "Setup complete!"
echo ""
echo "To start the database services, run:"
echo "  docker-compose up -d"
echo ""
echo "To initialize the database, run:"
echo "  python init_db.py"
echo ""
echo "To start the API server, run:"
echo "  python app/main.py"
echo ""
echo "API will be available at:"
echo "  http://localhost:8000"
echo "  Documentation: http://localhost:8000/docs"