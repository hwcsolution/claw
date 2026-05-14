---
name: huawei-image-gen
description: "Huawei Cloud MaaS text-to-image generation. Triggers: (1) User needs AI image generation (2) Xiaohongshu cover image (3) Says generate image, AI draw. Supports: Qwen-image model, Chinese/English prompts, multiple sizes, base64 output."
---

# huawei-image-gen - Huawei Cloud MaaS Text-to-Image

Generate images using Huawei Cloud MaaS Qwen-image model.

## Prerequisites

### 1. Enable Model Service

Visit Huawei Cloud MaaS Console:
https://console.huaweicloud.com/modelarts/?region=cn-southwest-2#/model-studio/deployment

**Setup Steps**:

![Enable Model](开通模型.png)

1. Login to Huawei Cloud Console
2. Navigate to ModelArts → Model Studio → Model Deployment
3. Search for **Qwen-image** in model gallery
4. Click "Deploy" or "Enable"
5. Wait for deployment to complete

### 2. Get API Key

**Steps**:

![Create API-Key](创建API-Key.png)

1. Go to deployed model details page
2. Click "API Key Management" or "Get Key"
3. Create new API Key
4. Copy and save the API Key (**shown only once**)

### 3. Configure API Key

**Option 1: Environment Variable**
```bash
export MAAS_API_KEY="your-api-key"
```

**Option 2: Config File**
```json
// config/config.json
{
  "maas": {
    "api_key": "your-api-key"
  }
}
```

## Workflow

### Step 1: Receive Image Request

Parameters:
- prompt: Image description (Chinese/English supported)
- size: Image size (default 1024x1024)
- seed: Random seed (optional, default 1)

### Step 2: Build Request

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

### Step 3: Call API and Save

1. Send request to MaaS API
2. Receive base64 encoded image
3. Decode and save to specified directory

### Step 4: Return Result

Output:
- Image save path
- Generation parameters

### Step 5: Send Image to User

Use message tool to send generated image to user:

```python
message(
    action="send",
    media="[image_path]",
    message="Image generated 🖼️"
)
```

**Important**: Must send image to user after generation, don't just save without sending.

## Usage Examples

### Basic Usage
```
User: Generate an image of a running cat

Execute:
1. Call Qwen-image to generate
2. Save image
3. Return image path
```

### Xiaohongshu Cover Image
```
User: Generate a cover image for this skincare post

Execute:
1. Generate prompt based on post content
2. Call API to generate
3. Save to Xiaohongshu image directory
```

### Specify Size
```
User: Generate a 3:4 vertical image, premium skincare photo

Execute:
1. Convert 3:4 to specific size (e.g., 768x1024)
2. Build prompt
3. Generate and save
```

## API Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| model | Model name | qwen-image |
| prompt | Image description | Chinese/English |
| size | Image size | 1024x1024, 512x512, etc. |
| response_format | Response format | b64_json (only supported format) |
| seed | Random seed | 0-2147483648, default 1 |

## Size Mapping

Xiaohongshu common sizes:
- 3:4 vertical → 768x1024
- 1:1 square → 1024x1024
- 4:3 horizontal → 1024x768

## Configuration

API Key configuration methods:

**Option 1: Environment Variable**
```bash
export MAAS_API_KEY="your-api-key"
```

**Option 2: Config File**
```json
// config/config.json
{
  "maas": {
    "api_key": "your-api-key"
  }
}
```

## Output Format

```markdown
## 🖼️ Image Generated

**Prompt**: [prompt content]
**Size**: [size]
**Save Path**: [file path]
**Generation Time**: [time]

![Generated Image](file://[path])
```

## Notes

- Keep API Key confidential, never commit to repository
- Check if API Key is valid when generation fails
- Be aware of API rate limits for bulk generation
- Use timestamp in filename to avoid overwriting

## Related Documentation

- [API Reference](references/api-reference.md)
- [Setup Guide](references/setup-guide.md)
- [Chinese Version](SKILL_CN.md)
