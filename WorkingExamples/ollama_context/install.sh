#!/bin/bash
# install.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${YELLOW}>>> $1${NC}"
}

# Function to check if last command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success: $1${NC}"
    else
        echo -e "${RED}✗ Error: $1${NC}"
        exit 1
    fi
}

# Check if we're already in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        check_status "Virtual environment creation"
    fi

    print_status "NOTE: You need to activate the virtual environment manually:"
    echo -e "${GREEN}Run: source venv/bin/activate${NC}"
    echo -e "Then run this script again."
    exit 0
fi

# If we get here, we're in a virtual environment
print_status "Installing retrieval (RAG) library..."
pip3 install -e ../rag --break-system-packages
check_status "Retrieval installation"

print_status "Installing context (CAG) library..."
pip3 install -e ../cag --break-system-packages
check_status "Context installation"

print_status "Installing combined context library..."
pip3 install -e . --break-system-packages
check_status "Context library installation"

echo -e "\n${GREEN}Installation Complete!${NC}"
echo -e "You can now use the libraries as follows:"
echo -e "- Import Retrieval: from rag_ollama import RAGEngine"
echo -e "- Import Context:   from cag_ollama import CAGEngine"
echo -e "- Import Combined:  from ollama_context import ContextEngine\n"
