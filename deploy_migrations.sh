#!/bin/bash

# === CONFIG ===
HEROKU_APP="airborne-images-12bytes"  # Replace with your actual Heroku app name
BRANCH="main"                         # Change to 'master' if you're using that

echo "🔧 Making migrations..."
python3 manage.py makemigrations

echo "🧹 Staging migrations..."
git add */migrations/*.py

echo "💬 Committing migration files..."
git commit -m "Auto: Apply latest model changes and migrations" || echo "✅ Nothing to commit."

echo "⬆️  Pushing code to Heroku..."
git push heroku $BRANCH

echo "🚀 Running migrations on Heroku..."
heroku run python manage.py migrate --app $HEROKU_APP

echo "✅ Done!"
