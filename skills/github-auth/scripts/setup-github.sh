#!/bin/bash

# GitHub Authentication Setup Script
# Interactive setup for SSH Key or Personal Access Token

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_ask() { echo -e "${YELLOW}[?]${NC} $1"; }
log_step() { echo -e "${CYAN}▶${NC} $1"; }
log_title() { echo -e "\n${BOLD}$1${NC}\n"; }

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Show banner
show_banner() {
    cat << 'EOF'
   ____ _  _ ____ ____ ____ ____ 
  / ___| || |  _ \|  _ \| __ )|  _ \
 | |  _| || |_| | | | |  _ \| | | |
 | |_| |__   _| |_| | |_| | |_) | |_| |
  \____|  |_|____/|____/|____/|____/
  
  Authentication Setup
  
EOF
}

# Show authentication comparison
show_comparison() {
    cat << 'EOF'
┌─────────────────────────────────────────────────────┐
│           认证方式对比                               │
├─────────────────────────────────────────────────────┤
│ 功能              │ SSH 密钥 │ Personal Access Token │
├──────────────────┼─────────┼───────────────────────┤
│ 克隆仓库          │    ✅    │          ✅            │
│ 推送/拉取代码      │    ✅    │          ✅            │
│ 创建分支          │    ✅    │          ✅            │
│ 创建 PR (API)     │    ❌    │          ✅            │
│ 创建 Issue        │    ❌    │          ✅            │
│ 创建 Release      │    ❌    │          ✅            │
│ GitHub API        │    ❌    │          ✅            │
└─────────────────────────────────────────────────────┘

⚠️  重要提示：
   - SSH 无法通过 API 创建 PR
   - 如需创建 PR/Issue/Release，必须使用 Token
   - 可以同时配置两种方式

EOF
}

# Check if git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed!"
        log_info "Please install Git first:"
        echo "  Ubuntu/Debian: sudo apt-get install git"
        echo "  macOS: brew install git"
        echo "  Windows: https://git-scm.com/downloads"
        exit 1
    fi
    log_success "Git is installed: $(git --version)"
}

# Setup SSH Key
setup_ssh() {
    log_title "SSH 密钥设置"
    
    log_info "SSH 密钥用于 Git 操作（克隆、推送、拉取）"
    log_warn "⚠️  SSH 无法通过 GitHub API 创建 PR/Issue/Release"
    echo ""
    
    log_ask "继续配置 SSH？ (y/n): "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy] ]]; then
        log_info "已取消 SSH 配置"
        return
    fi
    
    # Get user info
    log_ask "GitHub 用户名: "
    read -r username
    [ -z "$username" ] && { log_error "用户名不能为空"; return; }
    
    log_ask "GitHub 邮箱: "
    read -r email
    [ -z "$email" ] && { log_error "邮箱不能为空"; return; }
    
    # Generate SSH key
    log_step "生成 SSH 密钥..."
    "$SCRIPT_DIR/generate-ssh-key.sh" "$email"
    
    # Configure git
    log_step "配置 Git..."
    git config --global user.name "$username"
    git config --global user.email "$email"
    log_success "Git 配置完成"
    
    # Show public key
    echo ""
    log_info "你的 SSH 公钥："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat ~/.ssh/id_ed25519_github.pub
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Instructions
    log_step "下一步：添加 SSH 公钥到 GitHub"
    echo ""
    echo "1. 访问: https://github.com/settings/ssh/new"
    echo "2. 点击 'New SSH key'"
    echo "3. 标题: OpenClaw Bot"
    echo "4. 粘贴上面的公钥"
    echo "5. 点击 'Add SSH key'"
    echo ""
    
    log_ask "已添加到 GitHub？ (y/n): "
    read -r added
    if [[ "$added" =~ ^[Yy] ]]; then
        test_ssh_connection
    fi
}

# Test SSH connection
test_ssh_connection() {
    log_step "测试 SSH 连接..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_success "SSH 认证成功！"
        log_info "你现在可以使用 SSH 进行 Git 操作了"
    else
        log_error "SSH 认证失败"
        log_info "请确认已将公钥添加到 GitHub"
    fi
}

