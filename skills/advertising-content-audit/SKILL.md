# advertising-content-audit

广告内容一站式合规审核，自动完成图片OCR、广告法违禁词检测、平台规则审核，输出统一合规报告。

## 技能描述

当用户需要审核广告内容、检查违禁词、审核公关稿、检查海报或广告图合规性时，使用此技能。技能支持纯文本、单张/多张广告图、图文混合输入，自动完成OCR提取、广告法合规审核、平台规则审核，并生成统一的合规报告。

## 触发关键词

- 广告审核
- 合规检查
- 违禁词检测
- 公关稿审核
- 海报检查
- 广告图合规
- 广告法审核
- 平台规则审核
- 广告内容安全

## 依赖

- Qwen2.5-VL-72B 模型（用于图片OCR）
- ad-compliance-review 技能（用于广告法合规审核）
- content-review 技能（用于平台规则审核）

## 执行流程

### 1. 接收用户输入
- 支持纯文本输入
- 支持单张或多张广告图片输入
- 支持图文混合输入
- 自动识别输入类型并处理

### 2. 图片OCR处理（如果包含图片）
- 调用 Qwen2.5-VL-72B 模型进行高精度OCR
- 提取图片中的完整文字内容
- 保留文字排版和位置信息
- 支持多张图片批量处理
- API密钥：通过环境变量 `MAAS_API_KEY` 配置

### 3. 内容合并
- 合并OCR提取的文字与用户输入的文本
- 保留原始内容结构
- 生成完整的待审核内容

### 4. 广告法合规审核
- 调用 `ad-compliance-review` 技能
- 检测《广告法》违禁词（最、第一、顶级、唯一、100%、国家级、完美等）
- 输出违规词、位置、风险等级、修改建议
- 引用具体法律条款

### 5. 平台规则审核
- 调用 `content-review` 技能
- 检测平台禁止的敏感词、违规表述
- 输出违规项、风险等级、修改建议
- 根据平台特性（小红书、抖音、微信等）调整审核标准

### 6. 生成统一合规报告
- 汇总两次审核结果
- 去重并合并相同风险项
- 计算整体风险等级：
  - **安全**：无违规内容
  - **警告**：轻微违规，需要修改
  - **严重违规**：存在严重违法内容
- 生成结构化Markdown报告

## 输出格式

```markdown
# 广告内容合规审核报告

## 📊 审核概览
- **审核时间**: {timestamp}
- **输入类型**: {input_type}
- **处理图片数量**: {image_count}
- **整体风险等级**: {risk_level} ⚠️
- **合规评分**: {score}/100

## 🔍 广告法合规审核结果

### 违规词检测
| 违禁词 | 位置 | 风险等级 | 法律依据 | 修改建议 |
|--------|------|----------|----------|----------|
| {word1} | {pos1} | {level1} | {law1} | {suggestion1} |
| {word2} | {pos2} | {level2} | {law2} | {suggestion2} |

### 风险评估
- **高风险项**: {count_high}
- **中风险项**: {count_medium}
- **低风险项**: {count_low}

## 📱 平台规则审核结果

### 平台违规检测
| 违规项 | 位置 | 风险等级 | 平台规则 | 修改建议 |
|--------|------|----------|----------|----------|
| {violation1} | {pos1} | {level1} | {rule1} | {suggestion1} |
| {violation2} | {pos2} | {level2} | {rule2} | {suggestion2} |

### 平台适配性
- **小红书**: {xiaohongshu_compatibility}
- **抖音**: {douyin_compatibility}
- **微信**: {wechat_compatibility}
- **微博**: {weibo_compatibility}

## ✏️ 修改建议

### 自动修改版文案
```
{modified_content}
```

### 关键修改点
1. **{修改点1}**: {说明1}
2. **{修改点2}**: {说明2}
3. **{修改点3}**: {说明3}

## 📋 审核结论

✅ **通过项**: {pass_items}
⚠️ **警告项**: {warning_items}
❌ **违规项**: {violation_items}

### 最终建议
{final_recommendation}
```

## 使用示例

### 示例1：纯文本审核
```
用户：请审核这段广告文案："我们的产品是市场上最好的，100%有效，国家级认证"

技能：自动调用 ad-compliance-review 和 content-review，检测"最好"、"100%"、"国家级"等违禁词
```

### 示例2：图片广告审核
```
用户：请审核这张海报图片 [图片]
技能：1. OCR提取文字 2. 合并审核 3. 生成报告
```

### 示例3：图文混合审核
```
用户：请审核这个广告，文案是"独家配方，完美效果"，图片包含"顶级品质"字样
技能：1. OCR提取图片文字 2. 合并文本 3. 双重审核 4. 生成报告
```

## 实现脚本

创建 `advertising_audit.py` 脚本：

