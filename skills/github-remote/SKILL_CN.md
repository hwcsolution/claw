# GitHub 远程连接技能

连接 GitHub 仓库并执行远程操作：克隆、推送、创建分支、创建 PR。

## 描述

完整的 GitHub 远程操作技能，集成 Git 命令和 GitHub API。

### Git 操作
- `clone` - 克隆仓库
- `push` - 推送文件（询问是否创建新分支）
- `pull` - 拉取最新更改
- `branch` - 创建/切换分支
- `status` - 显示工作区状态
- `log` - 显示提交历史
- `diff` - 显示更改

### GitHub API
- `pr` - 创建 Pull Request
- `issue` - 创建 Issue
- `release` - 创建 Release
- `repos` - 列出仓库
- `info` - 显示仓库信息

### 配置
- `config` - 配置设置
- `auth` - 检查认证

## 认证

| 操作 | SSH 密钥 | Token |
|------|----------|-------|
| Git 操作 | ✅ | ✅ |
| GitHub API | ❌ | ✅ |

**重要**：GitHub API 操作（PR、Issue、Release）需要 Token。

## 使用方法

```bash
cd scripts
./github-remote.sh <命令> [选项]

# 示例：
./github-remote.sh clone user/repo
./github-remote.sh push user/repo file.py
./github-remote.sh pr user/repo "PR 标题"
./github-remote.sh auth
```

## 交互式推送

推送文件时，脚本会询问：
```
[?] 创建新分支？ (y/n) [y]:
```

- `y` - 创建新分支（询问分支名称）
- `n` - 推送到当前分支

## 文件结构

```
github-remote/
├── SKILL.md              # 英文说明
├── SKILL_CN.md           # 中文说明
├── scripts/              # 可执行脚本
│   └── github-remote.sh      # 主脚本（所有操作）
├── references/           # 参考文档
│   └── usage.md              # 详细使用指南
└── assets/               # （空）
```

## 激活方式

当用户提到以下关键词时激活：
- "推送到 [repo]"
- "克隆 [repo]"
- "创建 PR"
- "创建 Issue"
- "上传到 GitHub"
- "连接到 [repo]"

## 注意事项

- 保持简洁 - 一个脚本完成所有功能
- 创建新分支前总是询问用户
- 创建 PR 需要 Token
- SSH 仅用于推送/拉取