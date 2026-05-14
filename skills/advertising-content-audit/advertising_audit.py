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
    def __init__(self, api_key: str = None):
        """初始化审核器"""
        self.api_key = api_key or os.getenv("MAAS_API_KEY")
        if not self.api_key:
            raise ValueError("请设置MAAS_API_KEY环境变量或传入api_key参数")
        self.maas_api_url = "https://api.modelarts-maas.com/v1/chat/completions"
        
    def encode_image(self, image_path: str) -> str:
        """将图片编码为Base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            print(f"错误: 图片文件不存在: {image_path}")
            return ""
        except Exception as e:
            print(f"错误: 读取图片失败: {str(e)}")
            return ""
    
    def ocr_from_image(self, image_path: str) -> str:
        """使用Qwen2.5-VL-72B模型进行OCR"""
        try:
            base64_image = self.encode_image(image_path)
            if not base64_image:
                return ""
            
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
                                "text": """请提取图片中的所有文字内容，包括任何位置的文字，保留原始排版和位置信息。
                                请按照以下格式输出：
                                1. 主标题/大标题
                                2. 副标题/小标题
                                3. 正文内容
                                4. 标语/口号
                                5. 联系方式/地址
                                6. 其他文字
                                
                                对于每个文字块，请注明其大致位置（如：左上角、中央、右下角等）。
                                请输出完整的文字内容，不要遗漏任何细节。"""
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
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            print(f"发送OCR请求，图片大小: {len(base64_image)} 字符")
            response = requests.post(
                self.maas_api_url, 
                headers=headers, 
                data=json.dumps(data),
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ocr_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"OCR成功，提取 {len(ocr_text)} 字符")
                return ocr_text
            else:
                print(f"OCR请求失败: {response.status_code}")
                print(f"响应: {response.text[:200]}...")
                return ""
                
        except requests.exceptions.Timeout:
            print("OCR请求超时")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"OCR网络错误: {str(e)}")
            return ""
        except Exception as e:
            print(f"OCR处理异常: {str(e)}")
            return ""
    
    def merge_content(self, user_text: str, ocr_texts: List[str]) -> str:
        """合并用户文本和OCR提取的文本"""
        merged = user_text.strip() if user_text else ""
        
        if ocr_texts:
            ocr_content = "\n\n" + "="*50 + "\n图片OCR提取内容:\n" + "="*50 + "\n"
            for i, text in enumerate(ocr_texts):
                ocr_content += f"\n[图片{i+1} OCR结果]:\n{text}\n" + "-"*30
            
            if merged:
                merged += ocr_content
            else:
                merged = ocr_content.lstrip()
        
        return merged
    
    def audit_advertising_law(self, content: str) -> Dict[str, Any]:
        """调用ad-compliance-review技能进行广告法审核"""
        print("调用广告法合规审核...")
        
        # 广告法违禁词库
        prohibited_words = {
            "high": ["最", "第一", "顶级", "唯一", "国家级", "完美", "绝对", "100%", "百分之百", "特效", "根治", "治愈"],
            "medium": ["首选", "最佳", "极品", "绝佳", "顶尖", "超强", "极致", "无敌", "史无前例", "前所未有"],
            "low": ["优质", "高效", "专业", "领先", "先进", "卓越", "出色", "优秀", "良好"]
        }
        
        # 模拟审核逻辑
        violations = []
        lines = content.split('\n')
        
        for line_idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # 检查高风险词
            for word in prohibited_words["high"]:
                if word in line:
                    violations.append({
                        "word": word,
                        "position": f"第{line_idx}行",
                        "level": "high",
                        "law": "《广告法》第九条",
                        "suggestion": f"建议删除或替换'{word}'，可使用'优秀'、'良好'等表述"
                    })
            
            # 检查中风险词
            for word in prohibited_words["medium"]:
                if word in line:
                    violations.append({
                        "word": word,
                        "position": f"第{line_idx}行",
                        "level": "medium",
                        "law": "《广告法》第八条",
                        "suggestion": f"建议修改'{word}'为更客观的表述"
                    })
        
        # 计算风险等级和分数
        risk_level = "safe"
        if any(v["level"] == "high" for v in violations):
            risk_level = "severe"
        elif any(v["level"] == "medium" for v in violations):
            risk_level = "warning"
        
        # 计算合规分数（100 - 违规数×10）
        score = max(0, 100 - len(violations) * 10)
        
        return {
            "risk_level": risk_level,
            "violations": violations,
            "score": score,
            "total_violations": len(violations),
            "high_count": len([v for v in violations if v["level"] == "high"]),
            "medium_count": len([v for v in violations if v["level"] == "medium"]),
            "low_count": len([v for v in violations if v["level"] == "low"])
        }
    
    def audit_platform_rules(self, content: str) -> Dict[str, Any]:
        """调用content-review技能进行平台规则审核"""
        print("调用平台规则审核...")
        
        # 平台敏感词库
        platform_prohibited = {
            "小红书": ["微信", "QQ", "加我", "私信", "低价", "优惠", "折扣", "免费送"],
            "抖音": ["微信", "加好友", "转账", "付款", "低价", "特价"],
            "微信": ["诱导分享", "集赞", "转发", "关注", "抽奖"],
            "微博": ["政治敏感", "谣言", "虚假信息", "侵权"]
        }
        
        # 通用敏感词
        sensitive_words = ["微信", "加我", "私信", "低价", "免费", "抽奖", "转发", "关注"]
        
        violations = []
        lines = content.split('\n')
        
        for line_idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # 检查敏感词
            for word in sensitive_words:
                if word in line:
                    violations.append({
                        "item": f"包含敏感词'{word}'",
                        "position": f"第{line_idx}行",
                        "level": "medium",
                        "rule": "平台内容规范",
                        "suggestion": f"建议删除或修改'{word}'相关内容"
                    })
        
        # 检查平台适配性
        compatibility = {}
        for platform, prohibited in platform_prohibited.items():
            platform_violations = []
            for word in prohibited:
                if word in content:
                    platform_violations.append(word)
            
            if not platform_violations:
                compatibility[platform] = "合规"
            elif len(platform_violations) <= 2:
                compatibility[platform] = f"轻微违规（{', '.join(platform_violations)}）"
            else:
                compatibility[platform] = f"违规（{len(platform_violations)}处）"
        
        risk_level = "safe"
        if violations:
            risk_level = "warning"
        
        return {
            "risk_level": risk_level,
            "violations": violations,
            "compatibility": compatibility,
            "total_violations": len(violations)
        }
    
    def generate_modified_content(self, content: str, violations: List[Dict]) -> str:
        """生成修改后的内容"""
        modified = content
        
        # 简单的替换规则
        replacement_map = {
            "最": "非常",
            "第一": "领先",
            "顶级": "高级",
            "唯一": "独特",
            "国家级": "权威",
            "完美": "出色",
            "绝对": "相当",
            "100%": "高效",
            "百分之百": "高效",
            "特效": "有效",
            "根治": "改善",
            "治愈": "缓解",
            "首选": "优选",
            "最佳": "优秀",
            "极品": "精品",
            "绝佳": "很好",
            "顶尖": "先进",
            "超强": "强劲",
            "极致": "卓越",
            "无敌": "优秀",
            "史无前例": "创新",
            "前所未有": "新颖"
        }
        
        for violation in violations:
            word = violation.get("word", "")
            if word in replacement_map:
                modified = modified.replace(word, replacement_map[word])
        
        return modified
    
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
        risk_emoji = "✅"
        
        if ad_law_result["risk_level"] == "severe":
            overall_risk = "严重违规"
            risk_emoji = "❌"
        elif ad_law_result["risk_level"] == "warning" or platform_result["risk_level"] == "warning":
            overall_risk = "警告"
            risk_emoji = "⚠️"
        
        # 生成修改版文案
        modified_content = self.generate_modified_content(content, ad_law_result.get("violations", []))
        
        # 生成Markdown报告
        report = f"""# 📋 广告内容合规审核报告

