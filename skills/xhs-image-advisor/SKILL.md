---
name: xhs-image-advisor
description: 小红书配图方案生成。基于文章内容和账号调性，制定配图策略，生成 8 维度 prompt，调用 huawei-image-gen 生成图片。
---

# XHS 配图方案

## 小红书图片规则

| 类型 | 规格 | 说明 |
|------|------|------|
| 封面图 | 竖图 3:4，如 1080×1440px | 最重要，决定点击率 |
| 内容图 | 1-9 张，建议 1080×1440px | 统一风格，有视觉连贯性 |
| 方图 | 1:1，如 1080×1080px | 部分场景适用 |

**小红书封面要点：**
- 竖图在 feed 流中占更大版面，视觉更突出
- 封面文字要大、要清晰（快速传达内容）
- 配色饱和度可以偏高（在 feed 流中更抢眼）
- 风格统一（和账号调性一致）

---

## 配图策略制定

### 第一步：分析内容

读取笔记草稿，分析：
- **内容主题**：核心是什么
- **情绪基调**：干货/种草/温暖/活泼/专业...
- **目标受众**：哪类人看到这个图会点进去
- **账号调性**：从 `memory/account_profile.json` 读取风格偏好

### 第二步：制定配图方案

**配图数量建议：**
- 干货/教程类：5-9 张（步骤图）
- 种草/测评类：3-6 张（产品图+场景图）
- 经验分享类：3-5 张（场景图+心情图）
- 对比/盘点类：4-6 张（对比图+结论图）

**每张图的功能定位：**

| 图片 | 功能 | 内容重点 |
|------|------|---------|
| 第1张（封面） | 吸引点击 | 标题文字 + 视觉钩子 |
| 第2-N张（内容图） | 传递信息 | 对应正文段落的视觉化 |
| 最后一张 | 引导互动 | 账号名/二维码/CTA |

### 第三步：生成 8 维度 Prompt

每张图必须覆盖 8 个视觉维度：

| 维度 | 含义 | 关键词参考 |
|------|------|-----------|
| **风格/媒介** | 整体视觉风格 | flat illustration, minimalist design, film photography, 3D render, watercolor, lifestyle photo |
| **构图** | 画面布局 | centered symmetry, rule of thirds, diagonal, flat lay, close-up |
| **空间环境** | 背景场景 | clean white background, warm wooden desk, outdoor natural light, minimal studio |
| **主体** | 画面主角 | product detail shot, young woman silhouette, hand holding phone, abstract shapes |
| **细节** | 纹理/文字等微观元素 | no text, linen texture, clean edges, Chinese text overlay area reserved |
| **光影** | 光源与反射 | soft natural window light, warm side light, flat even lighting, golden hour backlight |
| **色彩** | 主色调 | warm beige #F5E6D3, cool blue-gray #4A6FA5, vibrant coral #FF6B6B, Morandi muted tones |
| **镜头** | 焦段与景深 | 50mm portrait lens, wide angle flat, macro close-up, tilt-shift |

**末尾固定附加（封面图和内容图统一）：** `no text, no letters, no watermark, high quality, 4K detail`

> ⚠️ 封面图同样禁止生成任何文字——AI 生成的文字内容不可控且经常出错。
> 封面文字应在小红书发布时通过平台自带编辑器手动添加，或用 PS/Canva 后期叠加。
> prompt 中不要写 `text area reserved`，这会诱导模型生成文字。

**Prompt 组装示例：**

测评类封面：
```
Lifestyle flat lay photography, centered symmetrical composition, clean white background with subtle shadow, smartphone and accessories as main subjects, no text, no letters, no watermark, soft even studio lighting, warm white #FFFFFF with product accent colors, 35mm wide angle, high quality 4K detail
```

种草类内容图：
```
Warm lifestyle photography, rule-of-thirds composition, cozy coffee shop with warm wooden textures, young woman using phone with natural gesture, no text no watermark, warm golden window side light, warm beige #F5E6D3 and earth tones, 50mm portrait lens shallow depth of field, high quality 4K detail
```

### 第四步：安全检查（必须执行）

⛔ 生成图片前，确认 prompt **不包含**以下内容：
- 政治人物（现任/历史）、政治事件、国旗国徽讽刺
- 色情/性暗示内容
- 暴力/血腥场景
- 赌博相关元素
- 毒品相关内容
- 宗教贬低内容
- 可识别的真实人物（用泛化描述替代）
- 种族歧视/仇恨符号

**替代策略：**
- 真人 → 用轮廓/剪影/局部（如手部、背影）
- 品牌logo → 用同类物品描述（如「白色圆角方形图标」）

### 第五步：调用 huawei-image-gen 生成图片

⛔ **重要：huawei-image-gen 是 EasyClaw 内置技能，通过 Python 脚本命令行调用**

