# 广告内容审核技能使用示例

## 快速开始

### 1. 基本使用
```python
from advertising_audit import AdvertisingContentAudit

# 初始化审核器
auditor = AdvertisingContentAudit(api_key="your_api_key")

# 审核纯文本
report = auditor.process("我们的产品是市场上最好的，100%有效")
print(report)

# 审核文本+图片
report = auditor.process(
    "产品宣传文案",
    ["advertisement.png", "poster.jpg"]
)
print(report)
```

### 2. 命令行使用
```bash
# 审核纯文本
python advertising_audit.py "顶级品质，国家级认证"

# 审核多张图片
python advertising_audit.py "" ad1.png ad2.jpg ad3.webp

# 审核图文混合
python advertising_audit.py "宣传文案" image1.png image2.jpg
```

## 使用场景示例

### 场景1：电商广告审核
```python
text = """
🔥限时特惠！我们的面膜是市面上最好的！
💯100%纯天然成分，国家级专利技术
✨使用后皮肤完美无瑕，绝对有效！
📞立即购买：13800138000
"""

auditor = AdvertisingContentAudit(api_key="your_key")
report = auditor.process(text)
```

### 场景2：社交媒体海报审核
```python
# 假设有海报图片 poster.png 包含文字：
# "独家配方"
# "最有效成分"
# "立即加微信咨询"

auditor = AdvertisingContentAudit(api_key="your_key")
report = auditor.process("", ["poster.png"])
```

### 场景3：公关稿审核
```python
pr_content = """
关于我公司新产品发布的新闻稿

我公司最新研发的XX产品，采用全球顶尖技术，
是国内唯一获得国际认证的产品。
产品效果显著，用户满意度达到100%，
是行业的首选解决方案。
"""

auditor = AdvertisingContentAudit(api_key="your_key")
report = auditor.process(pr_content)
```

## 输出示例

### 示例报告输出
```markdown
# 📋 广告内容合规审核报告

## 📊 审核概览
- **审核时间**: 2024-05-12 15:30:25
- **输入类型**: 纯文本
- **处理图片数量**: 0
- **整体风险等级**: 警告 ⚠️
- **合规评分**: 70/100

## 🔍 广告法合规审核结果

### 📝 审核摘要
- **总违规数**: 3 处
- **高风险违规**: 2 处
- **中风险违规**: 1 处
- **低风险违规**: 0 处

### ⚖️ 违规词检测
| 违禁词 | 位置 | 风险等级 | 法律依据 | 修改建议 |
|--------|------|----------|----------|----------|
| 最好 | 第1行 | 🔴 high | 《广告法》第九条 | 建议删除或替换'最好'，可使用'优秀'、'良好'等表述 |
| 100% | 第2行 | 🔴 high | 《广告法》第十一条 | 建议修改'100%'为更客观的表述 |
| 唯一 | 第3行 | 🟡 medium | 《广告法》第九条 | 建议修改'唯一'为'独特'或'创新' |

## 📱 平台规则审核结果

### 🌐 平台适配性评估
| 平台 | 合规状态 | 说明 |
|------|----------|------|
| 小红书 | ⚠️ 轻微违规（微信） | 包含联系方式 |
| 抖音 | ⚠️ 轻微违规（微信） | 包含联系方式 |
| 微信 | ✅ 合规 | 符合平台内容规范 |
| 微博 | ✅ 合规 | 符合平台内容规范 |

## ✏️ 修改建议

### 📝 自动修改版文案
```
🔥限时特惠！我们的面膜是市面上优秀的！
💯高效纯天然成分，权威专利技术
✨使用后皮肤效果出色，相当有效！
📞立即购买：13800138000
```

## 📋 审核结论

### 📈 审核统计
✅ **通过项**: 1
⚠️ **警告项**: 1
❌ **违规项**: 2

### 💡 最终建议
**⚠️ 广告内容存在轻微违规，建议按照修改建议调整后发布。**

**修改建议：**
1. 替换或删除违禁词
2. 确保不包含平台敏感词
3. 修改后建议重新审核
```

## 集成到OpenClaw

### 1. 在OpenClaw中调用
当用户发送以下类型消息时自动触发：
- "请审核这个广告"
- "检查一下这个文案是否合规"
- "帮我看看这个海报有没有违禁词"
- "广告法审核"
- "合规检查"

