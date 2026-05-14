---
name: xhs-researcher
description: 竞品研究工具。使用搜狗微信搜索进行内容角度研究，结合全网搜索分析竞品，提炼差异化角度，为选题提供数据支撑。（小红书内站搜索已禁用）
---

# XHS 竞品研究与选题分析

## 搜索引擎

| 引擎 | 数据来源 | 能拿到什么 | 适合做什么 |
|------|---------|-----------|-----------|
| 搜狗微信搜索脚本 | 微信公众号文章 | 标题/摘要/发布时间/来源 | 内容角度研究、标题模式分析 |
| ~~xiaohongshu-search~~ | ~~小红书内站（浏览器）~~ | ~~标题/点赞/收藏/评论/标签~~ | **已禁用** - 为避免封号风险，不再使用 |

> ⚠️ **重要变更**：`xiaohongshu-search` 已禁用。所有竞品分析改用搜狗微信搜索 + `multi-search-engine` 全网搜索完成。

**当前推荐搭配：**
- 微信搜索：快、稳定、适合批量关键词扫描
- 全网搜索（`multi-search-engine`）：补充热点资讯、行业动态

---

## 引擎一：搜狗微信搜索脚本

### 脚本目录

脚本位于 `${SKILL_DIR}/scripts/`

| 脚本 | 用途 | 命令 |
|------|------|------|
| `scripts/search_wechat.js` | 搜狗微信文章搜索 | `node ${SKILL_DIR}/scripts/search_wechat.js "关键词"` |

### 搜索参数

`${SKILL_DIR}` 为本 SKILL.md 所在目录的绝对路径，Agent 执行前需先确认：

```bash
# 跨平台兼容命令（相对于工作区根目录）
node "./skills/xhs-researcher/scripts/search_wechat.js" "关键词"
node "./skills/xhs-researcher/scripts/search_wechat.js" "关键词" -n 15
node "./skills/xhs-researcher/scripts/search_wechat.js" "关键词" -n 20 -o result.json
```

**跨平台说明：** EasyClaw 启动时已将工作区设为当前工作目录（`$PWD`），直接使用 `./` 相对路径即可，无需区分 Windows / macOS / Linux。

**输出字段：** 文章标题、链接、摘要、发布时间、来源公众号

### 搜索关键词策略

每次执行 2-3 轮，覆盖不同维度：

```bash
# 示例：数码领域（macOS）
node ~/.easyclaw/workspace-xhs-operator/skills/xhs-researcher/scripts/search_wechat.js "手机推荐 2026" -n 10
node ~/.easyclaw/workspace-xhs-operator/skills/xhs-researcher/scripts/search_wechat.js "数码测评" -n 10
node ~/.easyclaw/workspace-xhs-operator/skills/xhs-researcher/scripts/search_wechat.js "手机对比 性价比" -n 10
```

两次搜索间等待 3-5 秒，避免反爬限制。

### 注意事项
- 搜索结果可能因反爬为空，换关键词重试
- 不建议使用 `-r` 参数解析真实URL（成功率低）
- 工具仅用于学习研究，禁止大规模爬取

---

## ~~引擎二：小红书内站搜索（xiaohongshu-search）~~ （已禁用）

> ⚠️ **此引擎已禁用**
>
> 为避免浏览器操作触发小红书封号风险，`xiaohongshu-search` 不再使用。
>
> **替代方案**：
> - 使用 `multi-search-engine` 进行全网搜索获取热点数据
> - 使用 `web_search` 搜索竞品相关内容
> - 话题标签基于领域常用标签推荐，而非抓取数据

---

## 协同工作流

### 标准竞品研究流程（Step 2 中执行）

```
① 搜狗微信搜索（快速，3轮）
   关键词1：[领域核心词] -n 10
   关键词2：[热点词+领域] -n 10
   关键词3：[用户痛点词] -n 10
   → 提取：标题模式、内容角度、已覆盖方向

② 全网搜索（multi-search-engine，补充热点数据）
   搜索：[领域关键词] + 热点/趋势/测评
   → 提取：行业动态、用户关注点、竞品信息

③ 交叉分析 → 生成差异化选题
```

### 差异化角度提炼

从两路数据中提炼 3-5 个差异化机会：

```
差异化分析报告：

【高频内容方向】（已被大量覆盖，竞争激烈）
- 方向A：已有 X 篇相关内容，平均点赞 X
- 方向B：...

【差异化机会】
1. [竞品的不足] → 我们可以 [更好的角度]
   数据支撑：搜小红书「XX」只有X篇，均值点赞低

2. [尚未被覆盖的角度]
   数据支撑：微信搜索无相关结果，小红书结果少

【话题标签参考】（从小红书高赞笔记中提取）
大话题：#XX #XX
精准标签：#XX #XX
```
