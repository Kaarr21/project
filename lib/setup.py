#!/bin/bash
# Setup script for Personal Finance Tracker

echo "Setting up Personal Finance Tracker..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install sqlalchemy

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate"
echo "python lib/cli.py"