### 2. 作为子技能调用
```python
# 在其他技能中调用广告审核
from advertising_audit import AdvertisingContentAudit

def some_other_skill():
    # ... 其他处理逻辑
    
    # 调用广告审核
    auditor = AdvertisingContentAudit(api_key="your_key")
    audit_report = auditor.process(user_content, image_paths)
    
    # 使用审核结果
    if "严重违规" in audit_report:
        return "广告内容存在严重违规，请修改后再提交。"
    else:
        return f"审核完成：\n{audit_report}"
```

## 高级配置

### 1. 自定义违禁词
修改 `advertising_audit.py` 中的 `prohibited_words`：
```python
prohibited_words = {
    "high": ["最", "第一", "顶级", ...],  # 添加你的高风险词
    "medium": ["首选", "最佳", ...],      # 添加你的中风险词
    "low": ["优质", "高效", ...]          # 添加你的低风险词
}
```

### 2. 自定义平台规则
修改 `platform_prohibited`：
```python
platform_prohibited = {
    "小红书": ["微信", "QQ", ...],
    "抖音": ["微信", "加好友", ...],
    # 添加其他平台
}
```

### 3. 环境变量配置
```bash
# 设置API密钥
export MAAS_API_KEY="your_api_key_here"

# 设置日志级别
export AUDIT_LOG_LEVEL="DEBUG"

# 设置缓存目录
export AUDIT_CACHE_DIR="/tmp/audit_cache"
```

## 错误处理

### 常见错误及解决方案
1. **API密钥错误**
   ```
   ❌ OCR请求失败: 401
   ```
   解决方案：检查API密钥是否正确，是否有足够余额

2. **图片读取失败**
   ```
   ❌ 错误: 图片文件不存在: ad.png
   ```
   解决方案：检查文件路径和权限

3. **网络超时**
   ```
   ❌ OCR请求超时
   ```
   解决方案：增加超时时间或检查网络连接

4. **内存不足**
   ```
   ❌ 内存不足，无法处理大图片
   ```
   解决方案：压缩图片或增加系统内存

## 性能优化建议

1. **批量处理**：一次性审核多个广告内容
2. **缓存结果**：相同内容只审核一次
3. **图片压缩**：大图片先压缩再OCR
4. **异步处理**：长时间操作使用异步
5. **增量审核**：只审核修改部分

## 监控和日志

### 日志文件
审核日志保存在 `logs/audit.log`，包含：
- 处理时间
- 输入内容摘要
- 审核结果
- 错误信息

### 性能监控
```python
import time

start_time = time.time()
report = auditor.process(content, images)
end_time = time.time()

print(f"处理时间: {end_time - start_time:.2f}秒")
print(f"内容长度: {len(content)}字符")
print(f"图片数量: {len(images)}张")
```

## 最佳实践

1. **预处理内容**：先清理不必要的空格和格式
2. **分批处理**：大量内容分批审核避免超时
3. **结果缓存**：相同内容缓存审核结果
4. **定期更新**：定期更新违禁词库和平台规则
5. **人工复核**：重要内容建议人工复核

## 扩展开发

### 添加新审核规则
```python
class CustomAdvertisingAudit(AdvertisingContentAudit):
    def audit_custom_rules(self, content: str) -> Dict[str, Any]:
        """添加自定义审核规则"""
        violations = []
        
        # 你的自定义审核逻辑
        if "自定义违禁词" in content:
            violations.append({
                "word": "自定义违禁词",
                "position": "检测位置",
                "level": "high",
                "rule": "自定义规则",
                "suggestion": "修改建议"
            })
        
        return {
            "risk_level": "severe" if violations else "safe",
            "violations": violations
        }
    
    def process(self, user_input: str, image_paths: List[str] = None) -> str:
        # 原有处理流程
        report = super().process(user_input, image_paths)
        
        # 添加自定义审核
        custom_result = self.audit_custom_rules(user_input)
        
        # 合并到报告
        # ... 合并逻辑
        
        return enhanced_report
```

### 集成其他审核服务
```python
def integrate_third_party_audit(content: str):
    """集成第三方审核服务"""
    # 调用第三方API
    # 解析结果
    # 合并到审核报告
    pass
```

## 支持与反馈

如有问题或建议：
1. 查看日志文件 `logs/audit.log`
2. 运行测试脚本 `python test_audit.py`
3. 提交Issue到GitHub仓库
4. 联系技术支持邮箱