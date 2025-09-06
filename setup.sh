#!/bin/bash

# Telegram Music Bot Setup Script
# This script will help you set up the Telegram Music Bot

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get user input
get_input() {
    read -p "$1: " input
    echo "$input"
}

# Function to validate input
validate_input() {
    if [ -z "$1" ]; then
        print_error "Input cannot be empty"
        exit 1
    fi
}

# Function to update bot token in config
update_bot_token() {
    local token="$1"
    local config_file="src/config.py"
    
    if [ -f "$config_file" ]; then
        sed -i "s/BOT_TOKEN = \"YOUR_TELEGRAM_BOT_TOKEN_HERE\"/BOT_TOKEN = \"$token\"/" "$config_file"
        print_success "Bot token updated in config.py"
    else
        print_error "Config file not found: $config_file"
        exit 1
    fi
}

# Function to update admin user ID
update_admin_id() {
    local admin_id="$1"
    local config_file="src/config.py"
    
    if [ -f "$config_file" ]; then
        sed -i "s/ADMIN_USER_ID = 123456789/ADMIN_USER_ID = $admin_id/" "$config_file"
        print_success "Admin user ID updated in config.py"
    else
        print_error "Config file not found: $config_file"
        exit 1
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    # Check if running on Debian/Ubuntu
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git curl
    # Check if running on CentOS/RHEL/Fedora
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip ffmpeg git curl
    # Check if running on macOS
    elif command_exists brew; then
        brew install python3 ffmpeg git curl
    else
        print_warning "Could not detect package manager. Please install the following manually:"
        print_warning "- Python 3.8+"
        print_warning "- pip3"
        print_warning "- ffmpeg"
        print_warning "- git"
        print_warning "- curl"
    fi
    
    print_success "System dependencies installed"
}

# Function to create virtual environment
create_venv() {
    print_info "Creating Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Function to activate virtual environment and install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install required packages
    pip install python-telegram-bot shazamio yt-dlp instaloader requests firebase-admin spotipy mutagen pillow
    
    print_success "Python dependencies installed"
}

# Function to create directories
create_directories() {
    print_info "Creating required directories..."
    
    mkdir -p downloads temp logs config
    
    print_success "Directories created"
}

# Function to create requirements.txt
create_requirements() {
    print_info "Creating requirements.txt..."
    
    cat > requirements.txt << EOF
python-telegram-bot>=20.4
shazamio>=0.6.0
yt-dlp>=2023.7.6
instaloader>=4.9.2
requests>=2.31.0
firebase-admin>=6.3.0
spotipy>=2.23.0
mutagen>=1.46.0
Pillow>=10.0.0
EOF
    
    print_success "requirements.txt created"
}

# Function to create systemd service file
create_systemd_service() {
    print_info "Creating systemd service file..."
    
    local service_file="/etc/systemd/system/telegram-music-bot.service"
    
    sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=Telegram Music Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python src/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable telegram-music-bot
    
    print_success "Systemd service created and enabled"
}

# Function to create start script
create_start_script() {
    print_info "Creating start script..."
    
    cat > start_bot.sh << 'EOF'
#!/bin/bash

# Telegram Music Bot Start Script

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the bot
python src/bot.py
EOF
    
    chmod +x start_bot.sh
    
    print_success "Start script created: start_bot.sh"
}

# Function to create update script
create_update_script() {
    print_info "Creating update script..."
    
    cat > update_bot.sh << 'EOF'
#!/bin/bash

# Telegram Music Bot Update Script

cd "$(dirname "$0")"

print_info "Stopping bot..."
sudo systemctl stop telegram-music-bot 2>/dev/null || true

print_info "Pulling latest changes..."
git pull origin main

print_info "Updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt

print_info "Starting bot..."
sudo systemctl start telegram-music-bot

print_success "Bot updated successfully!"
EOF
    
    chmod +x update_bot.sh
    
    print_success "Update script created: update_bot.sh"
}

