# GitHub 认证技能

配置 GitHub 认证以进行远程操作。选择 SSH 密钥或个人访问令牌。

## 描述

此技能帮助你设置 GitHub 认证，提供两种方式：

**SSH 密钥** - 用于 Git 操作：
- ✅ 克隆仓库
- ✅ 推送/拉取代码
- ✅ 创建分支
- ❌ 无法通过 API 创建 PR

**个人访问令牌** - 用于 GitHub API：
- ✅ 所有 Git 操作
- ✅ 创建 Pull Request
- ✅ 创建 Issue
- ✅ 创建 Release
- ✅ 访问 GitHub API

## 要求

### Token 权限
创建个人访问令牌时，需要选择：
- `repo` - 完全控制私有仓库

### 如何获取 Token
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：✅ `repo`
4. 生成并保存令牌

## 使用方法

```bash
cd scripts
./setup-github.sh

# 选择认证方式：
# 1) SSH 密钥（用于 Git 操作）
# 2) 个人访问令牌（用于 Git + GitHub API）
# 3) 配置两种方式
```

## 认证对比

| 功能 | SSH 密钥 | Token |
|------|----------|-------|
| 克隆 | ✅ | ✅ |
| 推送/拉取 | ✅ | ✅ |
| 创建分支 | ✅ | ✅ |
| 创建 PR | ❌ | ✅ |
| 创建 Issue | ❌ | ✅ |
| 创建 Release | ❌ | ✅ |
| GitHub API | ❌ | ✅ |

## 文件结构

```
github-auth/
├── SKILL.md              # 英文说明
├── SKILL_CN.md           # 中文说明
├── scripts/              # 可执行脚本
│   ├── setup-github.sh       # 主设置脚本
│   ├── generate-ssh-key.sh   # SSH 密钥生成
│   ├── configure-token.sh    # Token 配置
│   └── check-repo-access.sh  # 仓库访问检查
├── references/           # 参考文档
│   ├── AUTHENTICATION_COMPARISON.md
│   └── AUTHENTICATION_COMPARISON_CN.md
└── assets/               # （空）
```

## 激活方式

当用户提到以下关键词时激活：
- "设置 GitHub"
- "配置 GitHub"
- "GitHub 认证"
- "连接到 GitHub"

## 注意事项

- SSH 对基本 Git 操作更简单
- Token 是 GitHub API 操作必需的（PR、Issue、Release）
- 可以同时配置两种方式
- Token 存储在 `~/.config/github-remote.conf`