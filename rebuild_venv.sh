#!/bin/bash

VENV_NAME="venv"

echo "🔁 Removing old virtual environment..."
rm -rf $VENV_NAME

echo "🚀 Creating new virtual environment..."
python3 -m venv $VENV_NAME

echo "✅ Virtual environment '$VENV_NAME' created."

echo "📦 Activating venv and installing dependencies..."
source $VENV_NAME/bin/activate

if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed from requirements.txt"
else
    echo "⚠️ No requirements.txt found. venv is clean and ready."
fi

echo "🎉 Environment rebuild complete. You’re ready to go!"


# "Run this script:  ./rebuild_venv.sh"