**技能类型判断：**
- huawei-image-gen 位于 EasyClaw 全局技能目录（安装目录下的 `skills/huawei-image-gen/`）
- **不在**工作区 `skills/` 目录下
- 调用方式：执行 Python 脚本，不是 sessions_spawn

---

⛔ **逐张生成，不要批量**：每生成一张，立即记录路径，然后再生成下一张。

**调用方式（Python 命令行）：**

```bash
# 文生图
python {baseDir}/scripts/generate_image.py --prompt "[8 维度 prompt]" --filename "output.jpg" --resolution 2K

# 指定比例（如竖图 3:4）
python {baseDir}/scripts/generate_image.py --prompt "[8 维度 prompt]" --filename "output.jpg" --aspect-ratio 3:4 --resolution 2K
```

**参数说明：**
| 参数 | 说明 | 必填 |
|------|------|------|
| `--prompt` | 画面描述（8 维度 prompt） | ✅ |
| `--filename` | 输出文件路径（必须.jpg/.jpeg） | ✅ |
| `--resolution` | 分辨率：2K（默认）或 3K | ❌ |
| `--aspect-ratio` | 比例：1:1/2:3/3:2/3:4/4:3/9:16/16:9/21:9 | ❌ |
| `-i` | 输入图片（图生图时使用，可多个） | ❌ |

**封面图（竖图）：**
- 比例：`--aspect-ratio 3:4`
- 保存路径：`output/covers/cover_YYYYMMDD_[slug].jpg`

**内容图（竖图/方图）：**
- 比例：`--aspect-ratio 3:4` 或 `--aspect-ratio 1:1`
- 保存路径：`drafts/images/img_001.jpg`、`img_002.jpg`...

**风格一致性要求：**
- 同一篇笔记的所有图片使用相同视觉风格
- 色彩基调保持统一（如全部暖系或全部冷系）
- 不同张图之间有视觉连贯性

---

**📌 调用示例（数码测评类封面）：**

```bash
# Windows PowerShell
python "{baseDir}/scripts/generate_image.py" --prompt "Lifestyle product photography, centered symmetrical composition, clean white desk background with subtle shadow, 8.8-inch tablet device showing slim profile from side angle, no text no letters no watermark, soft natural window lighting from side, cool white #FFFFFF with silver accent #C0C0C0, 35mm wide angle sharp focus, high quality 4K detail" --filename "output/covers/cover_20260413_oppo_pad_mini.jpg" --aspect-ratio 3:4 --resolution 2K

# macOS/Linux
python "{baseDir}/scripts/generate_image.py" --prompt "Lifestyle product photography, centered symmetrical composition, clean white desk background with subtle shadow, 8.8-inch tablet device showing slim profile from side angle, no text no letters no watermark, soft natural window lighting from side, cool white #FFFFFF with silver accent #C0C0C0, 35mm wide angle sharp focus, high quality 4K detail" --filename "output/covers/cover_20260413_oppo_pad_mini.jpg" --aspect-ratio 3:4 --resolution 2K
```

**路径说明：**
- `{baseDir}` 是 huawei-image-gen 技能目录（由 EasyClaw 自动解析）
- 输出路径用相对路径（相对于工作区根目录）
- 统一用正斜杠 `/`（Windows/macOS/Linux 都兼容）

---

**⚠️ 注意事项：**
1. 输出格式固定为 **JPEG**，`--filename` 必须以 `.jpg` 或 `.jpeg` 结尾
2. prompt 末尾固定添加：`no text, no letters, no watermark, high quality, 4K detail`
3. 封面图不要生成文字（AI 生成文字会出错），文字在发布时手动添加
4. 逐张生成，不要批量（每张图独立执行命令）

---

## 不同账号类型的配图风格参考

| 账号类型 | 推荐风格 | 色彩偏好 |
|---------|---------|---------|
| 数码测评 | 产品棚拍风、极简白背景 | 冷白、科技蓝、银灰 |
| 美妆护肤 | 生活质感照、平铺摆拍 | 粉调、奶油白、玫瑰金 |
| 美食 | 自然光食物摄影 | 暖橙、米白、棕褐 |
| 旅行 | 风景大片、人文纪实 | 多彩、饱和、自然 |
| 母婴育儿 | 温馨生活感、柔和光线 | 奶黄、薄荷绿、婴儿蓝 |
| 职场/干货 | 信息图表风、简洁插画 | 商务蓝、白、灰 |
| 健身运动 | 动感拍摄、高对比度 | 活力橙、黑白、荧光绿 |

---

## 输出总结格式

```
🎨 配图方案

共 N 张图：
- 第1张（封面）：[描述] → 保存至 output/covers/cover_YYYYMMDD.jpg
- 第2张（内容图1）：[描述] → 保存至 drafts/images/img_001.jpg
- ...

视觉风格：[统一风格描述]
色彩基调：[主色调描述]

生成状态：
✅ 封面图 - 已生成
✅ 内容图1 - 已生成
❌ 内容图2 - 生成失败（原因：...）
```
