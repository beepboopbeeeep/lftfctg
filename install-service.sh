#!/bin/bash

# Systemd Service Installation Script for Telegram Music Bot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SERVICE_NAME="telegram-music-bot"
SERVICE_USER="telegram-bot"
SERVICE_DIR="/opt/telegram-music-bot"

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    exit 1
fi

# Check if bot is already installed
if [ -d "$SERVICE_DIR" ]; then
    print_warning "Bot is already installed in $SERVICE_DIR"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
fi

# Get current directory
CURRENT_DIR=$(pwd)

print_info "Installing Telegram Music Bot as systemd service..."

# Create service user
if ! id "$SERVICE_USER" &>/dev/null; then
    print_info "Creating service user..."
    useradd -r -s /bin/false -d "$SERVICE_DIR" "$SERVICE_USER"
    print_success "Service user created"
else
    print_warning "Service user already exists"
fi

# Create service directory
print_info "Creating service directory..."
mkdir -p "$SERVICE_DIR"
print_success "Service directory created"

# Copy files
print_info "Copying files..."
cp -r "$CURRENT_DIR"/* "$SERVICE_DIR/"
print_success "Files copied"

# Set permissions
print_info "Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$SERVICE_DIR"
chmod +x "$SERVICE_DIR/start_bot.sh"
chmod +x "$SERVICE_DIR/update_bot.sh"
print_success "Permissions set"

# Create systemd service
print_info "Creating systemd service..."
cp "$SERVICE_DIR/telegram-music-bot.service" /etc/systemd/system/
systemctl daemon-reload
print_success "Systemd service created"

# Enable and start service
print_info "Enabling and starting service..."
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
print_success "Service enabled and started"

# Check service status
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_success "Service is running"
else
    print_error "Service failed to start"
    systemctl status "$SERVICE_NAME"
    exit 1
fi

# Create logrotate config
print_info "Creating logrotate configuration..."
cat > /etc/logrotate.d/telegram-music-bot << EOF
$SERVICE_DIR/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
    postrotate
        systemctl reload-or-restart $SERVICE_NAME
    endscript
}
EOF
print_success "Logrotate configuration created"

# Create update script
print_info "Creating update script..."
cat > /usr/local/bin/update-telegram-bot << 'EOF'
#!/bin/bash
SERVICE_DIR="/opt/telegram-music-bot"
cd "$SERVICE_DIR"
sudo -u telegram-bot ./update_bot.sh
EOF
chmod +x /usr/local/bin/update-telegram-bot
print_success "Update script created"

# Create status script
print_info "Creating status script..."
cat > /usr/local/bin/telegram-bot-status << 'EOF'
#!/bin/bash
echo "=== Telegram Music Bot Status ==="
echo ""
echo "Service Status:"
systemctl status telegram-music-bot --no-pager -l
echo ""
echo "Recent Logs:"
journalctl -u telegram-music-bot --no-pager -n 20
echo ""
echo "Disk Usage:"
du -sh /opt/telegram-music-bot/downloads /opt/telegram-music-bot/temp /opt/telegram-music-bot/logs 2>/dev/null || true
EOF
chmod +x /usr/local/bin/telegram-bot-status
print_success "Status script created"

print_success "Installation completed successfully!"
echo ""
print_info "Service Management:"
echo "  Start:    systemctl start $SERVICE_NAME"
echo "  Stop:     systemctl stop $SERVICE_NAME"
echo "  Restart:  systemctl restart $SERVICE_NAME"
echo "  Status:   systemctl status $SERVICE_NAME"
echo "  Logs:     journalctl -u $SERVICE_NAME -f"
echo ""
print_info "Utility Scripts:"
echo "  Update:   update-telegram-bot"
echo "  Status:   telegram-bot-status"
echo ""
print_info "Service Directory: $SERVICE_DIR"
print_success "Enjoy your Telegram Music Bot! 🎵"