# GitHub Authentication Skill

Configure GitHub authentication for remote operations. Choose between SSH Key or Personal Access Token.

## Description

This skill helps you set up GitHub authentication with two methods:

**SSH Key** - For Git operations:
- ✅ Clone repositories
- ✅ Push/Pull code
- ✅ Create branches
- ❌ Cannot create PR via API

**Personal Access Token** - For GitHub API:
- ✅ All Git operations
- ✅ Create Pull Requests
- ✅ Create Issues
- ✅ Create Releases
- ✅ Access GitHub API

## Requirements

### Token Permissions
When creating a Personal Access Token, select:
- `repo` - Full control of private repositories

### How to Get Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: ✅ `repo`
4. Generate and save the token

## Usage

```bash
cd scripts
./setup-github.sh

# Choose authentication method:
# 1) SSH Key (for Git operations)
# 2) Personal Access Token (for Git + GitHub API)
# 3) Configure both
```

## Authentication Comparison

| Feature | SSH Key | Token |
|---------|---------|-------|
| Clone | ✅ | ✅ |
| Push/Pull | ✅ | ✅ |
| Create Branch | ✅ | ✅ |
| Create PR | ❌ | ✅ |
| Create Issue | ❌ | ✅ |
| Create Release | ❌ | ✅ |
| GitHub API | ❌ | ✅ |

## Files

```
github-auth/
├── SKILL.md              # This file
├── SKILL_CN.md           # Chinese version
├── scripts/              # Executable scripts
│   ├── setup-github.sh       # Main setup script
│   ├── generate-ssh-key.sh   # SSH key generation
│   ├── configure-token.sh    # Token configuration
│   └── check-repo-access.sh  # Repository access check
├── references/           # Reference documents
│   ├── AUTHENTICATION_COMPARISON.md
│   └── AUTHENTICATION_COMPARISON_CN.md
└── assets/               # (empty)
```

## Activation

This skill activates when user mentions:
- "Setup GitHub"
- "Configure GitHub"
- "GitHub authentication"
- "Connect to GitHub"

## Notes

- SSH is simpler for basic Git operations
- Token is required for GitHub API operations (PR, Issue, Release)
- You can configure both methods
- Token is stored in `~/.config/github-remote.conf`