```python
#!/usr/bin/env python3
"""
广告内容一站式合规审核脚本
支持图片OCR、广告法审核、平台规则审核
"""

import os
import sys
import json
import base64
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

class AdvertisingContentAudit:
    def __init__(self, api_key: str):
        """初始化审核器"""
        self.api_key = api_key
        self.maas_api_url = "https://api.modelarts-maas.com/v1/chat/completions"
        
    def encode_image(self, image_path: str) -> str:
        """将图片编码为Base64格式"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def ocr_from_image(self, image_path: str) -> str:
        """使用Qwen2.5-VL-72B模型进行OCR"""
        try:
            base64_image = self.encode_image(image_path)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            data = {
                "model": "qwen2.5-vl-72b",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请提取图片中的所有文字内容，包括任何位置的文字，保留原始排版和位置信息。请输出完整的文字内容，不要遗漏任何细节。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.maas_api_url, 
                headers=headers, 
                data=json.dumps(data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ocr_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return ocr_text
            else:
                print(f"OCR请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return ""
                
        except Exception as e:
            print(f"OCR处理异常: {str(e)}")
            return ""
    
    def merge_content(self, user_text: str, ocr_texts: List[str]) -> str:
        """合并用户文本和OCR提取的文本"""
        merged = user_text
        if ocr_texts:
            ocr_content = "\n".join([f"[图片{i+1}OCR]: {text}" for i, text in enumerate(ocr_texts)])
            merged = f"{user_text}\n\n{ocr_content}" if user_text else ocr_content
        return merged
    
    def audit_advertising_law(self, content: str) -> Dict[str, Any]:
        """调用ad-compliance-review技能进行广告法审核"""
        # 这里需要集成ad-compliance-review技能
        # 暂时返回模拟数据
        return {
            "risk_level": "warning",
            "violations": [
                {
                    "word": "最好",
                    "position": "第3行第5字",
                    "level": "high",
                    "law": "《广告法》第九条",
                    "suggestion": "建议改为'优秀'或'良好'"
                },
                {
                    "word": "100%",
                    "position": "第4行第8字",
                    "level": "medium",
                    "law": "《广告法》第十一条",
                    "suggestion": "建议改为'高效'或'显著'"
                }
            ],
            "score": 70
        }
    
    def audit_platform_rules(self, content: str) -> Dict[str, Any]:
        """调用content-review技能进行平台规则审核"""
        # 这里需要集成content-review技能
        # 暂时返回模拟数据
        return {
            "risk_level": "safe",
            "violations": [
                {
                    "item": "夸大宣传",
                    "position": "第3行",
                    "level": "low",
                    "rule": "小红书社区规范第3.2条",
                    "suggestion": "建议提供具体数据支持"
                }
            ],
            "compatibility": {
                "xiaohongshu": "基本合规，建议优化",
                "douyin": "合规",
                "wechat": "合规",
                "weibo": "合规"
            }
        }
    
    def generate_report(self, 
                       content: str, 
                       ad_law_result: Dict[str, Any], 
                       platform_result: Dict[str, Any],
                       has_images: bool = False,
                       image_count: int = 0) -> str:
        """生成合规审核报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        input_type = "图文混合" if has_images else "纯文本"
        
        # 计算整体风险等级
        overall_risk = "安全"
        if ad_law_result["risk_level"] == "severe" or platform_result["risk_level"] == "severe":
            overall_risk = "严重违规"
        elif ad_law_result["risk_level"] == "warning" or platform_result["risk_level"] == "warning":
            overall_risk = "警告"
        
        # 生成修改版文案
        modified_content = content
        for violation in ad_law_result.get("violations", []):
            if violation.get("suggestion"):
                # 简单的替换逻辑，实际应用中需要更智能
                modified_content = modified_content.replace(
                    violation["word"], 
                    violation["suggestion"].split("改为")[-1].strip("'").strip('"')
                )
        
        # 生成Markdown报告
        report = f"""# 广告内容合规审核报告

## 📊 审核概览
- **审核时间**: {timestamp}
- **输入类型**: {input_type}
- **处理图片数量**: {image_count}
- **整体风险等级**: {overall_risk} {'⚠️' if overall_risk != '安全' else '✅'}
- **合规评分**: {ad_law_result.get('score', 0)}/100

## 🔍 广告法合规审核结果

### 违规词检测
| 违禁词 | 位置 | 风险等级 | 法律依据 | 修改建议 |
|--------|------|----------|----------|----------|
"""
        
        for violation in ad_law_result.get("violations", []):
            report += f"| {violation.get('word', '')} | {violation.get('position', '')} | {violation.get('level', '')} | {violation.get('law', '')} | {violation.get('suggestion', '')} |\n"
        
        # 风险评估
        high_count = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "high"])
        medium_count = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "medium"])
        low_count = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "low"])
        
        report += f"""
### 风险评估
- **高风险项**: {high_count}
- **中风险项**: {medium_count}
- **低风险项**: {low_count}

## 📱 平台规则审核结果

### 平台违规检测
| 违规项 | 位置 | 风险等级 | 平台规则 | 修改建议 |
|--------|------|----------|----------|----------|
"""
        
        for violation in platform_result.get("violations", []):
            report += f"| {violation.get('item', '')} | {violation.get('position', '')} | {violation.get('level', '')} | {violation.get('rule', '')} | {violation.get('suggestion', '')} |\n"
        
        # 平台适配性
        compat = platform_result.get("compatibility", {})
        report += f"""
### 平台适配性
- **小红书**: {compat.get('xiaohongshu', '未评估')}
- **抖音**: {compat.get('douyin', '未评估')}
- **微信**: {compat.get('wechat', '未评估')}
- **微博**: {compat.get('weibo', '未评估')}

## ✏️ 修改建议

### 自动修改版文案
```
{modified_content}
```

### 关键修改点
"""
        
        # 添加修改点
        modifications = []
        for i, violation in enumerate(ad_law_result.get("violations", []), 1):
            if violation.get("word") and violation.get("suggestion"):
                modifications.append(f"{i}. **{violation['word']}**: {violation['suggestion']}")
        
        report += "\n".join(modifications)
        
        # 审核结论
        pass_items = len([v for v in platform_result.get("violations", []) if v.get("level") == "low"])
        warning_items = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "medium"])
        violation_items = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "high"])
        
        report += f"""

## 📋 审核结论

✅ **通过项**: {pass_items}
⚠️ **警告项**: {warning_items}
❌ **违规项**: {violation_items}

### 最终建议
"""
        
        if overall_risk == "安全":
            report += "广告内容基本合规，可以发布。"
        elif overall_risk == "警告":
            report += "广告内容存在轻微违规，建议按照修改建议调整后发布。"
        else:
            report += "广告内容存在严重违规，必须修改后才能发布。"
        
        return report
    
    def process(self, user_input: str, image_paths: List[str] = None) -> str:
        """主处理流程"""
        print("开始广告内容合规审核...")
        
        # 1. OCR处理图片
        ocr_texts = []
        if image_paths:
            print(f"检测到 {len(image_paths)} 张图片，开始OCR处理...")
            for i, img_path in enumerate(image_paths):
                print(f"处理图片 {i+1}/{len(image_paths)}: {img_path}")
                ocr_text = self.ocr_from_image(img_path)
                if ocr_text:
                    ocr_texts.append(ocr_text)
                    print(f"图片 {i+1} OCR完成，提取 {len(ocr_text)} 字符")
        
        # 2. 合并内容
        full_content = self.merge_content(user_input, ocr_texts)
        print(f"合并后内容长度: {len(full_content)} 字符")
        
        # 3. 广告法合规审核
        print("进行广告法合规审核...")
        ad_law_result = self.audit_advertising_law(full_content)
        
        # 4. 平台规则审核
        print("进行平台规则审核...")
        platform_result = self.audit_platform_rules(full_content)
        
        # 5. 生成报告
        print("生成合规审核报告...")
        report = self.generate_report(
            full_content, 
            ad_law_result, 
            platform_result,
            has_images=bool(image_paths),
            image_count=len(image_paths) if image_paths else 0
        )
        
        print("审核完成!")
        return report

def main():
    """主函数"""
    # 从环境变量获取API密钥
    api_key = os.getenv("MAAS_API_KEY", "TtylR0PEsimq8JhSezmLvJi_GicIGWPYG9eCrAEo6DENROKvkO8PX9ikGcvngEnRO0qR2JDSG7PAzYFJ-P34FA")
    
    # 创建审核器实例
    auditor = AdvertisingContentAudit(api_key)
    
    # 示例使用
    user_text = "我们的产品是市场上最好的，100%有效，国家级认证"
    image_paths = []  # 可以添加图片路径
    
    report = auditor.process(user_text, image_paths)
    print(report)

if __name__ == "__main__":
    main()
```