# Function to create log rotation config
create_log_rotation() {
    print_info "Creating log rotation configuration..."
    
    sudo tee /etc/logrotate.d/telegram-music-bot > /dev/null << EOF
logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
    
    print_success "Log rotation configuration created"
}

# Function to setup Firebase (optional)
setup_firebase() {
    print_info "Firebase setup (optional)..."
    
    read -p "Do you want to set up Firebase for cloud data storage? (y/N): " setup_firebase
    if [[ "$setup_firebase" =~ ^[Yy]$ ]]; then
        print_info "Please follow these steps to set up Firebase:"
        print_info "1. Go to https://console.firebase.google.com/"
        print_info "2. Create a new project or select an existing one"
        print_info "3. Add a web app to your project"
        print_info "4. Download the service account key JSON file"
        print_info "5. Place the JSON file in the config/ directory as 'firebase-credentials.json'"
        
        read -p "Press Enter when you have placed the Firebase credentials file..."
        
        if [ -f "config/firebase-credentials.json" ]; then
            print_success "Firebase credentials file found"
        else
            print_warning "Firebase credentials file not found. The bot will use local storage instead."
        fi
    else
        print_info "Skipping Firebase setup. The bot will use local storage."
    fi
}

# Function to test bot
test_bot() {
    print_info "Testing bot..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test if bot can start
    if timeout 10 python src/bot.py 2>/dev/null; then
        print_success "Bot test passed"
    else
        print_warning "Bot test failed. Please check the configuration."
    fi
}

# Main setup function
main() {
    echo "================================================"
    echo "  Telegram Music Bot Setup Script"
    echo "================================================"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Welcome message
    print_info "This script will help you set up the Telegram Music Bot"
    print_info "Please make sure you have the following ready:"
    print_info "1. Telegram Bot Token from @BotFather"
    print_info "2. Your Telegram User ID (for admin access)"
    echo ""
    
    # Get bot token
    bot_token=$(get_input "Enter your Telegram Bot Token")
    validate_input "$bot_token"
    
    # Get admin user ID
    admin_id=$(get_input "Enter your Telegram User ID")
    validate_input "$admin_id"
    
    # Check if it's a number
    if ! [[ "$admin_id" =~ ^[0-9]+$ ]]; then
        print_error "Admin user ID must be a number"
        exit 1
    fi
    
    echo ""
    print_info "Starting setup process..."
    echo ""
    
    # Install system dependencies
    install_system_deps
    echo ""
    
    # Create directories
    create_directories
    echo ""
    
    # Create virtual environment
    create_venv
    echo ""
    
    # Install Python dependencies
    install_python_deps
    echo ""
    
    # Create requirements file
    create_requirements
    echo ""
    
    # Update configuration
    update_bot_token "$bot_token"
    update_admin_id "$admin_id"
    echo ""
    
    # Setup Firebase (optional)
    setup_firebase
    echo ""
    
    # Create scripts
    create_start_script
    create_update_script
    echo ""
    
    # Create systemd service (optional)
    read -p "Do you want to create a systemd service for auto-start on boot? (y/N): " create_service
    if [[ "$create_service" =~ ^[Yy]$ ]]; then
        create_systemd_service
        create_log_rotation
        echo ""
    fi
    
    # Test bot
    test_bot
    echo ""
    
    # Setup complete
    print_success "Setup completed successfully!"
    echo ""
    print_info "To start the bot:"
    print_info "  • Manual start: ./start_bot.sh"
    print_info "  • System service: sudo systemctl start telegram-music-bot"
    echo ""
    print_info "To check bot status:"
    print_info "  • System service: sudo systemctl status telegram-music-bot"
    echo ""
    print_info "To view logs:"
    print_info "  • System service: sudo journalctl -u telegram-music-bot -f"
    echo ""
    print_info "To update the bot:"
    print_info "  • Run: ./update_bot.sh"
    echo ""
    print_success "Enjoy your Telegram Music Bot! 🎵"
}

# Run main function
main "$@"