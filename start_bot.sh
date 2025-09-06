#!/bin/bash

# Telegram Music Bot Start Script

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p downloads temp logs

# Check if config.py exists
if [ ! -f "src/config.py" ]; then
    echo "Config file not found. Please run setup.sh first."
    exit 1
fi

# Start the bot
echo "Starting Telegram Music Bot..."
python src/bot.py