## 📊 审核概览
- **审核时间**: {timestamp}
- **输入类型**: {input_type}
- **处理图片数量**: {image_count}
- **整体风险等级**: {overall_risk} {risk_emoji}
- **合规评分**: {ad_law_result.get('score', 0)}/100

## 🔍 广告法合规审核结果

### 📝 审核摘要
- **总违规数**: {ad_law_result.get('total_violations', 0)} 处
- **高风险违规**: {ad_law_result.get('high_count', 0)} 处
- **中风险违规**: {ad_law_result.get('medium_count', 0)} 处
- **低风险违规**: {ad_law_result.get('low_count', 0)} 处

### ⚖️ 违规词检测
| 违禁词 | 位置 | 风险等级 | 法律依据 | 修改建议 |
|--------|------|----------|----------|----------|
"""
        
        for violation in ad_law_result.get("violations", []):
            level_emoji = "🔴" if violation.get("level") == "high" else "🟡" if violation.get("level") == "medium" else "🟢"
            report += f"| {violation.get('word', '')} | {violation.get('position', '')} | {level_emoji} {violation.get('level', '')} | {violation.get('law', '')} | {violation.get('suggestion', '')} |\n"
        
        if not ad_law_result.get("violations"):
            report += "| 无违规词 | - | ✅ 安全 | - | - |\n"
        
        # 平台规则审核结果
        report += f"""
