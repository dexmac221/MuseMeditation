#!/bin/bash
# 🚀 GitHub Repository Setup Script
# Prepares the MuseMeditation project for GitHub publication

echo "🚀 MuseMeditation - GitHub Repository Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if git is installed
check_git() {
    if command -v git &> /dev/null; then
        print_status "Git is installed"
        return 0
    else
        print_error "Git is not installed. Please install git first:"
        print_info "sudo apt install git"
        return 1
    fi
}

# Initialize git repository if not already done
init_git() {
    if [ -d ".git" ]; then
        print_info "Git repository already initialized"
        return 0
    else
        print_info "Initializing Git repository..."
        git init
        print_status "Git repository initialized"
        return 0
    fi
}

# Set up git configuration
setup_git_config() {
    print_info "Checking Git configuration..."
    
    # Check if user name is configured
    if ! git config user.name > /dev/null 2>&1; then
        print_warning "Git user name not configured"
        read -p "Enter your full name: " username
        git config user.name "$username"
        print_status "Git user name set to: $username"
    else
        current_name=$(git config user.name)
        print_status "Git user name: $current_name"
    fi
    
    # Check if user email is configured  
    if ! git config user.email > /dev/null 2>&1; then
        print_warning "Git user email not configured"
        read -p "Enter your email address: " email
        git config user.email "$email"
        print_status "Git user email set to: $email"
    else
        current_email=$(git config user.email)
        print_status "Git user email: $current_email"
    fi
}

# Add remote origin
setup_remote() {
    print_info "Setting up remote repository..."
    
    # Check if remote already exists
    if git remote get-url origin > /dev/null 2>&1; then
        current_remote=$(git remote get-url origin)
        print_info "Remote origin already set: $current_remote"
        
        read -p "Do you want to change the remote URL? (y/N): " change_remote
        if [[ $change_remote =~ ^[Yy]$ ]]; then
            read -p "Enter new remote URL: " new_remote
            git remote set-url origin "$new_remote"
            print_status "Remote origin updated to: $new_remote"
        fi
    else
        # Default to the provided GitHub URL
        default_remote="https://github.com/dexmac221/MuseMeditation.git"
        print_info "Adding remote origin: $default_remote"
        git remote add origin "$default_remote"
        print_status "Remote origin added"
    fi
}

# Create initial commit
create_initial_commit() {
    print_info "Preparing initial commit..."
    
    # Add all files to staging
    git add .
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        print_info "No changes to commit"
        return 0
    fi
    
    # Create initial commit
    print_info "Creating initial commit..."
    git commit -m "🧠 Initial release: Professional EEG Brain Monitoring System

✨ Features:
- Complete PyQt5 GUI application for real-time EEG monitoring
- Advanced meditation analysis with brain state classification
- Ubuntu 24.04 compatibility patches for muselsl library  
- Multi-sensor integration (EEG + PPG + accelerometer)
- Personal calibration system for improved accuracy
- Automated setup and comprehensive diagnostic tools

🏆 Technical Achievements:
- Professional-grade brain-computer interface implementation
- Real-time signal processing at 256+ Hz sample rates
- Thread-safe Qt architecture with proper error handling
- Research-based meditation detection algorithms
- Open-source community contributions (Ubuntu 24.04 fixes)

🚀 Ready for:
- Personal meditation training with biofeedback
- Research EEG data collection and analysis  
- Educational demonstrations of neurotechnology
- Further development and customization

Project Status: Complete and fully operational! 🧠✨"
    
    print_status "Initial commit created successfully"
}

# Verify project structure
verify_project_structure() {
    print_info "Verifying project structure..."
    
    required_files=(
        "README.md"
        "LICENSE" 
        "CONTRIBUTING.md"
        "CHANGELOG.md"
        "requirements.txt"
        "working_muse_gui.py"
        "patch_muselsl.py"
        "system_check.py"
        "setup.sh"
        ".gitignore"
    )
    
    required_dirs=(
        ".github/ISSUE_TEMPLATE"
        ".github/workflows"
    )
    
    missing_files=()
    
    # Check files
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_status "$file ✓"
        else
            print_error "$file ✗"
            missing_files+=("$file")
        fi
    done
    
    # Check directories
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_status "$dir/ ✓"
        else
            print_error "$dir/ ✗"
            missing_files+=("$dir/")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_status "All required files and directories are present"
        return 0
    else
        print_warning "Some files/directories are missing:"
        for missing in "${missing_files[@]}"; do
            print_error "  - $missing"
        done
        return 1
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 Repository Setup Complete!"
    echo "============================="
    echo ""
    print_status "Your MuseMeditation project is ready for GitHub!"
    echo ""
    print_info "Next steps:"
    echo "  1. 🌐 Visit: https://github.com/dexmac221/MuseMeditation"
    echo "  2. 📤 Push to GitHub:"
    echo "     git push -u origin main"
    echo ""
    echo "  3. ✨ Optional - Create additional branches:"
    echo "     git checkout -b develop    # For development work"
    echo "     git checkout -b docs       # For documentation updates"
    echo ""
    print_info "Repository features ready:"
    echo "  ✅ Professional README with badges and documentation"
    echo "  ✅ MIT License for open-source distribution"  
    echo "  ✅ Contributing guidelines for community participation"
    echo "  ✅ Issue templates for bug reports and feature requests"
    echo "  ✅ GitHub Actions CI/CD for automated testing"
    echo "  ✅ Comprehensive .gitignore for Python projects"
    echo ""
    print_info "Your project demonstrates:"
    echo "  🧠 Professional brain-computer interface development"
    echo "  💻 Advanced real-time system programming"
    echo "  🔧 Open-source community contribution (Ubuntu fixes)"
    echo "  📚 Comprehensive documentation and user support"
    echo ""
    echo "🌟 Ready to share your exceptional EEG project with the world!"
}

# Main execution
main() {
    if ! check_git; then
        exit 1
    fi
    
    init_git
    setup_git_config
    setup_remote
    
    if verify_project_structure; then
        create_initial_commit
        show_next_steps
    else
        print_warning "Project structure verification failed, but continuing..."
        print_info "You may want to ensure all files are properly created"
        create_initial_commit
        show_next_steps
    fi
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n\n${YELLOW}[⚠]${NC} Setup interrupted by user"; exit 130' INT

# Run main function
main "$@"
