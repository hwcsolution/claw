# 华为云MaaS API参考

## API端点

```
POST https://api.modelarts-maas.com/v1/images/generations
```

## 请求头

```
Content-Type: application/json
Authorization: Bearer {api_key}
```

## 请求体

```json
{
  "model": "qwen-image",
  "prompt": "图片描述",
  "size": "1024x1024",
  "response_format": "b64_json",
  "seed": 1
}
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称，固定为 qwen-image |
| prompt | string | 是 | 图片描述，支持中英文 |
| size | string | 是 | 图片尺寸，如 1024x1024 |
| response_format | string | 是 | 返回格式，暂仅支持 b64_json |
| seed | integer | 否 | 随机种子，范围[0, 2147483648]，默认1 |

## 响应格式

```json
{
  "data": [
    {
      "b64_json": "base64编码的图片数据"
    }
  ]
}
```

## 错误响应

```json
{
  "error": {
    "message": "错误信息",
    "type": "错误类型"
  }
}
```

## 常见尺寸

| 用途 | 尺寸 | 比例 |
|------|------|------|
| 小红书竖图 | 768x1024 | 3:4 |
| 小红书方图 | 1024x1024 | 1:1 |
| 横图 | 1024x768 | 4:3 |
| 宽屏 | 1024x576 | 16:9 |
| 手机竖屏 | 576x1024 | 9:16 |

## Prompt技巧

### 好的Prompt要素

1. **主体**：明确描述主要内容
2. **风格**：指定艺术风格
3. **场景**：描述环境背景
4. **光线**：说明光线条件
5. **细节**：添加具体细节

### 示例

**简单**：
```
一只奔跑的猫
```

**详细**：
```
一只橘色的小猫在草地上奔跑，阳光明媚，照片风格，高清细节
```

**小红书风格**：
```
护肤品瓶子放在白色大理石桌面上，简约风格，自然光，俯拍角度，高级感，适合小红书封面
```

## 限制说明

- 单次生成一张图片
- 返回格式仅支持base64
- 注意API调用频率限制
- API Key需保密