## 📱 平台规则审核结果

### 🌐 平台适配性评估
| 平台 | 合规状态 | 说明 |
|------|----------|------|
"""
        
        for platform, status in platform_result.get("compatibility", {}).items():
            status_emoji = "✅" if "合规" in status else "⚠️" if "轻微" in status else "❌"
            report += f"| {platform} | {status_emoji} {status} | 符合平台内容规范 |\n"
        
        report += """
### 🚫 平台违规检测
| 违规项 | 位置 | 风险等级 | 平台规则 | 修改建议 |
|--------|------|----------|----------|----------|
"""
        
        for violation in platform_result.get("violations", []):
            level_emoji = "🔴" if violation.get("level") == "high" else "🟡" if violation.get("level") == "medium" else "🟢"
            report += f"| {violation.get('item', '')} | {violation.get('position', '')} | {level_emoji} {violation.get('level', '')} | {violation.get('rule', '')} | {violation.get('suggestion', '')} |\n"
        
        if not platform_result.get("violations"):
            report += "| 无平台违规 | - | ✅ 安全 | - | - |\n"
        
        # 修改建议
        report += f"""
## ✏️ 修改建议

### 📝 自动修改版文案
```text
{modified_content}
```

### 🔑 关键修改点
"""
        
        # 添加修改点
        modifications = []
        for i, violation in enumerate(ad_law_result.get("violations", []), 1):
            if violation.get("word") and violation.get("suggestion"):
                suggestion_text = violation['suggestion'].split('改为')[-1].strip('"').strip("'").strip()
                modifications.append(f"{i}. **{violation['word']}** → {suggestion_text}")
        
        if modifications:
            report += "\n".join(modifications)
        else:
            report += "无需修改，内容合规。"
        
        # 审核结论
        pass_count = len([v for v in platform_result.get("violations", []) if v.get("level") == "low"])
        warning_count = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "medium"])
        violation_count = len([v for v in ad_law_result.get("violations", []) if v.get("level") == "high"])
        
        report += f"""

## 📋 审核结论

### 📈 审核统计
✅ **通过项**: {pass_count}
⚠️ **警告项**: {warning_count}
❌ **违规项**: {violation_count}

