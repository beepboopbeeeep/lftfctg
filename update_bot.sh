#!/bin/bash

# Telegram Music Bot Update Script

cd "$(dirname "$0")"

echo "=== Telegram Music Bot Update Script ==="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git first."
    exit 1
fi

# Function to ask for confirmation
ask_confirmation() {
    read -p "$1 (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Update cancelled."
        exit 1
    fi
}

# Stop bot if running as service
echo "Checking if bot is running as service..."
if systemctl is-active --quiet telegram-music-bot; then
    echo "Stopping bot service..."
    sudo systemctl stop telegram-music-bot
fi

# Backup current configuration
echo "Backing up configuration..."
if [ -f "src/config.py" ]; then
    cp src/config.py src/config.py.backup
    echo "Configuration backed up to src/config.py.backup"
fi

# Pull latest changes
echo "Pulling latest changes from repository..."
git pull origin main

# Check if there are conflicts
if [ $? -ne 0 ]; then
    echo "Error: Git pull failed. Please resolve conflicts manually."
    exit 1
fi

# Restore configuration
echo "Restoring configuration..."
if [ -f "src/config.py.backup" ]; then
    cp src/config.py.backup src/config.py
    echo "Configuration restored from backup."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating new one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p downloads temp logs config

# Make scripts executable
echo "Making scripts executable..."
chmod +x setup.sh start_bot.sh update_bot.sh

# Start bot service if it was running
if systemctl is-enabled --quiet telegram-music-bot; then
    echo "Starting bot service..."
    sudo systemctl start telegram-music-bot
    echo "Bot service started."
fi

echo ""
echo "=== Update completed successfully! ==="
echo ""
echo "To start the bot manually:"
echo "  ./start_bot.sh"
echo ""
echo "To check bot status (if running as service):"
echo "  sudo systemctl status telegram-music-bot"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u telegram-music-bot -f"
echo ""
echo "Enjoy your updated Telegram Music Bot! 🎵"