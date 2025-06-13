#!/bin/bash

# Kalimati Market Scraper Runner
# This script builds and runs the Kalimati Market scraper using Docker

# Set script to exit on error
set -e

echo "🚀 Starting Kalimati Market Scraper..."

# Create data directory if it doesn't exist
mkdir -p data

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    echo "Running with Docker Compose..."
    docker-compose up --build
# Check if Docker is installed
elif command -v docker &> /dev/null; then
    echo "Running with Docker..."
    docker build -t kalimati-scraper .
    docker run -v "$(pwd)/data:/app/data" kalimati-scraper
else
    echo "Error: Neither Docker nor Docker Compose is installed."
    echo "Please install Docker to run this application."
    exit 1
fi

echo "✅ Scraper completed. Check the 'data' directory for results." 
