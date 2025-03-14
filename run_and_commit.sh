#!/bin/bash

# Script to run the Kalimati Market scraper and commit the changes to GitHub

# Set script to exit on error
set -e

echo "🚀 Starting Kalimati Market Scraper with GitHub commit..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Get the current date
DATE=$(date +"%Y-%m-%d")

# Create data directory if it doesn't exist
mkdir -p data

# Run the scraper using Docker
echo "🐳 Running scraper in Docker container..."
docker build -t kalimati-scraper .
docker run --rm -v "$(pwd)/data:/app/data" kalimati-scraper

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed. Please install Git first."
    exit 1
fi

# Check if the current directory is a git repository
if [ ! -d .git ]; then
    echo "❌ Error: This directory is not a git repository. Please initialize git first."
    exit 1
fi

# Commit and push changes
echo "📝 Committing changes to GitHub..."
git add data/
git diff --quiet && git diff --staged --quiet || git commit -m "Update market data: $DATE"

# Ask if the user wants to push the changes
read -p "Do you want to push the changes to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing changes to GitHub..."
    git push
    echo "✅ Changes pushed to GitHub."
else
    echo "❌ Changes not pushed to GitHub."
fi

echo "✅ Scraper completed and changes committed." 