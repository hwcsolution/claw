#!/bin/bash

# GitHub Token Configuration Script
# This script helps configure Git to use GitHub Personal Access Tokens

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Display GitHub token creation instructions
show_token_instructions() {
    echo ""
    echo "========================================"
    echo "    GitHub Personal Access Token Setup"
    echo "========================================"
    echo ""
    log_info "Follow these steps to create a GitHub Personal Access Token:"
    echo ""
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
    echo "3. Give your token a descriptive name (e.g., 'My Computer')"
    echo "4. Select expiration:"
    echo "   - Recommended: 90 days (or custom duration)"
    echo "   - For automation: No expiration (use with caution)"
    echo "5. Select scopes (permissions):"
    echo "   - ✅ repo (Full control of private repositories)"
    echo "   - ✅ workflow (Update GitHub Action workflows)"
    echo "   - ✅ write:packages (Upload packages to GitHub Packages)"
    echo "   - ✅ delete:packages (Delete packages from GitHub Packages)"
    echo "   - ✅ admin:org (Full control of orgs and teams)"
    echo "   - ✅ admin:public_key (Full control of user public keys)"
    echo "   - ✅ admin:repo_hook (Full control of repository hooks)"
    echo "   - ✅ admin:org_hook (Full control of organization hooks)"
    echo "   - ✅ gist (Create gists)"
    echo "   - ✅ notifications (Access notifications)"
    echo "   - ✅ user (Update ALL user data)"
    echo "   - ✅ delete_repo (Delete repositories)"
    echo "   - ✅ write:discussion (Read and write team discussions)"
    echo "   - ✅ write:packages (Upload packages to GitHub Packages)"
    echo "   - ✅ read:packages (Download packages from GitHub Packages)"
    echo "   - ✅ delete:packages (Delete packages from GitHub Packages)"
    echo "   - ✅ admin:gpg_key (Full control of GPG keys)"
    echo "6. Click 'Generate token'"
    echo "7. COPY THE TOKEN IMMEDIATELY (you won't see it again!)"
    echo ""
    log_warning "Important: Store your token securely. You won't be able to see it again!"
    echo ""
    read -p "Press Enter when you have your token ready..." dummy
}

# Configure Git with token
configure_git_with_token() {
    local github_username="$1"
    local github_email="$2"
    local github_token="$3"
    
    log_info "Configuring Git with your credentials..."
    
    # Set Git user info
    git config --global user.name "$github_username"
    git config --global user.email "$github_email"
    
    log_success "Git user configured:"
    echo "  Name:  $(git config --global user.name)"
    echo "  Email: $(git config --global user.email)"
    echo ""
    
    # Configure credential helper
    log_info "Setting up Git credential helper..."
    
    echo "Select credential storage method:"
    echo "1. Cache (stores in memory for 15 minutes)"
    echo "2. Store (stores in plain text file - less secure)"
    echo "3. OS keychain (macOS: keychain, Linux: libsecret, Windows: wincred)"
    echo "4. Manual (you'll enter credentials each time)"
    echo ""
    
    read -p "Enter choice (1-4): " credential_choice
    
    case $credential_choice in
        1)
            # Cache credentials
            git config --global credential.helper cache
            git config --global credential.helper 'cache --timeout=900'
            log_success "Credentials will be cached for 15 minutes"
            ;;
        2)
            # Store credentials in plain text
            git config --global credential.helper store
            log_warning "Credentials will be stored in plain text at ~/.git-credentials"
            log_info "Make sure to protect this file with proper permissions"
            ;;
        3)
            # Use OS keychain
            if [[ "$OSTYPE" == "darwin"* ]]; then
                git config --global credential.helper osxkeychain
                log_success "Using macOS Keychain for credential storage"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Try libsecret first, then fallback
                if command -v git-credential-libsecret &> /dev/null; then
                    git config --global credential.helper libsecret
                    log_success "Using libsecret for credential storage"
                else
                    git config --global credential.helper cache
                    log_warning "libsecret not found, using cache instead"
                fi
            else
                git config --global credential.helper store
                log_info "Using store method for your OS"
            fi
            ;;
        4)
            log_info "No credential helper configured. You'll need to enter credentials each time."
            ;;
        *)
            log_warning "Invalid choice, using cache method"
            git config --global credential.helper cache
            git config --global credential.helper 'cache --timeout=900'
            ;;
    esac
    
    # Store token in environment (temporary)
    log_info "To use your token immediately, you can set it as an environment variable:"
    echo ""
    echo "  export GITHUB_TOKEN=\"$github_token\""
    echo ""
    log_info "Or use it directly in Git commands:"
    echo ""
    echo "  git clone https://$github_username:$github_token@github.com/username/repo.git"
    echo ""
    
    # Create a helper script for token usage
    create_token_helper "$github_username" "$github_token"
    
    return 0
}

