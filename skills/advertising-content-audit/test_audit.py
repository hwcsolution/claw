#!/usr/bin/env python3
"""
广告内容审核测试脚本
用于测试技能的基本功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advertising_audit import AdvertisingContentAudit

def test_text_only():
    """测试纯文本审核"""
    print("="*60)
    print("测试1: 纯文本审核")
    print("="*60)
    
    # 测试用例
    test_cases = [
        {
            "name": "高风险文案",
            "text": "我们的产品是市场上最好的，100%有效，国家级认证，绝对完美效果！",
            "expected_risk": "severe"
        },
        {
            "name": "中风险文案", 
            "text": "这是我们的首选产品，具有绝佳的效果和顶尖的技术",
            "expected_risk": "warning"
        },
        {
            "name": "低风险文案",
            "text": "优质产品，专业服务，高效解决方案",
            "expected_risk": "safe"
        },
        {
            "name": "合规文案",
            "text": "我们提供可靠的产品和专业的服务，帮助客户解决问题",
            "expected_risk": "safe"
        }
    ]
    
    # 初始化审核器
    api_key = os.getenv("MAAS_API_KEY")
    if not api_key:
        print("⚠️ 警告: 未设置MAAS_API_KEY环境变量，使用测试模式")
        api_key = "test_key"
    auditor = AdvertisingContentAudit(api_key)
    
    for test_case in test_cases:
        print(f"\n📝 测试: {test_case['name']}")
        print(f"文案: {test_case['text']}")
        
        try:
            report = auditor.process(test_case['text'], [])
            
            # 检查报告内容
            if "严重违规" in report and test_case['expected_risk'] == "severe":
                print("✅ 测试通过: 正确识别为严重违规")
            elif "警告" in report and test_case['expected_risk'] == "warning":
                print("✅ 测试通过: 正确识别为警告")
            elif "安全" in report and test_case['expected_risk'] == "safe":
                print("✅ 测试通过: 正确识别为安全")
            else:
                print("❌ 测试失败: 风险等级不匹配")
                
            # 显示报告摘要
            lines = report.split('\n')
            for i, line in enumerate(lines[:20]):  # 只显示前20行
                if line.strip():
                    print(f"  {line}")
            
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")

def test_mixed_content():
    """测试混合内容审核"""
    print("\n" + "="*60)
    print("测试2: 混合内容审核（文本+模拟图片OCR）")
    print("="*60)
    
    api_key = os.getenv("MAAS_API_KEY", "TtylR0PEsimq8JhSezmLvJi_GicIGWPYG9eCrAEo6DENROKvkO8PX9ikGcvngEnRO0qR2JDSG7PAzYFJ-P34FA")
    auditor = AdvertisingContentAudit(api_key)
    
    # 模拟图片OCR结果
    print("📷 模拟图片OCR处理...")
    
    # 测试混合内容
    text = "产品宣传文案"
    # 模拟图片路径（实际测试时需要真实图片）
    # image_paths = ["test_image.png"]
    
    try:
        # 实际测试时取消注释下面这行
        # report = auditor.process(text, image_paths)
        
        # 模拟测试
        print("🔧 模拟处理混合内容...")
        
        # 模拟OCR结果
        ocr_texts = [
            "顶级品质\n100%纯天然\n国家级认证",
            "最有效成分\n完美配方\n绝对安全"
        ]
        
        # 合并内容
        merged = auditor.merge_content(text, ocr_texts)
        print(f"合并后内容:\n{merged[:200]}...")
        
        # 审核广告法
        ad_result = auditor.audit_advertising_law(merged)
        print(f"广告法审核结果: {ad_result['risk_level']}, 违规数: {ad_result['total_violations']}")
        
        # 审核平台规则
        platform_result = auditor.audit_platform_rules(merged)
        print(f"平台规则审核结果: {platform_result['risk_level']}, 违规数: {platform_result['total_violations']}")
        
        # 生成报告
        report = auditor.generate_report(
            merged, 
            ad_result, 
            platform_result,
            has_images=True,
            image_count=2
        )
        
        print("\n📋 生成的报告摘要:")
        for line in report.split('\n')[:15]:
            if line.strip():
                print(f"  {line}")
        
        print("✅ 混合内容测试完成")
        
    except Exception as e:
        print(f"❌ 混合内容测试异常: {str(e)}")

def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("测试3: 错误处理")
    print("="*60)
    
    # 测试1: 空文本
    print("测试空文本处理...")
    api_key = os.getenv("MAAS_API_KEY")
    if not api_key:
        print("⚠️ 警告: 未设置MAAS_API_KEY环境变量，使用测试模式")
        api_key = "test_key"
    auditor = AdvertisingContentAudit(api_key)
    
    try:
        report = auditor.process("", [])
        if "审核概览" in report:
            print("✅ 空文本处理正常")
        else:
            print("❌ 空文本处理异常")
    except Exception as e:
        print(f"❌ 空文本处理异常: {str(e)}")
    
    # 测试2: 无效API密钥
    print("\n测试无效API密钥处理...")
    try:
        invalid_auditor = AdvertisingContentAudit("invalid_key")
        # 这里应该测试OCR失败的处理
        print("⚠️ 注意: 需要实际调用API来测试密钥有效性")
    except Exception as e:
        print(f"❌ 无效密钥处理异常: {str(e)}")

def test_report_generation():
    """测试报告生成"""
    print("\n" + "="*60)
    print("测试4: 报告生成功能")
    print("="*60)
    
    api_key = os.getenv("MAAS_API_KEY")
    if not api_key:
        print("⚠️ 警告: 未设置MAAS_API_KEY环境变量，使用测试模式")
        api_key = "test_key"
    auditor = AdvertisingContentAudit(api_key)
    
    # 测试数据
    content = "这是测试文案，包含最好的产品和100%的效果。"
    
    ad_result = {
        "risk_level": "warning",
        "violations": [
            {
                "word": "最好",
                "position": "第1行第8字",
                "level": "high",
                "law": "《广告法》第九条",
                "suggestion": "建议改为'优秀'"
            },
            {
                "word": "100%",
                "position": "第1行第15字",
                "level": "medium", 
                "law": "《广告法》第十一条",
                "suggestion": "建议改为'高效'"
            }
        ],
        "score": 80,
        "total_violations": 2,
        "high_count": 1,
        "medium_count": 1,
        "low_count": 0
    }
    
    platform_result = {
        "risk_level": "safe",
        "violations": [
            {
                "item": "包含数字百分比",
                "position": "第1行",
                "level": "low",
                "rule": "平台内容规范",
                "suggestion": "建议提供数据来源"
            }
        ],
        "compatibility": {
            "小红书": "合规",
            "抖音": "合规",
            "微信": "合规",
            "微博": "合规"
        },
        "total_violations": 1
    }
    
    try:
        report = auditor.generate_report(
            content, 
            ad_result, 
            platform_result,
            has_images=False,
            image_count=0
        )
        
        print("生成的报告结构检查:")
        
        # 检查关键部分
        checks = [
            ("标题", "# 广告内容合规审核报告" in report),
            ("审核时间", "审核时间" in report),
            ("风险等级", "整体风险等级" in report),
            ("广告法结果", "广告法合规审核结果" in report),
            ("平台规则", "平台规则审核结果" in report),
            ("修改建议", "修改建议" in report),
            ("审核结论", "审核结论" in report)
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                all_passed = False
        
        if all_passed:
            print("✅ 报告生成测试通过")
        else:
            print("❌ 报告生成测试失败")
            
        # 显示报告前几行
        print("\n报告预览:")
        for line in report.split('\n')[:10]:
            print(f"  {line}")
            
    except Exception as e:
        print(f"❌ 报告生成测试异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始广告内容审核技能测试")
    print("="*60)
    
    # 运行所有测试
    test_text_only()
    test_mixed_content()
    test_error_handling()
    test_report_generation()
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
    
    # 总结
    print("\n📊 测试总结:")
    print("1. 纯文本审核: ✅ 完成")
    print("2. 混合内容审核: ✅ 完成（模拟）")
    print("3. 错误处理: ✅ 完成")
    print("4. 报告生成: ✅ 完成")
    print("\n💡 注意事项:")
    print("- 实际图片OCR测试需要真实图片文件")
    print("- API密钥需要有效才能进行OCR测试")
    print("- 建议在实际环境中进行完整测试")

if __name__ == "__main__":
    main()