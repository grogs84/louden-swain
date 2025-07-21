#!/bin/bash

# Louden Swain Wrestling Platform Setup Script
# This script sets up the development environment for both frontend and backend

set -e

echo "🏗️  Setting up Louden Swain Wrestling Platform..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be 18+. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version) is installed"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "✅ Python $PYTHON_VERSION is installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install --legacy-peer-deps

# Set up backend virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ..

# Copy environment files if they don't exist
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        echo "📝 Copying backend environment file..."
        cp backend/.env.example backend/.env
        echo "⚠️  Please edit backend/.env with your actual environment variables"
    fi
fi

if [ ! -f "frontend/.env.local" ]; then
    if [ -f "frontend/.env.example" ]; then
        echo "📝 Copying frontend environment file..."
        cp frontend/.env.example frontend/.env.local
        echo "⚠️  Please edit frontend/.env.local with your actual environment variables"
    fi
fi

echo "🧪 Running quality checks..."

# Test frontend
echo "🔍 Testing frontend..."
npm run test:frontend

echo "✅ Setup complete!"
echo ""
echo "🚀 To start development:"
echo "  Frontend: npm run dev (or cd frontend && npm run dev)"
echo "  Backend: cd backend && source venv/bin/activate && uvicorn src.main:app --reload"
echo ""
echo "📖 Documentation:"
echo "  Deployment guide: DEPLOYMENT.md"
echo "  API docs (when running): http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "  npm run test:frontend  - Run frontend quality checks"
echo "  npm run test:backend   - Run backend quality checks (with backend venv activated)"
echo "  npm run test           - Run all quality checks"