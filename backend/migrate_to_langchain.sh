#!/bin/bash

# Migration script from CrewAI to LangChain
echo "========================================="
echo "AgentDoc: CrewAI to LangChain Migration"
echo "========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "Please activate your virtual environment first:"
    echo "  source .venv/bin/activate  # Linux/Mac"
    echo "  .venv\\Scripts\\activate    # Windows"
    exit 1
fi

echo "✓ Virtual environment detected: $VIRTUAL_ENV"
echo ""

# Uninstall CrewAI
echo "Step 1: Uninstalling CrewAI..."
pip uninstall crewai crewai-tools -y
if [ $? -eq 0 ]; then
    echo "✓ CrewAI uninstalled successfully"
else
    echo "⚠️  Warning: CrewAI uninstall had issues (may not be installed)"
fi
echo ""

# Install LangChain
echo "Step 2: Installing LangChain..."
pip install langchain langchain-google-genai
if [ $? -eq 0 ]; then
    echo "✓ LangChain installed successfully"
else
    echo "❌ Error: LangChain installation failed"
    exit 1
fi
echo ""

# Install all requirements
echo "Step 3: Installing all requirements..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ All requirements installed"
else
    echo "⚠️  Warning: Some requirements may have failed"
fi
echo ""

# Verify installation
echo "Step 4: Verifying installation..."
python -c "import langchain; print('✓ LangChain version:', langchain.__version__)"
python -c "import langchain_google_genai; print('✓ LangChain Google GenAI installed')"
echo ""

# Check for CrewAI (should not be present)
python -c "import crewai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✓ CrewAI successfully removed"
else
    echo "⚠️  Warning: CrewAI still detected"
fi
echo ""

echo "========================================="
echo "Migration Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Test the application: python manage.py runserver"
echo "2. Upload a test document to verify functionality"
echo "3. Check logs for any errors"
echo ""
echo "For more information, see MIGRATION_TO_LANGCHAIN.md"
