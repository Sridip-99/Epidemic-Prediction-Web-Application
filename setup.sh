#!/bin/bash

# Create Virtual Environment
echo "Creating virtual environment 'myenv'..."
python3 -m venv myenv

# Activate the Virtual Environment
echo "Activating virtual environment..."
source myenv/bin/activate

# Install Packages
echo "Installing Python packages from requirements.txt..."
pip install -r requirements.txt

echo "All packages installed successfully!"
