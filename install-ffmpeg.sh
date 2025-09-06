#!/bin/bash

# FFmpeg Installation Script for Telegram Music Bot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if running as root for system installations
if [[ $EUID -eq 0 ]]; then
    IS_ROOT=true
else
    IS_ROOT=false
fi

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
        elif [ -f /etc/fedora-release ]; then
            OS="fedora"
        else
            OS="linux_unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    print_info "Detected OS: $OS"
}

# Install FFmpeg on Debian/Ubuntu
install_ffmpeg_debian() {
    print_info "Installing FFmpeg on Debian/Ubuntu..."
    
    if [ "$IS_ROOT" = true ]; then
        apt update
        apt install -y ffmpeg
    else
        sudo apt update
        sudo apt install -y ffmpeg
    fi
    
    # Verify installation
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed successfully"
        ffmpeg -version | head -n 1
    else
        print_error "FFmpeg installation failed"
        return 1
    fi
}

# Install FFmpeg on RedHat/CentOS
install_ffmpeg_redhat() {
    print_info "Installing FFmpeg on RedHat/CentOS..."
    
    if [ "$IS_ROOT" = true ]; then
        yum install -y epel-release
        yum install -y ffmpeg
    else
        sudo yum install -y epel-release
        sudo yum install -y ffmpeg
    fi
    
    # Verify installation
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed successfully"
        ffmpeg -version | head -n 1
    else
        print_error "FFmpeg installation failed"
        return 1
    fi
}

# Install FFmpeg on Fedora
install_ffmpeg_fedora() {
    print_info "Installing FFmpeg on Fedora..."
    
    if [ "$IS_ROOT" = true ]; then
        dnf install -y ffmpeg
    else
        sudo dnf install -y ffmpeg
    fi
    
    # Verify installation
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed successfully"
        ffmpeg -version | head -n 1
    else
        print_error "FFmpeg installation failed"
        return 1
    fi
}

# Install FFmpeg on Arch Linux
install_ffmpeg_arch() {
    print_info "Installing FFmpeg on Arch Linux..."
    
    if [ "$IS_ROOT" = true ]; then
        pacman -Syu --noconfirm ffmpeg
    else
        sudo pacman -Syu --noconfirm ffmpeg
    fi
    
    # Verify installation
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed successfully"
        ffmpeg -version | head -n 1
    else
        print_error "FFmpeg installation failed"
        return 1
    fi
}

# Install FFmpeg on macOS
install_ffmpeg_macos() {
    print_info "Installing FFmpeg on macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed. Please install Homebrew first:"
        print_error "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        return 1
    fi
    
    # Install FFmpeg using Homebrew
    brew install ffmpeg
    
    # Verify installation
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg installed successfully"
        ffmpeg -version | head -n 1
    else
        print_error "FFmpeg installation failed"
        return 1
    fi
}

# Install FFmpeg on Windows
install_ffmpeg_windows() {
    print_error "Windows installation not supported by this script."
    print_error "Please download FFmpeg from https://ffmpeg.org/download.html"
    print_error "And add it to your system PATH"
    return 1
}

# Download static FFmpeg binaries
download_static_ffmpeg() {
    print_info "Downloading static FFmpeg binaries..."
    
    # Create directory for static binaries
    mkdir -p ffmpeg_static
    cd ffmpeg_static
    
    # Detect architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" ]]; then
        ARCH="amd64"
    elif [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "aarch64" ]]; then
        ARCH="arm64"
    elif [[ "$ARCH" == "armv7l" ]]; then
        ARCH="armhf"
    else
        print_error "Unsupported architecture: $ARCH"
        return 1
    fi
    
    # Download static build
    if [[ "$OS" == "linux" ]]; then
        URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-${ARCH}-static.tar.xz"
        print_info "Downloading from: $URL"
        
        if command -v wget &> /dev/null; then
            wget -q "$URL" -O ffmpeg.tar.xz
        elif command -v curl &> /dev/null; then
            curl -s "$URL" -o ffmpeg.tar.xz
        else
            print_error "Neither wget nor curl is available"
            return 1
        fi
        
        # Extract
        tar -xf ffmpeg.tar.xz
        rm ffmpeg.tar.xz
        
        # Find the extracted directory
        EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "ffmpeg-*" | head -n 1)
        
        if [[ -n "$EXTRACTED_DIR" ]]; then
            cd "$EXTRACTED_DIR"
            
            # Move binaries to /usr/local/bin (or ~/.local/bin for non-root)
            if [ "$IS_ROOT" = true ]; then
                mv ffmpeg ffprobe /usr/local/bin/
            else
                mkdir -p ~/.local/bin
                mv ffmpeg ffprobe ~/.local/bin/
                
                # Add ~/.local/bin to PATH if not already there
                if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
                    print_warning "Added ~/.local/bin to PATH. Please restart your shell or run: source ~/.bashrc"
                fi
            fi
            
            cd ../..
            rm -rf ffmpeg_static
            
            print_success "Static FFmpeg binaries installed successfully"
            return 0
        else
            print_error "Failed to extract FFmpeg binaries"
            return 1
        fi
    else
        print_error "Static builds are only available for Linux"
        return 1
    fi
}

# Test FFmpeg functionality
test_ffmpeg() {
    print_info "Testing FFmpeg functionality..."
    
    if ! command -v ffmpeg &> /dev/null; then
        print_error "FFmpeg not found in PATH"
        return 1
    fi
    
    # Test basic functionality
    if ffmpeg -version > /dev/null 2>&1; then
        print_success "FFmpeg is working correctly"
        ffmpeg -version | head -n 1
        return 0
    else
        print_error "FFmpeg is not working correctly"
        return 1
    fi
}

# Main installation function
main() {
    echo "================================================"
    echo "  FFmpeg Installation Script for Telegram Music Bot"
    echo "================================================"
    echo ""
    
    # Detect operating system
    detect_os
    
    # Check if FFmpeg is already installed
    if command -v ffmpeg &> /dev/null; then
        print_success "FFmpeg is already installed!"
        ffmpeg -version | head -n 1
        echo ""
        
        read -p "Do you want to reinstall FFmpeg? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled"
            exit 0
        fi
    fi
    
    # Try to install based on OS
    case $OS in
        "debian")
            install_ffmpeg_debian
            ;;
        "redhat")
            install_ffmpeg_redhat
            ;;
        "fedora")
            install_ffmpeg_fedora
            ;;
        "arch")
            install_ffmpeg_arch
            ;;
        "macos")
            install_ffmpeg_macos
            ;;
        "windows")
            install_ffmpeg_windows
            ;;
        *)
            print_warning "Unsupported operating system: $OS"
            print_info "Trying to download static binaries..."
            if ! download_static_ffmpeg; then
                print_error "Failed to install FFmpeg"
                print_error "Please install FFmpeg manually and try again"
                exit 1
            fi
            ;;
    esac
    
    # Test installation
    if test_ffmpeg; then
        echo ""
        print_success "FFmpeg installation completed successfully!"
        print_info "You can now run your Telegram Music Bot with full functionality"
    else
        echo ""
        print_error "FFmpeg installation failed or is not working properly"
        print_error "Please check the installation logs and try again"
        exit 1
    fi
}

# Run main function
main "$@"