#!/bin/bash

# Loan Lifecycle Backend - Setup Script

echo "🏦 Setting up Loan Lifecycle Backend..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your PostgreSQL credentials"
echo "2. Create PostgreSQL database: createdb loan_db"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run the server: uvicorn app.main:app --reload"
echo ""
echo "📚 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
