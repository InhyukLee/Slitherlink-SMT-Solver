Bash
#!/bin/bash

echo "===================================================="
echo " Setting up Slitherlink SMT Solver Environment"
echo "===================================================="

# 1. Create a virtual environment named .venv if it does not exist
if [ ! -d ".venv" ]; then
    echo "Creating isolated virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "Virtual environment (.venv) already exists."
fi

# 2. Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# 3. Upgrade pip to ensure smooth dependency resolution
echo "Upgrading pip..."
pip install --upgrade pip

# 4. Install project requirements from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "ERROR: requirements.txt not found! Please ensure it exists in the root directory."
    exit 1
fi

# 5. Verify that pySMT can communicate with the Z3 solver binding
echo "Verifying SMT solver bindings..."
pysmt-install --check

echo "===================================================="
echo " Environment setup complete! Your virtual environment"
echo " is active and ready for development."
echo "===================================================="