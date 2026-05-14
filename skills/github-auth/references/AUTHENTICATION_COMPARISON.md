# GitHub Authentication: SSH vs Token

## Overview

This document explains the differences between SSH key and Personal Access Token (PAT) authentication methods for GitHub, and when to use each.

## Quick Comparison

| Feature | SSH Key | Personal Access Token |
|---------|---------|----------------------|
| **Git Operations** | ✅ Full access | ✅ Full access |
| **GitHub API** | ❌ No access | ✅ Full access |
| **PR Creation** | ❌ Not possible | ✅ Via API |
| **PR Merging** | ❌ Not possible | ✅ Via API |
| **Security** | Very high | High (with proper scopes) |
| **Ease of Use** | One-time setup | Requires token management |
| **Automation** | Limited to Git | Full API automation |
| **Expiration** | Never (unless revoked) | Configurable (default: never) |
| **Scope Control** | All or nothing | Granular permissions |

## Detailed Explanation

### SSH Key Authentication

**What it is:**
- A cryptographic key pair (public/private) for secure Git operations
- Public key added to GitHub account
- Private key stays on your machine

**What it CAN do:**
- Clone repositories (git clone)
- Push code (git push)
- Pull updates (git pull)
- Create and manage branches
- All standard Git operations

**What it CANNOT do:**
- Create Pull Requests via GitHub API
- Merge Pull Requests
- Access GitHub REST API
- Manage repository settings
- Create issues, labels, milestones
- Any operation that requires GitHub API

**Best for:**
- Daily development work
- Local Git operations
- When you only need to read/write code
- Simple authentication without token management

### Personal Access Token (PAT) Authentication

**What it is:**
- A token generated in GitHub settings
- Used for HTTPS authentication
- Can have granular permissions (scopes)

**What it CAN do:**
- Everything SSH keys can do (Git operations)
- **Create Pull Requests** via API
- Merge Pull Requests
- Access GitHub REST API
- Manage repository settings
- Create issues, labels, webhooks
- Full GitHub automation

**What it CANNOT do:**
- Nothing (with proper scopes) - it has full API access

**Best for:**
- CI/CD pipelines
- Automated scripts
- GitHub Actions workflows
- Creating PRs programmatically
- Repository management tools
- Any automation requiring GitHub API

## Practical Examples

### SSH Key Usage (Daily Work)
```bash
# Clone a repository
git clone git@github.com:user/repo.git

# Push changes
git push origin main

# Create a branch
git checkout -b feature-branch
```

### Token Usage (Automation)
```bash
# Create a Pull Request via API
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/user/repo/pulls \
  -d '{"title":"New feature","head":"feature-branch","base":"main"}'

# Merge a Pull Request
curl -X PUT \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/user/repo/pulls/123/merge
```

## When to Use Which

### Use SSH Key When:
- You're a developer working locally
- You only need to push/pull code
- You want simple, secure authentication
- You don't need API access
- You're setting up a new machine

### Use Personal Access Token When:
- You're writing automation scripts
- You need to create PRs programmatically
- You're setting up CI/CD pipelines
- You need GitHub API access
- You're building tools that interact with GitHub

## Security Considerations

### SSH Keys
- **Strength**: Very secure (cryptographic keys)
- **Risk**: If private key is compromised, attacker has full repo access
- **Management**: One key per machine, easy to revoke
- **Best Practice**: Use ed25519 algorithm, protect private key with passphrase

### Personal Access Tokens
- **Strength**: Secure with proper scopes
- **Risk**: Token can have broad permissions if not scoped properly
- **Management**: Can set expiration, granular permissions
- **Best Practice**: Use minimal required scopes, set expiration, rotate regularly

## Recommendation

**For most users:**
1. Set up SSH key for daily Git operations
2. Create a Personal Access Token with `repo` scope for automation
3. Store token securely (environment variables, password manager)
4. Use SSH for git commands, token for API calls

**For automation:**
1. Always use Personal Access Tokens
2. Set appropriate scopes (usually just `repo`)
3. Store tokens in secure environment variables
4. Rotate tokens regularly (every 90 days)

## Creating a Token for PR Automation

1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes:
   - `repo` (full control of private repositories)
   - Or `public_repo` (for public repositories only)
4. Set expiration (recommended: 90 days)
5. Generate and copy the token
6. Use as `GITHUB_TOKEN` environment variable

## Script Usage

This skill's `create-pr.sh` script will:
1. Try to use `GITHUB_TOKEN` environment variable if available
2. If no token, provide manual PR creation link
3. Guide user through token setup if needed

Remember: **SSH cannot create PRs via API, tokens are required for automation.**