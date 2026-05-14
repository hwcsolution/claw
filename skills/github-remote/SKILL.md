# GitHub Remote Connection Skill

Connect to GitHub repositories and perform remote operations: clone, push, create branch, create PR.

## Description

A complete skill for GitHub remote operations with Git commands and GitHub API integration.

### Git Operations
- `clone` - Clone repository
- `push` - Push files (asks about creating new branch)
- `pull` - Pull latest changes
- `branch` - Create/switch branch
- `status` - Show working tree status
- `log` - Show commit history
- `diff` - Show changes

### GitHub API
- `pr` - Create Pull Request
- `issue` - Create Issue
- `release` - Create Release
- `repos` - List repositories
- `info` - Show repository info

### Configuration
- `config` - Configure settings
- `auth` - Check authentication

## Authentication

| Operation | SSH Key | Token |
|-----------|---------|-------|
| Git Operations | ✅ | ✅ |
| GitHub API | ❌ | ✅ |

**Important**: GitHub API operations (PR, Issue, Release) require Token.

## Usage

```bash
cd scripts
./github-remote.sh <command> [options]

# Examples:
./github-remote.sh clone user/repo
./github-remote.sh push user/repo file.py
./github-remote.sh pr user/repo "PR title"
./github-remote.sh auth
```

## Interactive Push

When pushing files, the script asks:
```
[?] Create new branch? (y/n) [y]:
```

- `y` - Create new branch (asks for branch name)
- `n` - Push to current branch

## Files

```
github-remote/
├── SKILL.md              # This file
├── SKILL_CN.md           # Chinese version
├── scripts/              # Executable scripts
│   └── github-remote.sh      # Main script (all operations)
├── references/           # Reference documents
│   └── usage.md              # Detailed usage guide
└── assets/               # (empty)
```

## Activation

This skill activates when user mentions:
- "Push to [repo]"
- "Clone [repo]"
- "Create PR"
- "Create Issue"
- "Upload to GitHub"
- "Connect to [repo]"

## Notes

- Keep it simple - one script does all
- Always ask before creating new branch
- Token required for PR creation
- SSH works for push/pull only