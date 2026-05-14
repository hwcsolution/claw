#!/bin/bash

# GitHub Remote Connection Script (Enhanced)
# Complete Git operations + GitHub API integration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_ask() { echo -e "${YELLOW}[?]${NC} $1"; }
log_cmd() { echo -e "${CYAN}❯${NC} $1"; }

# Configuration
CONFIG_FILE="${HOME}/.config/github-remote.conf"
mkdir -p "$(dirname "$CONFIG_FILE")"

# Load config
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    fi
    GITHUB_TOKEN="${GITHUB_TOKEN:-${github_token:-}}"
    GIT_USER_NAME="${GIT_USER_NAME:-${git_user_name:-$(git config user.name 2>/dev/null || echo 'OpenClaw Bot')}}"
    GIT_USER_EMAIL="${GIT_USER_EMAIL:-${git_user_email:-$(git config user.email 2>/dev/null || echo 'bot@openclaw.ai')}}"
}

# Save config
save_config() {
    cat > "$CONFIG_FILE" << EOF
github_token="${GITHUB_TOKEN}"
git_user_name="${GIT_USER_NAME}"
git_user_email="${GIT_USER_EMAIL}"
EOF
    log_success "Config saved to $CONFIG_FILE"
}

# Show usage
usage() {
    cat << 'EOF'
GitHub Remote Operations (Enhanced)
===================================

Usage: github-remote.sh <command> [options]

Commands:
  Git Operations:
    clone <repo>                  Clone repository
    push <repo> <files>           Push files (asks about new branch)
    pull [branch]                 Pull latest changes
    branch <name>                 Create/switch branch
    status                        Show working tree status
    log [count]                   Show commit history
    diff [file]                   Show changes

  GitHub API:
    pr <repo> <title>             Create Pull Request
    issue <repo> <title>          Create Issue
    release <repo> <tag>          Create Release
    repos [user]                  List repositories
    info <repo>                   Show repository info

  Configuration:
    config                        Configure settings
    auth                          Check authentication

Options:
  --token TOKEN       GitHub token (or set GITHUB_TOKEN env)
  --branch NAME       Branch name
  --message TEXT      Commit/PR message
  --base NAME         Base branch (default: main)
  --private           Create private repository

Examples:
  # Clone repository
  github-remote.sh clone user/repo

  # Push files (interactive)
  github-remote.sh push user/repo myfile.py

  # Create PR
  github-remote.sh pr user/repo "Add feature" --token ghp_your_token_here

  # Create issue
  github-remote.sh issue user/repo "Bug report" --body "Description"

  # View status
  github-remote.sh status

  # Configure
  github-remote.sh config

EOF
    exit 0
}

