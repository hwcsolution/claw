---
name: huawei-image-gen
description: "华为云MaaS文生图。触发场景：(1) 用户需要AI生成图片 (2) 小红书配图生成 (3) 说生成图片、AI画图。支持：Qwen-image模型、中英文prompt、多种尺寸、base64输出。"
---

# huawei-image-gen - 华为云MaaS文生图

使用华为云MaaS平台的Qwen-image模型生成图片。

## 前置条件

### 1. 开通模型服务

访问华为云MaaS控制台：
https://console.huaweicloud.com/modelarts/?region=cn-southwest-2#/model-studio/deployment

**开通步骤**：

![开通模型](开通模型.png)

1. 登录华为云控制台
2. 进入ModelArts模型工作室
3. 在模型广场搜索 **Qwen-image**
4. 点击「部署」或「开通」
5. 等待模型部署完成

### 2. 获取API Key

**获取步骤**：

![创建API-Key](创建API-Key.png)

1. 在已部署的模型详情页
2. 点击「API Key管理」或「获取密钥」
3. 创建新的API Key
4. 复制并保存API Key（**只显示一次，请妥善保管**）

### 3. 配置API Key

**方式1：环境变量**
```bash
export MAAS_API_KEY="你的API Key"
```

**方式2：配置文件**
```json
// config/config.json
{
  "maas": {
    "api_key": "你的API Key"
  }
}
```

## 工作流程

### Step 1: 接收生图请求

参数：
- prompt：图片描述（支持中英文）
- size：图片尺寸（默认1024x1024）
- seed：随机种子（可选，默认1）

### Step 2: 构建请求

```python
url = "https://api.modelarts-maas.com/v1/images/generations"
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}
data = {
    "model": "qwen-image",
    "prompt": prompt,
    "size": size,
    "response_format": "b64_json",
    "seed": seed
}
```

### Step 3: 调用API并保存

1. 发送请求到MaaS API
2. 接收base64编码的图片
3. 解码并保存到指定目录

### Step 4: 返回结果

输出：
- 图片保存路径
- 生成参数记录

### Step 5: 发送图片给用户

使用 message 工具将生成的图片发送给用户：

```python
message(
    action="send",
    media="[图片路径]",
    message="图片生成完成 🖼️"
)
```

**重要**：生成图片后必须发送给用户，不要只保存不发送。

## 使用示例

### 基础用法
```
用户：生成一张图片，一只奔跑的猫

执行：
1. 调用Qwen-image生成
2. 保存图片
3. 返回图片路径
```

### 小红书配图
```
用户：为这篇护肤笔记生成封面图

执行：
1. 根据笔记内容生成prompt
2. 调用API生成
3. 保存到小红书配图目录
```

### 指定尺寸
```
用户：生成一张3:4的竖图，护肤品质感拍摄

执行：
1. 转换3:4为具体尺寸（如768x1024）
2. 构建prompt
3. 生成并保存
```

## API参数说明

| 参数 | 说明 | 取值 |
|------|------|------|
| model | 模型名称 | qwen-image |
| prompt | 图片描述 | 中英文均可 |
| size | 图片尺寸 | 1024x1024, 512x512等 |
| response_format | 返回格式 | b64_json（暂仅支持此格式） |
| seed | 随机种子 | 0-2147483648，默认1 |

## 尺寸映射

小红书常用尺寸：
- 3:4 竖图 → 768x1024
- 1:1 方图 → 1024x1024
- 4:3 横图 → 1024x768

## 配置

API Key配置方式：

**方式1：环境变量**
```bash
export MAAS_API_KEY="你的API Key"
```

**方式2：配置文件**
```json
// config/config.json
{
  "maas": {
    "api_key": "你的API Key"
  }
}
```

## 输出格式

```markdown
## 🖼️ 图片生成完成

**Prompt**: [prompt内容]
**尺寸**: [尺寸]
**保存路径**: [文件路径]
**生成时间**: [时间]

![生成的图片](file://[路径])
```

## 注意事项

- API Key必须保密，不要提交到代码仓库
- 生成失败时检查API Key是否有效
- 大批量生成注意API调用限制
- 保存的图片建议用时间戳命名避免覆盖

## 相关文档

- [API参考文档](references/api-reference.md)
- [设置指南](references/setup-guide.md)
- [英文版本](SKILL.md)