# Create a helper script for token management
create_token_helper() {
    local github_username="$1"
    local github_token="$2"
    
    helper_script="$HOME/.github_token_helper.sh"
    
    cat > "$helper_script" << EOF
#!/bin/bash
# GitHub Token Helper Script
# Source this file to set up your GitHub token environment

export GITHUB_USERNAME="$github_username"
export GITHUB_TOKEN="$github_token"

# Git remote URL with token
export GITHUB_REMOTE_URL="https://\${GITHUB_USERNAME}:\${GITHUB_TOKEN}@github.com"

# Function to clone with token
gh_clone() {
    if [ -z "\$1" ]; then
        echo "Usage: gh_clone username/repo"
        return 1
    fi
    git clone "https://\${GITHUB_USERNAME}:\${GITHUB_TOKEN}@github.com/\$1.git"
}

# Function to set remote URL with token
gh_set_remote() {
    if [ -z "\$1" ]; then
        echo "Usage: gh_set_remote username/repo"
        return 1
    fi
    git remote set-url origin "https://\${GITHUB_USERNAME}:\${GITHUB_TOKEN}@github.com/\$1.git"
}

echo "GitHub token helper loaded for user: \$GITHUB_USERNAME"
echo "Available functions: gh_clone, gh_set_remote"
EOF
    
    chmod +x "$helper_script"
    
    log_info "Created token helper script: $helper_script"
    log_info "To use it: source $helper_script"
    echo ""
}

# Test GitHub API access
test_github_api() {
    local github_token="$1"
    
    if [ -z "$github_token" ]; then
        log_warning "No token provided for API test"
        return 1
    fi
    
    log_info "Testing GitHub API access..."
    
    # Test with curl
    response=$(curl -s -H "Authorization: token $github_token" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user)
    
    if echo "$response" | grep -q '"login"'; then
        username=$(echo "$response" | grep '"login"' | head -1 | cut -d'"' -f4)
        log_success "✅ GitHub API access successful!"
        log_success "Authenticated as: $username"
        return 0
    else
        log_error "GitHub API test failed"
        log_info "Response: $response"
        return 1
    fi
}

# Main function
main() {
    echo ""
    echo "========================================"
    echo "    GitHub Token Configuration"
    echo "========================================"
    echo ""
    
    # Show instructions first
    show_token_instructions
    
    # Get user input
    echo ""
    read -p "Enter your GitHub username: " github_username
    read -p "Enter your GitHub email: " github_email
    read -p "Enter your GitHub Personal Access Token: " github_token
    
    if [ -z "$github_username" ] || [ -z "$github_email" ] || [ -z "$github_token" ]; then
        log_error "All fields are required."
        exit 1
    fi
    
    # Configure Git
    if configure_git_with_token "$github_username" "$github_email" "$github_token"; then
        log_success "Git configuration completed!"
    else
        log_error "Git configuration failed."
        exit 1
    fi
    
    # Test API access
    if test_github_api "$github_token"; then
        log_success "GitHub authentication verified!"
    else
        log_warning "GitHub API test failed. Please verify your token has correct permissions."
    fi
    
    # Display usage instructions
    echo ""
    log_info "Usage Instructions:"
    echo "====================="
    log_info "1. To clone a repository:"
    echo "   git clone https://$github_username:$github_token@github.com/username/repo.git"
    echo ""
    log_info "2. To push to an existing repository:"
    echo "   git push"
    echo "   (Git will use your cached credentials)"
    echo ""
    log_info "3. To set remote URL for an existing repo:"
    echo "   git remote set-url origin https://$github_username:$github_token@github.com/username/repo.git"
    echo ""
    log_info "4. For automated scripts, use the token helper:"
    echo "   source $HOME/.github_token_helper.sh"
    echo "   gh_clone username/repo"
    echo ""
    log_warning "Security Note:"
    echo "================"
    log_warning "• Never commit your token to version control"
    log_warning "• Use environment variables or credential helpers"
    log_warning "• Regularly rotate your tokens (every 90 days recommended)"
    log_warning "• Use fine-grained tokens with minimal permissions when possible"
    echo ""
    log_success "Setup complete! You can now use Git with GitHub using your token."
}

# Run main function
main "$@"