# Parse repo URL or owner/repo format
parse_repo() {
    local url="$1"
    if [[ "$url" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
        REPO_OWNER="${BASH_REMATCH[1]}"
        REPO_NAME="${BASH_REMATCH[2]}"
        REPO_FULL="${REPO_OWNER}/${REPO_NAME}"
    elif [[ "$url" =~ ^([^/]+)/([^/]+)$ ]]; then
        REPO_OWNER="${BASH_REMATCH[1]}"
        REPO_NAME="${BASH_REMATCH[2]}"
        REPO_FULL="${REPO_OWNER}/${REPO_NAME}"
    else
        log_error "Invalid repo format: $url"
        log_info "Use: user/repo or https://github.com/user/repo"
        exit 1
    fi
}

# GitHub API helper
github_api() {
    local method="$1"
    local endpoint="$2"
    local data="$3"

    if [ -z "$GITHUB_TOKEN" ]; then
        log_error "GitHub token required"
        log_info "Set with: github-remote.sh config"
        log_info "Or: export GITHUB_TOKEN=xxx"
        return 1
    fi

    local args=("-s" "-X" "$method")
    args+=("-H" "Authorization: token $GITHUB_TOKEN")
    args+=("-H" "Accept: application/vnd.github.v3+json")
    [ -n "$data" ] && args+=("-d" "$data")

    curl "${args[@]}" "https://api.github.com$endpoint"
}

# Command: Configure
cmd_config() {
    log_info "GitHub Remote Configuration"
    echo ""

    log_ask "GitHub Token (for API operations): "
    read -r token
    [ -n "$token" ] && GITHUB_TOKEN="$token"

    log_ask "Git User Name [$GIT_USER_NAME]: "
    read -r name
    [ -n "$name" ] && GIT_USER_NAME="$name"

    log_ask "Git User Email [$GIT_USER_EMAIL]: "
    read -r email
    [ -n "$email" ] && GIT_USER_EMAIL="$email"

    # Configure git
    git config --global user.name "$GIT_USER_NAME"
    git config --global user.email "$GIT_USER_EMAIL"

    save_config
    log_success "Configuration complete!"
}

# Command: Check authentication
cmd_auth() {
    log_info "Checking authentication..."

    # Check SSH
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_success "SSH: Authenticated"
    else
        log_error "SSH: Not configured"
    fi

    # Check Token
    if [ -n "$GITHUB_TOKEN" ]; then
        local user=$(github_api GET /user | grep '"login"' | cut -d'"' -f4)
        if [ -n "$user" ]; then
            log_success "Token: Authenticated as $user"
        else
            log_error "Token: Invalid or expired"
        fi
    else
        log_error "Token: Not set"
    fi
}

# Command: Clone
cmd_clone() {
    local repo="$1"
    [ -z "$repo" ] && { log_error "Repository required"; exit 1; }

    parse_repo "$repo"
    log_info "Cloning $REPO_FULL..."

    # Try SSH first, then HTTPS
    if git clone "git@github.com:$REPO_FULL.git" 2>/dev/null; then
        log_success "Cloned via SSH"
    elif git clone "https://github.com/$REPO_FULL.git" 2>/dev/null; then
        log_success "Cloned via HTTPS"
    else
        log_error "Failed to clone"
        log_info "Check if repository exists and you have access"
        exit 1
    fi

    cd "$REPO_NAME"
    log_info "Repository ready in: $(pwd)"
}

# Command: Push
cmd_push() {
    local repo="$1"
    local files="$2"
    local new_branch=""
    local message=""

    [ -z "$repo" ] && { log_error "Repository required"; exit 1; }
    [ -z "$files" ] && { log_error "Files required"; exit 1; }

    # Parse options
    shift 2
    while [[ $# -gt 0 ]]; do
        case $1 in
            --branch) new_branch="$2"; shift 2 ;;
            --message) message="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    parse_repo "$repo"

    # Setup work directory
    local work_dir=$(mktemp -d)
    trap "rm -rf $work_dir" EXIT

    log_info "Cloning $REPO_FULL..."
    if ! git clone "git@github.com:$REPO_FULL.git" "$work_dir" 2>/dev/null && \
       ! git clone "https://github.com/$REPO_FULL.git" "$work_dir" 2>/dev/null; then
        log_error "Failed to clone"
        exit 1
    fi

    cd "$work_dir"

    # Ask about new branch
    if [ -z "$new_branch" ]; then
        log_ask "Create new branch? (y/n) [y]: "
        read -r answer
        if [[ "$answer" =~ ^[Yy] ]] || [ -z "$answer" ]; then
            log_ask "Branch name: "
            read -r new_branch
            [ -z "$new_branch" ] && new_branch="feature/$(date +%Y%m%d-%H%M%S)"
        fi
    fi

    # Create branch
    if [ -n "$new_branch" ]; then
        log_info "Creating branch: $new_branch"
        git checkout -b "$new_branch" 2>/dev/null || git checkout "$new_branch"
    fi

    # Add files
    log_info "Adding files..."
    if [ -f "$files" ]; then
        cp "$files" .
        git add "$(basename "$files")"
    elif [ -d "$files" ]; then
        cp -r "$files"/* . 2>/dev/null || cp -r "$files" .
        git add .
    else
        git add "$files"
    fi

    # Show changes
    log_cmd "Changes to commit:"
    git diff --cached --stat

    # Commit
    [ -z "$message" ] && message="Add files: $(git diff --cached --name-only | tr '\n' ' ')"
    log_info "Committing: $message"
    git commit -m "$message"

    # Push
    local current_branch=$(git branch --show-current)
    log_info "Pushing to: $current_branch"
    git push -u origin "$current_branch"

    log_success "Pushed successfully!"
    log_info "Branch: $current_branch"
    log_info "Commit: $(git rev-parse --short HEAD)"
}

# Command: Pull
cmd_pull() {
    local branch="${1:-$(git branch --show-current 2>/dev/null || echo 'main')}"
    log_info "Pulling from: $branch"
    git pull origin "$branch"
    log_success "Pulled successfully"
}

# Command: Branch
cmd_branch() {
    local name="$1"
    [ -z "$name" ] && { git branch -a; return; }

    if git show-ref --verify --quiet "refs/heads/$name"; then
        log_info "Switching to: $name"
        git checkout "$name"
    else
        log_info "Creating branch: $name"
        git checkout -b "$name"
    fi
    log_success "Current branch: $name"
}

# Command: Status
cmd_status() {
    log_cmd "Git Status"
    git status -sb
    echo ""
    if [ -n "$(git diff --stat)" ]; then
        log_cmd "Unstaged changes:"
        git diff --stat
    fi
    if [ -n "$(git diff --cached --stat)" ]; then
        log_cmd "Staged changes:"
        git diff --cached --stat
    fi
}

# Command: Log
cmd_log() {
    local count="${1:-10}"
    log_cmd "Last $count commits:"
    git log --oneline --graph --decorate -n "$count"
}

# Command: Diff
cmd_diff() {
    local file="$1"
    if [ -n "$file" ]; then
        git diff "$file"
    else
        git diff
    fi
}

# Command: Create PR
cmd_pr() {
    local repo="$1"
    local title="$2"
    local base="main"
    local body=""

    [ -z "$repo" ] && { log_error "Repository required"; exit 1; }
    [ -z "$title" ] && { log_error "PR title required"; exit 1; }

    shift 2
    while [[ $# -gt 0 ]]; do
        case $1 in
            --base) base="$2"; shift 2 ;;
            --body) body="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    parse_repo "$repo"

    local head=$(git branch --show-current)
    [ -z "$body" ] && body="## Changes\n\nFrom branch: \`$head\`\n\n---\n*Created by GitHub Remote Skill*"

    log_info "Creating PR: $head → $base"

    local json="{\"title\":\"$title\",\"body\":\"$body\",\"head\":\"$head\",\"base\":\"$base\"}"
    local response=$(github_api POST "/repos/$REPO_FULL/pulls" "$json")

    if echo "$response" | grep -q '"html_url"'; then
        local pr_url=$(echo "$response" | grep '"html_url"' | head -1 | cut -d'"' -f4)
        local pr_num=$(echo "$response" | grep '"number"' | head -1 | cut -d':' -f2 | tr -d ', ')
        log_success "PR #$pr_num created!"
        log_info "$pr_url"
    else
        log_error "Failed to create PR"
        echo "$response" | grep -E '(message|error)' || echo "$response"
        exit 1
    fi
}

# Command: Create Issue
cmd_issue() {
    local repo="$1"
    local title="$2"
    local body=""

    [ -z "$repo" ] && { log_error "Repository required"; exit 1; }
    [ -z "$title" ] && { log_error "Issue title required"; exit 1; }

    shift 2
    while [[ $# -gt 0 ]]; do
        case $1 in
            --body) body="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    parse_repo "$repo"

    log_info "Creating issue: $title"

    local json="{\"title\":\"$title\",\"body\":\"$body\"}"
    local response=$(github_api POST "/repos/$REPO_FULL/issues" "$json")

    if echo "$response" | grep -q '"html_url"'; then
        local issue_url=$(echo "$response" | grep '"html_url"' | head -1 | cut -d'"' -f4)
        local issue_num=$(echo "$response" | grep '"number"' | head -1 | cut -d':' -f2 | tr -d ', ')
        log_success "Issue #$issue_num created!"
        log_info "$issue_url"
    else
        log_error "Failed to create issue"
        exit 1
    fi
}

# Command: Create Release
cmd_release() {
    local repo="$1"
    local tag="$2"
    local name="${3:-Release $tag}"
    local body=""

    [ -z "$repo" ] && { log_error "Repository required"; exit 1; }
    [ -z "$tag" ] && { log_error "Tag required"; exit 1; }

    shift 3
    while [[ $# -gt 0 ]]; do
        case $1 in
            --body) body="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    parse_repo "$repo"

    log_info "Creating release: $tag"

    local json="{\"tag_name\":\"$tag\",\"name\":\"$name\",\"body\":\"$body\"}"
    local response=$(github_api POST "/repos/$REPO_FULL/releases" "$json")

    if echo "$response" | grep -q '"html_url"'; then
        local release_url=$(echo "$response" | grep '"html_url"' | head -1 | cut -d'"' -f4)
        log_success "Release created: $tag"
        log_info "$release_url"
    else
        log_error "Failed to create release"
        exit 1
    fi
}

# Command: List Repos
cmd_repos() {
    local user="${1:-}"
    local endpoint="/user/repos"

    [ -n "$user" ] && endpoint="/users/$user/repos"

    log_info "Fetching repositories..."

    local response=$(github_api GET "$endpoint?per_page=100")

    echo "$response" | grep -E '"full_name"|"description"|"private"' | \
        paste - - - | \
        while read -r line; do
            local name=$(echo "$line" | grep '"full_name"' | cut -d'"' -f4)
            local desc=$(echo "$line" | grep '"description"' | cut -d'"' -f4)
            local private=$(echo "$line" | grep '"private"' | grep -q 'true' && echo "🔒" || echo "🌐")
            echo "$private $name - ${desc:-No description}"
        done
}

# Command: Repo Info
cmd_info() {
    local repo="$1"
    [ -z "$repo" ] && { log_error "Repository required"; exit 1; }

    parse_repo "$repo"

    log_info "Fetching repository info..."

    local response=$(github_api GET "/repos/$REPO_FULL")

    local name=$(echo "$response" | grep '"full_name"' | cut -d'"' -f4)
    local desc=$(echo "$response" | grep '"description"' | head -1 | cut -d'"' -f4)
    local stars=$(echo "$response" | grep '"stargazers_count"' | cut -d':' -f2 | tr -d ', ')
    local forks=$(echo "$response" | grep '"forks_count"' | cut -d':' -f2 | tr -d ', ')
    local issues=$(echo "$response" | grep '"open_issues_count"' | cut -d':' -f2 | tr -d ', ')
    local lang=$(echo "$response" | grep '"language"' | cut -d'"' -f4)
    local url=$(echo "$response" | grep '"html_url"' | head -1 | cut -d'"' -f4)

    cat << EOF

📦 $name
   ${desc:-No description}

📊 Stats:
   ⭐ Stars: $stars
   🍴 Forks: $forks
   🐛 Issues: $issues
   💻 Language: ${lang:-Unknown}

🔗 URL: $url

EOF
}

# Main
load_config

[ $# -lt 1 ] && usage

case "$1" in
    # Git operations
    clone) cmd_clone "$2" ;;
    push) cmd_push "$2" "$3" "${@:4}" ;;
    pull) cmd_pull "$2" ;;
    branch) cmd_branch "$2" ;;
    status) cmd_status ;;
    log) cmd_log "$2" ;;
    diff) cmd_diff "$2" ;;

    # GitHub API
    pr) cmd_pr "$2" "$3" "${@:4}" ;;
    issue) cmd_issue "$2" "$3" "${@:4}" ;;
    release) cmd_release "$2" "$3" "${@:4}" ;;
    repos) cmd_repos "$2" ;;
    info) cmd_info "$2" ;;

    # Configuration
    config) cmd_config ;;
    auth) cmd_auth ;;

    # Help
    -h|--help) usage ;;
    *) log_error "Unknown command: $1"; usage ;;
esac