# Setup Token
setup_token() {
    log_title "Personal Access Token 设置"
    
    log_info "Token 用于 GitHub API 操作（创建 PR、Issue、Release）"
    log_info "Token 需要包含仓库读写权限"
    echo ""
    
    # Show instructions
    log_step "如何获取 GitHub Token："
    echo ""
    echo "1. 访问: https://github.com/settings/tokens"
    echo "2. 点击 'Generate new token (classic)'"
    echo "3. 设置："
    echo "   - Note: OpenClaw Bot Token"
    echo "   - Expiration: No expiration (或选择期限)"
    echo "   - Select scopes:"
    echo "     ✅ repo (全部勾选)"
    echo "4. 点击 'Generate token'"
    echo "5. 复制生成的 Token（只显示一次！）"
    echo ""
    
    log_ask "已获取 Token？ (y/n): "
    read -r has_token
    if [[ ! "$has_token" =~ ^[Yy] ]]; then
        log_info "请先获取 Token，然后重新运行此脚本"
        return
    fi
    
    # Get token
    log_ask "粘贴你的 Token: "
    read -r token
    [ -z "$token" ] && { log_error "Token 不能为空"; return; }
    
    # Validate token
    log_step "验证 Token..."
    local user_info=$(curl -s -H "Authorization: token $token" https://api.github.com/user)
    
    if echo "$user_info" | grep -q '"login"'; then
        local login=$(echo "$user_info" | grep '"login"' | cut -d'"' -f4)
        log_success "Token 有效！认证用户: $login"
        
        # Check scopes
        local scopes=$(curl -sI -H "Authorization: token $token" https://api.github.com/ | grep -i "x-oauth-scopes" | cut -d':' -f2)
        if echo "$scopes" | grep -q "repo"; then
            log_success "Token 包含 repo 权限"
        else
            log_error "Token 缺少 repo 权限"
            log_info "请重新生成 Token 并勾选 repo 权限"
            return
        fi
        
        # Save token
        save_token "$token"
        
        # Configure git if not configured
        local git_name=$(git config user.name 2>/dev/null)
        local git_email=$(git config user.email 2>/dev/null)
        
        if [ -z "$git_name" ] || [ -z "$git_email" ]; then
            log_ask "GitHub 用户名 [$login]: "
            read -r username
            [ -z "$username" ] && username="$login"
            
            log_ask "GitHub 邮箱: "
            read -r email
            [ -z "$email" ] && { log_error "邮箱不能为空"; return; }
            
            git config --global user.name "$username"
            git config --global user.email "$email"
            log_success "Git 配置完成"
        fi
        
        log_success "Token 配置完成！"
        log_info "你现在可以使用 GitHub API 创建 PR/Issue/Release 了"
    else
        log_error "Token 无效或已过期"
        log_info "请检查 Token 是否正确"
    fi
}

# Save token
save_token() {
    local token="$1"
    local config_file="$HOME/.config/github-remote.conf"
    mkdir -p "$(dirname "$config_file")"
    
    # Update or create config
    if [ -f "$config_file" ]; then
        sed -i "s/github_token=.*/github_token=\"$token\"/" "$config_file" 2>/dev/null || \
        echo "github_token=\"$token\"" >> "$config_file"
    else
        cat > "$config_file" << EOF
github_token="$token"
git_user_name="$(git config user.name 2>/dev/null || echo 'OpenClaw Bot')"
git_user_email="$(git config user.email 2>/dev/null || echo 'bot@openclaw.ai')"
EOF
    fi
    
    # Also set environment variable for current session
    export GITHUB_TOKEN="$token"
    
    log_success "Token 已保存到: $config_file"
}

# Main
main() {
    show_banner
    check_git
    show_comparison
    
    log_ask "选择认证方式：
  1) SSH 密钥（用于 Git 操作）
  2) Personal Access Token（用于 Git + GitHub API）
  3) 配置两种方式
  
请输入 (1/2/3): "
    read -r choice
    
    case $choice in
        1)
            setup_ssh
            ;;
        2)
            setup_token
            ;;
        3)
            setup_ssh
            echo ""
            setup_token
            ;;
        *)
            log_error "无效选择"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "设置完成！"
    log_info "你可以使用以下命令测试："
    echo "  git clone git@github.com:user/repo.git  (SSH)"
    echo "  或使用 github-remote 技能进行操作"
}

main "$@"