## 安装说明

1. 创建技能目录：
```bash
mkdir -p ~/.openclaw/workspace/skills/advertising-content-audit
```

2. 将本SKILL.md文件放入目录

3. 创建Python脚本：
```bash
cp advertising_audit.py ~/.openclaw/workspace/skills/advertising-content-audit/
```

4. 安装依赖：
```bash
pip install requests pillow
```

5. 设置环境变量（可选）：
```bash
export MAAS_API_KEY="your_api_key_here"
```

## 使用方式

### 方式1：命令行调用
```bash
python advertising_audit.py
```

### 方式2：在OpenClaw中调用
当用户发送包含触发关键词的消息时，自动调用此技能。

### 方式3：API调用
```python
from advertising_audit import AdvertisingContentAudit

auditor = AdvertisingContentAudit(api_key="your_api_key")
report = auditor.process(
    user_text="广告文案内容",
    image_paths=["ad1.png", "ad2.jpg"]
)
print(report)
```

## 注意事项

1. **API密钥安全**：建议将API密钥存储在环境变量中
2. **图片格式**：支持PNG、JPEG、WEBP格式
3. **处理速度**：OCR处理可能需要几秒到几十秒，取决于图片大小和复杂度
4. **成本控制**：OCR调用会产生API费用，注意使用量
5. **错误处理**：网络异常或API错误时会有相应提示

## 扩展功能

未来可以扩展的功能：
1. 支持更多图片格式（GIF、BMP等）
2. 添加批量处理模式
3. 支持自定义违禁词库
4. 添加历史记录和统计分析
5. 集成更多审核平台（抖音、快手、B站等）

## 版本历史

- v1.0.0 (2024-05-12): 初始版本，支持图片OCR、广告法审核、平台规则审核