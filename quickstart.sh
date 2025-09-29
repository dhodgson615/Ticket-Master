#!/bin/bash

# Ticket-Master Quickstart Script
# AI-powered GitHub issue generator
# 
# This script automates the setup process for Ticket-Master after cloning.
# It installs dependencies, creates configuration, and helps set up GitHub token.

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

print_header() {
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}    Ticket-Master Quickstart Setup${NC}"
    echo -e "${GREEN}    AI-powered GitHub Issue Generator${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python 3
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed."
        print_info "Please install Python 3.9 or higher and try again."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_info "Found Python $python_version"
    
    # Check pip3
    if ! command_exists pip3; then
        print_error "pip3 is required but not installed."
        print_info "Please install pip3 and try again."
        exit 1
    fi
    
    # Check Make
    if ! command_exists make; then
        print_error "Make is required but not installed."
        print_info "Please install make and try again."
        exit 1
    fi
    
    # Check Git
    if ! command_exists git; then
        print_error "Git is required but not installed."
        print_info "Please install git and try again."
        exit 1
    fi
    
    print_success "All system requirements satisfied"
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing Python dependencies and setting up configuration..."
    
    if make setup; then
        print_success "Dependencies installed and configuration created successfully"
    else
        print_error "Failed to install dependencies"
        print_info "You can try running 'make setup' manually to see detailed error messages"
        exit 1
    fi
}

# Function to setup GitHub token
setup_github_token() {
    echo ""
    print_info "Setting up GitHub Personal Access Token..."
    
    if [ -n "$GITHUB_TOKEN" ]; then
        print_success "GITHUB_TOKEN environment variable is already set"
        return 0
    fi
    
    echo ""
    echo "You need a GitHub Personal Access Token to use Ticket-Master."
    echo "This token allows the application to create issues in your repositories."
    echo ""
    echo "To create a token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Give it a descriptive name like 'Ticket-Master'"
    echo "4. Select scopes: 'repo' (for private repos) or 'public_repo' (for public repos only)"
    echo "5. Click 'Generate token' and copy the token"
    echo ""
    
    read -p "Do you want to set your GitHub token now? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -s -p "Enter your GitHub Personal Access Token: " token
        echo ""
        
        if [ -n "$token" ]; then
            export GITHUB_TOKEN="$token"
            
            # Add to shell profile for persistence
            shell_profile=""
            if [ -f "$HOME/.bashrc" ]; then
                shell_profile="$HOME/.bashrc"
            elif [ -f "$HOME/.zshrc" ]; then
                shell_profile="$HOME/.zshrc"
            elif [ -f "$HOME/.profile" ]; then
                shell_profile="$HOME/.profile"
            fi
            
            if [ -n "$shell_profile" ]; then
                echo "export GITHUB_TOKEN=\"$token\"" >> "$shell_profile"
                print_success "GitHub token added to $shell_profile"
                print_info "Remember to run 'source $shell_profile' or restart your terminal"
            else
                print_warning "Could not determine shell profile. You may need to set GITHUB_TOKEN manually"
                print_info "Add this to your shell profile: export GITHUB_TOKEN=\"$token\""
            fi
        else
            print_warning "No token entered. You can set it later with:"
            print_info "export GITHUB_TOKEN=\"your_token_here\""
        fi
    else
        print_info "You can set your GitHub token later with:"
        print_info "export GITHUB_TOKEN=\"your_token_here\""
    fi
}

# Function to run validation test
validate_setup() {
    print_info "Validating setup..."
    
    # Test basic functionality
    if python3 main.py --help >/dev/null 2>&1; then
        print_success "Ticket-Master CLI is working correctly"
    else
        print_error "Ticket-Master CLI validation failed"
        return 1
    fi
    
    # Test configuration validation
    if python3 main.py validate-config >/dev/null 2>&1; then
        print_success "Configuration validation passed"
    else
        print_warning "Configuration validation had issues (this is normal without GITHUB_TOKEN)"
    fi
    
    return 0
}

# Function to show next steps
show_next_steps() {
    echo ""
    print_success "Quickstart setup completed successfully!"
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo ""
    echo "1. ${BLUE}Set your GitHub token (if not done already):${NC}"
    echo "   export GITHUB_TOKEN=\"your_github_personal_access_token\""
    echo ""
    echo "2. ${BLUE}Test with a dry run:${NC}"
    echo "   python3 main.py owner/repo --dry-run"
    echo ""
    echo "3. ${BLUE}Generate real issues:${NC}"
    echo "   python3 main.py owner/repo"
    echo ""
    echo "4. ${BLUE}Start the web interface:${NC}"
    echo "   python3 app.py"
    echo ""
    echo "5. ${BLUE}View all available commands:${NC}"
    echo "   make help"
    echo ""
    echo -e "${GREEN}Documentation:${NC}"
    echo "• README.md - Complete installation and usage guide"
    echo "• docs/CURRENT_FUNCTIONALITY.md - Feature overview"
    echo "• config.yaml - Configuration options"
    echo ""
    echo -e "${GREEN}Need help?${NC} Visit: https://github.com/dhodgson615/Ticket-Master"
    echo ""
}

# Main execution
main() {
    print_header
    
    # Verify we're in the right directory first
    if [ ! -f "main.py" ] || [ ! -f "Makefile" ]; then
        print_error "This script should be run from the Ticket-Master root directory"
        print_info "Make sure you're in the directory containing main.py and Makefile"
        print_info "Current directory: $(pwd)"
        exit 1
    fi
    
    # Check requirements
    check_requirements
    
    # Install dependencies
    install_dependencies
    
    # Setup GitHub token
    setup_github_token
    
    # Validate setup
    validate_setup
    
    # Show next steps
    show_next_steps
}

# Handle command line arguments
case "${1:-}" in
    -h|--help)
        echo "Ticket-Master Quickstart Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  -h, --help     Show this help message"
        echo "  --skip-token   Skip GitHub token setup"
        echo ""
        echo "This script automates the setup process for Ticket-Master."
        echo "It will install dependencies, create configuration, and help set up your GitHub token."
        exit 0
        ;;
    --skip-token)
        SKIP_TOKEN=1
        ;;
    "")
        # No arguments, proceed normally
        ;;
    *)
        print_error "Unknown argument: $1"
        print_info "Use --help for usage information"
        exit 1
        ;;
esac

# Override token setup if requested
if [ "${SKIP_TOKEN:-}" = "1" ]; then
    setup_github_token() {
        print_info "Skipping GitHub token setup (--skip-token specified)"
    }
fi

# Run main function
main