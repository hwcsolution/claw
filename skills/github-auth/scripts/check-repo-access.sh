#!/bin/bash

# GitHub Repository Access Check Script
# This script checks if the user has access to a GitHub repository

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

# Check SSH access to repository
check_ssh_access() {
    local repo_url="$1"
    
    log_info "Checking SSH access to repository: $repo_url"
    
    # Extract repo path from URL
    if [[ "$repo_url" == git@github.com:* ]]; then
        repo_path="${repo_url#git@github.com:}"
    elif [[ "$repo_url" == https://github.com/* ]]; then
        repo_path="${repo_url#https://github.com/}"
        repo_path="${repo_path%.git}"
    else
        log_error "Invalid repository URL format. Expected: git@github.com:user/repo.git or https://github.com/user/repo.git"
        return 1
    fi
    
    # Test SSH connection to GitHub
    log_info "Testing SSH connection to GitHub..."
    if ! ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_error "SSH authentication failed. Please check your SSH key setup."
        return 1
    fi
    
    log_success "SSH authentication successful!"
    
    # Try to clone the repository (dry run)
    log_info "Checking repository access..."
    
    # Create a temporary directory
    temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Try to clone with --depth 1 for speed
    if git clone --depth 1 "$repo_url" . 2>/dev/null; then
        log_success "✅ You have read access to the repository: $repo_url"
        
        # Check if we can push (try to get remote info)
        if git remote show origin 2>/dev/null | grep -q "push"; then
            log_success "✅ You appear to have push access to the repository"
            cd /tmp
            rm -rf "$temp_dir"
            return 0
        else
            log_warning "⚠️  You have read access but may not have push access"
            log_info "You might need to be added as a collaborator or have the repository forked."
            cd /tmp
            rm -rf "$temp_dir"
            return 2
        fi
    else
        log_error "❌ You do not have access to the repository: $repo_url"
        log_info "Possible reasons:"
        log_info "1. Repository is private and you're not a collaborator"
        log_info "2. Repository doesn't exist"
        log_info "3. SSH key not added to GitHub account"
        log_info "4. SSH key doesn't have proper permissions"
        cd /tmp
        rm -rf "$temp_dir"
        return 1
    fi
}

# Check HTTPS access to repository
check_https_access() {
    local repo_url="$1"
    local token="${2:-}"
    
    log_info "Checking HTTPS access to repository: $repoRR_url"
    
    # Extract repo path from URL
    if [[ "$repo_url" == https://github.com/* ]]; then
        repo_path="${RR_url#https://github.com/}"
        repo_path="${repo_path%.git}"
    else
        log_error "Invalid HTTPS repository URL format. Expected: https://github.com/user/repo.git"
        return 1
    fi
    
    # Split into user and repo
    IFS='/' read -r user repo <<< "$repo_path"
    
    # Check if repository exists and is accessible
    log_info "Checking repository existence and accessibility..."
    
    if [ -n "$token" ]; then
        # With token
        status_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $token" \
            "https://api.github.com/repos/$user/$repo")
    else
        # Without token (public repos only)
        status_code=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://api.github.com/repos/$user/$repo")
    fi
    
    case $status_code in
        200)
            log_success "✅ Repository exists and is accessible: $repo_url"
            return 0
            ;;
        401|403)
            log_error "❌ Access denied (HTTP $status_code)"
            log_info "You need proper authentication or repository permissions."
            return 1
            ;;
        404)
            log_error "❌ Repository not found (HTTP 404)"
            log_info "Check the repository URL: https://github.com/$user/$repo"
            return 1
            ;;
        *)
            log_error "❌ Unexpected error (HTTP $status_code)"
            return 1
            ;;
    esac
}

# Check repository permissions
check_repo_permissions() {
    local repo_url="$1"
    local method="${2:-ssh}"
    local token="${3:-}"
    
    echo ""
    echo "========================================"
    echo "    Repository Access Check"
    echo "========================================"
    echo ""
    
    log_info "Repository: $repo_url"
    log_info "Method: $method"
    echo ""
    
    case $method in
        ssh)
            check_ssh_access "$repo_url"
            return $?
            ;;
        https)
            check_https_access "$repo_url" "$token"
            return $?
            ;;
        *)
            log_error "Invalid method: $method. Use 'ssh' or 'https'."
            return 1
            ;;
    esac
}

# Suggest solutions for access issues
suggest_solutions() {
    local repo_url="$1"
    
    echo ""
    echo "========================================"
    echo "    Access Issue Solutions"
    echo "========================================"
    echo ""
    
    log_info "If you don't have access to the repository, try these solutions:"
    echo ""
    
    # Extract user and repo from URL
    if [[ "$repo_url" == git@github.com:* ]]; then
        repo_path="${repo_url#git@github.com:}"
        repo_path="${repo_path%.git}"
    elif [[ "$repo_url" == https://github.com/* ]]; then
        repo_path="${repo_url#https://github.com/}"
        repo_path="${repo_path%.git}"
    else
        repo_path="user/repo"
    fi
    
    IFS='/' read -r user repo <<< "$repo_path"
    
    log_info "1. **Fork the repository** (for public repos):"
    echo "   Visit: https://github.com/$user/$repo"
    echo "   Click the 'Fork' button in the top-right corner"
    echo "   Then clone your fork instead"
    echo ""
    
    log_info "2. **Request access** (for private repos):"
    echo "   Ask the repository owner to add you as a collaborator:"
    echo "   Settings → Collaborators → Add people"
    echo ""
    
    log_info "3. **Use HTTPS with Personal Access Token:**"
    echo "   a. Create a PAT: https://github.com/settings/tokens"
    echo "   b. Select 'repo' scope"
    echo "   c. Use URL: https://USERNAME:TOKEN@github.com/$user/$repo.git"
    echo ""
    
    log_info "4. **Check SSH key setup:**"
    echo "   a. Ensure SSH key is added to GitHub: https://github.com/settings/keys"
    echo "   b. Test SSH connection: ssh -T git@github.com"
    echo ""
    
    log_info "5. **Verify repository URL:**"
    echo "   Make sure the repository exists: https://github.com/$user/$repo"
    echo ""
}

# Main function
main() {
    if [ $# -lt 1 ]; then
        echo "Usage: $0 <repository-url> [method] [token]"
        echo ""
        echo "Examples:"
        echo "  $0 git@github.com:user/repo.git"
        echo "  $0 https://github.com/user/repo.git https"
        echo "  $0 https://github.com/user/repo.git https GITHUB_TOKEN"
        echo ""
        echo "Methods:"
        echo "  ssh    - Check SSH access (default)"
        echo "  https  - Check HTTPS access (requires token for private repos)"
        exit 1
    fi
    
    local repo_url="$1"
    local method="${2:-ssh}"
    local token="${3:-}"
    
    # Validate URL
    if [[ ! "$repo_url" =~ ^(git@github.com:|https://github.com/) ]]; then
        log_error "Invalid GitHub repository URL: $repo_url"
        log_info "Valid formats:"
        log_info "  SSH: git@github.com:user/repo.git"
        log_info "  HTTPS: https://github.com/user/repo.git"
        exit 1
    fi
    
    # Run permission check
    if check_repo_permissions "$repo_url" "$method" "$token"; then
        echo ""
        log_success "✅ You have access to the repository!"
        echo ""
        log_info "You can now:"
        log_info "  git clone $repo_url"
        log_info "  git push (if you have write access)"
        exit 0
    else
        echo ""
        log_error "❌ Access check failed"
        suggest_solutions "$repo_url"
        exit 1
    fi
}

# Run main function
main "$@"