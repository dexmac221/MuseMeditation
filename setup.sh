#!/bin/bash
# 🧠 Muse 2 EEG System - Auto Setup Script
# Automated installation and configuration for Ubuntu 24.04

echo "🧠 Muse 2 EEG Brain Monitoring System - Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# Check if running on Ubuntu
check_ubuntu() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]]; then
            print_status "Detected Ubuntu $VERSION_ID"
            return 0
        fi
    fi
    print_warning "This script is optimized for Ubuntu, but continuing anyway..."
    return 1
}

# Check if Python 3.8+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            print_status "Python $python_version is compatible"
            return 0
        else
            print_error "Python 3.8+ required, found $python_version"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Install system packages
install_system_packages() {
    print_info "Installing system packages..."
    
    # Update package list
    sudo apt update > /dev/null 2>&1
    
    # Install required packages
    local packages=("bluetooth" "bluez" "python3-pip" "python3-dev" "python3-venv")
    
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            print_status "$package already installed"
        else
            print_info "Installing $package..."
            if sudo apt install -y "$package" > /dev/null 2>&1; then
                print_status "$package installed"
            else
                print_error "Failed to install $package"
                return 1
            fi
        fi
    done
    
    # Enable and start Bluetooth service
    print_info "Starting Bluetooth service..."
    sudo systemctl enable bluetooth > /dev/null 2>&1
    sudo systemctl start bluetooth > /dev/null 2>&1
    
    if systemctl is-active --quiet bluetooth; then
        print_status "Bluetooth service is running"
    else
        print_warning "Bluetooth service may not be running properly"
    fi
    
    return 0
}

# Install Python packages
install_python_packages() {
    print_info "Installing Python packages..."
    
    # Check if we should use a virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_status "Using existing virtual environment: $VIRTUAL_ENV"
    else
        print_info "Installing packages globally (consider using a virtual environment)"
    fi
    
    # Install packages from requirements.txt
    if [[ -f "requirements.txt" ]]; then
        print_info "Installing from requirements.txt..."
        if pip3 install -r requirements.txt > /dev/null 2>&1; then
            print_status "Python packages installed successfully"
        else
            print_error "Failed to install some Python packages"
            print_info "You may need to run: pip3 install -r requirements.txt"
            return 1
        fi
    else
        print_error "requirements.txt not found"
        return 1
    fi
    
    return 0
}

# Apply muselsl patch
apply_patch() {
    print_info "Applying Ubuntu 24.04 compatibility patch..."
    
    if python3 patch_muselsl.py > /dev/null 2>&1; then
        print_status "muselsl patch applied successfully"
        return 0
    else
        print_error "Failed to apply muselsl patch"
        print_info "You may need to run manually: python3 patch_muselsl.py"
        return 1
    fi
}

# Run system diagnostic
run_diagnostic() {
    print_info "Running system diagnostic..."
    
    if python3 system_check.py; then
        print_status "System diagnostic passed"
        return 0
    else
        print_warning "System diagnostic found some issues"
        print_info "Review the diagnostic output above"
        return 1
    fi
}

# Add user to necessary groups
setup_permissions() {
    print_info "Setting up user permissions..."
    
    # Add user to dialout group for Bluetooth access
    if groups | grep -q "\bdialout\b"; then
        print_status "User already in dialout group"
    else
        sudo usermod -a -G dialout "$USER"
        print_status "Added user to dialout group"
        print_warning "You may need to log out and back in for group changes to take effect"
    fi
    
    return 0
}

# Main installation sequence
main() {
    echo "Starting automated setup..."
    echo ""
    
    # Pre-flight checks
    check_ubuntu
    if ! check_python; then
        print_error "Python requirements not met. Please install Python 3.8+"
        exit 1
    fi
    
    # Installation steps
    if ! install_system_packages; then
        print_error "System package installation failed"
        exit 1
    fi
    
    if ! install_python_packages; then
        print_error "Python package installation failed"
        exit 1
    fi
    
    if ! apply_patch; then
        print_warning "Patch application failed, but continuing..."
    fi
    
    if ! setup_permissions; then
        print_warning "Permission setup had issues, but continuing..."
    fi
    
    echo ""
    print_info "Running final diagnostic..."
    echo ""
    
    if run_diagnostic; then
        echo ""
        echo "🎉 SETUP COMPLETE!"
        echo "=================="
        print_status "All components installed and configured"
        print_status "System diagnostic passed"
        echo ""
        print_info "Ready to use! Try these commands:"
        echo "  python3 working_muse_gui.py  # Launch GUI"
        echo "  python3 test_lsl_working.py  # Test LSL streaming"
        echo "  python3 system_check.py      # Run diagnostic anytime"
        echo ""
    else
        echo ""
        print_warning "Setup completed with some issues"
        print_info "Check the diagnostic output above for details"
        print_info "You may still be able to use the system"
        echo ""
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n\n${YELLOW}[⚠]${NC} Setup interrupted by user"; exit 130' INT

# Run main function
main "$@"
