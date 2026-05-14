#!/bin/bash

# SSH Key Generation Script for GitHub
# This script generates SSH keys specifically for GitHub authentication

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

# Generate SSH key
generate_ssh_key() {
    local email="$1"
    local key_type="${2:-ed25519}"
    local key_path="$HOME/.ssh/id_${key_type}_github"
    
    log_info "Generating SSH key for GitHub..."
    log_info "Email: $email"
    log_info "Key type: $key_type"
    log_info "Key path: $key_path"
    echo ""
    
    # Create .ssh directory if it doesn't exist
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    
    # Check if key already exists
    if [ -f "$key_path" ]; then
        log_warning "SSH key already exists at: $key_path"
        echo ""
        echo "Existing public key:"
        echo "===================="
        cat "${key_path}.pub"
        echo "===================="
        echo ""
        
        read -p "Do you want to generate a new key? (y/n): " generate_new
        if [[ "$generate_new" != "y" && "$generate_new" != "Y" ]]; then
            log_info "Using existing SSH key."
            return 0
        fi
    fi
    
    # Generate new key
    log_info "Generating new SSH key..."
    case $key_type in
        ed25519)
            ssh-keygen -t ed25519 -C "$email" -f "$key_path" -N ""
            ;;
        rsa)
            ssh-keygen -t rsa -b 4096 -C "$email" -f "$key_path" -N ""
            ;;
        *)
            log_error "Unsupported key type: $key_type"
            return 1
            ;;
    esac
    
    # Set proper permissions
    chmod 600 "$key_path"
    chmod 644 "${key_path}.pub"
    
    log_success "SSH key generated successfully!"
    echo ""
    
    return 0
}

# Add SSH key to SSH agent
add_to_ssh_agent() {
    local key_path="$1"
    
    log_info "Starting SSH agent..."
    
    # Start SSH agent
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    
    # Add key to agent
    log_info "Adding SSH key to agent..."
    if ssh-add "$key_path"; then
        log_success "SSH key added to agent successfully!"
    else
        log_warning "Failed to add SSH key to agent. You may need to add it manually:"
        echo "  ssh-add $key_path"
    fi
    
    # List keys in agent
    log_info "Current SSH keys in agent:"
    ssh-add -l
    echo ""
}

# Configure SSH config for GitHub
configure_ssh_config() {
    local key_path="$1"
    
    log_info "Configuring SSH for GitHub..."
    
    ssh_config="$HOME/.ssh/config"
    
    # Create config file if it doesn't exist
    if [ ! -f "$ssh_config" ]; then
        touch "$ssh_config"
        chmod 600 "$ssh_config"
        log_info "Created SSH config file: $ssh_config"
    fi
    
    # Check if GitHub config already exists
    if grep -q "Host github.com" "$ssh_config"; then
        log_warning "GitHub SSH configuration already exists in $ssh_config"
        echo ""
        echo "Current GitHub configuration:"
        echo "============================="
        grep -A 5 "Host github.com" "$ssh_config"
        echo "============================="
        echo ""
        
        read -p "Do you want to update it? (y/n): " update_config
        if [[ "$update_config" != "y" && "$update_config" != "Y" ]]; then
            log_info "Keeping existing SSH configuration."
            return 0
        fi
        
        # Remove existing GitHub configuration
        sed -i '/^Host github.com/,/^$/d' "$ssh_config"
    fi
    
    # Add new GitHub configuration
    cat >> "$ssh_config" << EOF

Host github.com
    HostName github.com
    User git
    IdentityFile $key_path
    IdentitiesOnly yes
EOF
    
    log_success "SSH config updated for GitHub!"
    echo ""
    log_info "SSH configuration added:"
    echo "==========================="
    tail -6 "$ssh_config"
    echo "==========================="
    echo ""
}

# Display public key
display_public_key() {
    local key_path="$1"
    
    log_success "Your public SSH key for GitHub:"
    echo ""
    echo "=============================================="
    cat "${key_path}.pub"
    echo "=============================================="
    echo ""
    
    log_info "Instructions to add this key to GitHub:"
    echo "1. Go to https://github.com/settings/keys"
    echo "2. Click 'New SSH key'"
    echo "3. Give it a title (e.g., 'My Computer' or 'Work Laptop')"
    echo "4. Paste the ENTIRE public key above into the 'Key' field"
    echo "5. Click 'Add SSH key'"
    echo ""
    log_info "Important: Copy the entire key including the 'ssh-ed25519' or 'ssh-rsa' prefix and the email comment"
}

# Test SSH connection to GitHub
test_ssh_connection() {
    log_info "Testing SSH connection to GitHub..."
    echo ""
    
    # Test connection
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_success "✅ SSH connection to GitHub successful!"
        log_success "You can now use Git with GitHub via SSH."
    else
        log_warning "SSH connection test returned:"
        ssh -T git@github.com 2>&1 | head -5
        echo ""
        log_info "This is normal if you haven't added the SSH key to GitHub yet."
        log_info "After adding the key to GitHub, run: ssh -T git@github.com"
    fi
}

# Main function
main() {
    echo ""
    echo "========================================"
    echo "    GitHub SSH Key Generator"
    echo "========================================"
    echo ""
    
    # Get user input
    read -p "Enter your GitHub email address: " github_email
    
    if [ -z "$github_email" ]; then
        log_error "Email address is required."
        exit 1
    fi
    
    # Select key type
    echo ""
    echo "Select SSH key type:"
    echo "1. ed25519 (Recommended - more secure, faster)"
    echo "2. RSA 4096 (Compatible with older systems)"
    echo ""
    
    read -p "Enter choice (1 or 2): " key_choice
    
    case $key_choice in
        1)
            key_type="ed25519"
            ;;
        2)
            key_type="rsa"
            ;;
        *)
            log_warning "Invalid choice, defaulting to ed25519"
            key_type="ed25519"
            ;;
    esac
    
    # Generate key
    key_path="$HOME/.ssh/id_${key_type}_github"
    
    if ! generate_ssh_key "$github_email" "$key_type"; then
        exit 1
    fi
    
    # Add to SSH agent
    add_to_ssh_agent "$key_path"
    
    # Configure SSH
    configure_ssh_config "$key_path"
    
    # Display public key
    display_public_key "$key_path"
    
    # Test connection
    test_ssh_connection
    
    # Summary
    echo ""
    log_success "Summary:"
    log_info "1. SSH key generated: $key_path"
    log_info "2. Public key displayed above (copy to GitHub)"
    log_info "3. SSH agent configured"
    log_info "4. SSH config updated"
    log_info "5. To use with Git repositories:"
    echo "   git clone git@github.com:username/repo.git"
    echo "   git remote set-url origin git@github.com:username/repo.git"
    echo ""
    log_info "Remember to add the public key to your GitHub account!"
}

# Run main function
main "$@"