#!/bin/bash
# 广告内容审核技能安装脚本

set -e

echo "🚀 开始安装广告内容审核技能..."
echo "========================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python版本: $PYTHON_VERSION"

# 检查依赖
echo "📦 检查Python依赖..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "安装requests库..."
    pip install requests
else
    echo "✅ requests库已安装"
fi

# 设置环境变量
echo "🔧 设置环境变量..."
if [ -z "$MAAS_API_KEY" ]; then
    echo "⚠️ 警告: MAAS_API_KEY环境变量未设置"
    echo "请执行以下命令设置:"
    echo "  export MAAS_API_KEY=\"your_huaweicloud_maas_api_key\""
    echo "或添加到 ~/.bashrc 或 ~/.zshrc:"
    echo "  echo 'export MAAS_API_KEY=\"your_huaweicloud_maas_api_key\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
else
    echo "✅ MAAS_API_KEY已设置"
fi

# 创建必要的目录
echo "📁 创建日志目录..."
mkdir -p logs
mkdir -p reports

# 测试技能
echo "🧪 测试技能功能..."
if python3 test_audit.py --help &> /dev/null; then
    echo "✅ 测试脚本正常"
else
    echo "❌ 测试脚本异常"
fi

# 显示使用说明
echo ""
echo "========================================"
echo "🎉 广告内容审核技能安装完成！"
echo "========================================"
echo ""
echo "📋 使用说明:"
echo ""
echo "1. 在OpenClaw中使用:"
echo "   发送 '广告审核'、'合规检查'、'违禁词检测' 等关键词"
echo "   或上传广告图片自动触发"
echo ""
echo "2. 命令行使用:"
echo "   python3 advertising_audit.py \"广告文案\" [图片路径...]"
echo ""
echo "3. Python API使用:"
echo "   from advertising_audit import AdvertisingContentAudit"
echo "   auditor = AdvertisingContentAudit(api_key=\"your_key\")"
echo "   report = auditor.process(\"广告文案\", [\"image1.jpg\"])"
echo ""
echo "4. 集成到OpenClaw:"
echo "   技能已自动注册，触发关键词:"
echo "   - 广告审核"
echo "   - 合规检查"
echo "   - 违禁词检测"
echo "   - 公关稿审核"
echo "   - 海报检查"
echo "   - 广告图合规"
echo ""
echo "🔧 配置说明:"
echo "   编辑 config.yaml 调整审核规则"
echo "   设置 MAAS_API_KEY 环境变量用于OCR"
echo ""
echo "📚 文档:"
echo "   README.md - 基本使用指南"
echo "   SKILL.md - 技能详细说明"
echo "   example_usage.md - 使用示例"
echo "   USER.md - 用户指南"
echo ""
echo "⚠️ 注意: 请确保已设置 MAAS_API_KEY 环境变量"
echo "========================================"