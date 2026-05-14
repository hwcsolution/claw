# GitHub Remote Connection Skill

完整的 GitHub 远程操作技能 - Git 操作 + GitHub API 集成。

## 快速开始

```bash
# 配置（首次使用）
./github-remote.sh config

# 克隆仓库
./github-remote.sh clone user/repo

# 推送文件（会询问是否创建新分支）
./github-remote.sh push user/repo myfile.py

# 创建 PR
./github-remote.sh pr user/repo "Add feature"
```

## 命令总览

### Git 操作

| 命令 | 说明 | 示例 |
|------|------|------|
| `clone` | 克隆仓库 | `clone user/repo` |
| `push` | 推送文件 | `push user/repo file.py` |
| `pull` | 拉取更新 | `pull [branch]` |
| `branch` | 创建/切换分支 | `branch feature/new` |
| `status` | 查看状态 | `status` |
| `log` | 查看历史 | `log [count]` |
| `diff` | 查看更改 | `diff [file]` |

### GitHub API

| 命令 | 说明 | 示例 |
|------|------|------|
| `pr` | 创建 PR | `pr user/repo "标题"` |
| `issue` | 创建 Issue | `issue user/repo "标题"` |
| `release` | 创建 Release | `release user/repo v1.0` |
| `repos` | 列出仓库 | `repos [user]` |
| `info` | 仓库信息 | `info user/repo` |

### 配置

| 命令 | 说明 |
|------|------|
| `config` | 配置 Token、用户信息 |
| `auth` | 检查认证状态 |

## 使用示例

### 1. 克隆和推送

```bash
# 克隆仓库
./github-remote.sh clone user/repo

# 推送文件（交互式）
./github-remote.sh push user/repo myfile.py
# [?] Create new branch? (y/n) [y]: y
# [?] Branch name: feature/new-feature
# [✓] Pushed successfully!

# 推送到指定分支
./github-remote.sh push user/repo myfile.py \
    --branch feature/new \
    --message "Add new feature"
```

### 2. 创建 PR

```bash
# 创建 PR（需要 Token）
./github-remote.sh pr user/repo "Add new feature" \
    --base main \
    --body "Description here"

# 输出：
# [✓] PR #42 created!
# [INFO] https://github.com/user/repo/pull/42
```

### 3. 创建 Issue

```bash
./github-remote.sh issue user/repo "Bug in feature X" \
    --body "Steps to reproduce..."
```

### 4. 创建 Release

```bash
./github-remote.sh release user/repo v1.0.0 \
    --body "Release notes..."
```

### 5. 查看仓库信息

```bash
./github-remote.sh info user/repo

# 输出：
# 📦 user/repo
#    A test repository
# 
# 📊 Stats:
#    ⭐ Stars: 10
#    🍴 Forks: 5
#    🐛 Issues: 2
#    💻 Language: Python
# 
# 🔗 URL: https://github.com/user/repo
```

### 6. 列出仓库

```bash
# 列出你的仓库
./github-remote.sh repos

# 列出其他用户的仓库
./github-remote.sh repos username
```

### 7. Git 操作

```bash
# 查看状态
./github-remote.sh status

# 查看历史
./github-remote.sh log 20

# 查看更改
./github-remote.sh diff myfile.py

# 创建分支
./github-remote.sh branch feature/new

# 拉取更新
./github-remote.sh pull main
```

## 配置

### 方式 1：交互式配置

```bash
./github-remote.sh config

# [?] GitHub Token: ghp_your_token_here
# [?] Git User Name [OpenClaw Bot]: Your Name
# [?] Git User Email [bot@openclaw.ai]: your@email.com
# [✓] Config saved
```

### 方式 2：环境变量

```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GIT_USER_NAME="Your Name"
export GIT_USER_EMAIL="your@email.com"
```

### 方式 3：配置文件

配置保存在：`~/.config/github-remote.conf`

## 认证检查

```bash
./github-remote.sh auth

# 输出：
# [✓] SSH: Authenticated
# [✓] Token: Authenticated as username
```

## 交互式推送

推送文件时会自动询问：

```
[?] Create new branch? (y/n) [y]:
```

- 输入 `y` 或回车：创建新分支
  - 继续询问分支名称
  - 默认：`feature/YYYYMMDD-HHMMSS`
- 输入 `n`：推送到当前分支

## 认证说明

| 操作 | SSH 密钥 | Token | 说明 |
|------|----------|-------|------|
| 克隆仓库 | ✅ | ✅ | SSH 优先 |
| 推送代码 | ✅ | ✅ | SSH 优先 |
| 创建分支 | ✅ | ✅ | SSH 优先 |
| **创建 PR** | ❌ | ✅ | Token 必需 |
| **创建 Issue** | ❌ | ✅ | Token 必需 |
| **创建 Release** | ❌ | ✅ | Token 必需 |
| **API 操作** | ❌ | ✅ | Token 必需 |

## 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - `repo` - 完整仓库访问
   - `user` - 用户信息
4. 生成并保存 Token

## 完整工作流示例

```bash
# 1. 配置
./github-remote.sh config

# 2. 克隆仓库
./github-remote.sh clone user/repo
cd repo

# 3. 创建新功能
echo "def new_feature(): pass" > feature.py

# 4. 推送到新分支
./github-remote.sh push user/repo feature.py
# [?] Create new branch? y
# [?] Branch name: feature/new-feature

# 5. 创建 PR
./github-remote.sh pr user/repo "Add new feature"

# 完成！
```

## 错误处理

### Token 未设置

```
[✗] GitHub token required
[INFO] Set with: github-remote.sh config
[INFO] Or: export GITHUB_TOKEN=xxx
```

### 认证失败

```
[✗] Failed to clone
[INFO] Check if repository exists and you have access
```

### PR 创建失败

```
[✗] Failed to create PR
{"message": "Bad credentials", ...}
```

## 技能激活关键词

- "推送到 [repo]"
- "克隆 [repo]"
- "创建 PR"
- "创建 Issue"
- "查看仓库信息"
- "列出仓库"

## 与其他技能对比

| 技能 | 功能 | 适用场景 |
|------|------|----------|
| **github-auth** | SSH/Token 认证配置 | 初次设置 |
| **github-remote** | Git 操作 + GitHub API | 日常使用 |

## 技术细节

- **语言**: Bash
- **API**: GitHub REST API v3
- **认证**: SSH + Token 双模式
- **配置**: `~/.config/github-remote.conf`
- **依赖**: git, curl

## 限制

- Token 需要 `repo` 权限
- 大文件需要 Git LFS
- API 请求有速率限制

---

**一个脚本，完整功能：Git 操作 + GitHub API 集成！**