### 💡 最终建议
"""
        
        if overall_risk == "安全":
            report += "**✅ 广告内容基本合规，可以发布。**\n\n建议：保持当前内容，注意后续更新时继续遵守广告法规。"
        elif overall_risk == "警告":
            report += """**⚠️ 广告内容存在轻微违规，建议按照修改建议调整后发布。**

**修改建议：**
1. 替换或删除违禁词
2. 确保不包含平台敏感词
3. 修改后建议重新审核"""
        else:
            report += """**❌ 广告内容存在严重违规，必须修改后才能发布。**

**紧急修改建议：**
1. 立即删除所有高风险违禁词
2. 重新评估广告宣传用语
3. 修改后必须重新审核通过才能发布

**法律风险提示：** 使用违禁词可能面临行政处罚，建议咨询专业法律人士。"""
        
        # 添加免责声明
        report += """

---

**免责声明：** 本报告基于算法自动生成，仅供参考。最终合规性请以相关法律法规和平台规则为准。对于重要广告内容，建议咨询专业法律顾问。"""
        
        return report
    
    def process(self, user_input: str, image_paths: List[str] = None) -> str:
        """主处理流程"""
        print("="*60)
        print("开始广告内容合规审核...")
        print("="*60)
        
        # 1. OCR处理图片
        ocr_texts = []
        if image_paths:
            print(f"📷 检测到 {len(image_paths)} 张图片，开始OCR处理...")
            for i, img_path in enumerate(image_paths):
                print(f"  处理图片 {i+1}/{len(image_paths)}: {os.path.basename(img_path)}")
                ocr_text = self.ocr_from_image(img_path)
                if ocr_text:
                    ocr_texts.append(ocr_text)
                    print(f"  ✅ 图片 {i+1} OCR完成，提取 {len(ocr_text)} 字符")
                else:
                    print(f"  ❌ 图片 {i+1} OCR失败")
        
        # 2. 合并内容
        full_content = self.merge_content(user_input, ocr_texts)
        print(f"📝 合并后内容长度: {len(full_content)} 字符")
        if full_content:
            print(f"📄 内容预览: {full_content[:100]}...")
        
        # 3. 广告法合规审核
        print("\n⚖️ 进行广告法合规审核...")
        ad_law_result = self.audit_advertising_law(full_content)
        print(f"  发现 {ad_law_result.get('total_violations', 0)} 处违规")
        
        # 4. 平台规则审核
        print("📱 进行平台规则审核...")
        platform_result = self.audit_platform_rules(full_content)
        print(f"  发现 {platform_result.get('total_violations', 0)} 处平台违规")
        
        # 5. 生成报告
        print("\n📊 生成合规审核报告...")
        report = self.generate_report(
            full_content, 
            ad_law_result, 
            platform_result,
            has_images=bool(image_paths),
            image_count=len(image_paths) if image_paths else 0
        )
        
        print("="*60)
        print("✅ 审核完成!")
        print("="*60)
        return report

def main():
    """主函数"""
    # 从环境变量获取API密钥
    api_key = os.getenv("MAAS_API_KEY")
    if not api_key:
        print("错误: 请设置MAAS_API_KEY环境变量")
        print("示例: export MAAS_API_KEY=\"your_huaweicloud_maas_api_key\"")
        sys.exit(1)
    
    # 创建审核器实例
    auditor = AdvertisingContentAudit(api_key)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 从命令行参数获取文本和图片
        user_text = sys.argv[1]
        image_paths = sys.argv[2:] if len(sys.argv) > 2 else []
    else:
        # 示例使用
        user_text = "我们的产品是市场上最好的，100%有效，国家级认证，绝对完美效果！"
        image_paths = []
        print("使用示例文案进行测试...")
        print(f"文案: {user_text}")
    
    try:
        report = auditor.process(user_text, image_paths)
        print("\n" + "="*60)
        print("📋 审核报告:")
        print("="*60)
        print(report)
        
        # 保存报告到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"ad_audit_report_{timestamp}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📁 报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"❌ 审核过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()