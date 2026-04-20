#!/bin/bash
# Quick setup script for Temporiq AI

echo "🚀 Temporiq AI - Quick Setup"
echo "========================================"

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env from template
if [ ! -f .env ]; then
    echo ""
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your Supabase credentials!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your Supabase credentials"
echo "2. Run: streamlit run app.py"
echo ""
echo "For help, visit: https://github.com/srpatel03/Temporiq-AI"
