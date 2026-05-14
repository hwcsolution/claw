#!/usr/bin/env python3
"""
简单测试智能知识库功能
"""

import sys
import os

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'scripts'))

from knowledge_db import KnowledgeDatabase
from error_signature import ErrorSignatureExtractor
from intelligent_analyzer import IntelligentAnalyzer

def test_knowledge_db():
    """测试知识库数据库"""
    print("=== 测试知识库数据库 ===")
    
    # 初始化数据库
    db = KnowledgeDatabase('test_simple.db')
    print("✅ 数据库初始化成功")
    
    # 添加测试数据
    solution_id = db.add_solution(
        signature="redis_conn_timeout",
        error_summary="Redis连接超时",
        solution="1. 检查Redis服务状态\n2. 检查网络连接\n3. 调整超时设置",
        category="database",
        severity="ERROR",
        tags=["redis", "connection", "timeout"]
    )
    print(f"✅ 添加解决方案成功，ID: {solution_id}")
    
    # 验证解决方案
    db.verify_solution("redis_conn_timeout", "test-admin", "测试验证")
    print("✅ 解决方案验证成功")
    
    # 搜索解决方案
    results = db.search_solutions("redis")
    print(f"✅ 搜索到 {len(results)} 个解决方案")
    
    # 获取统计信息
    stats = db.get_statistics()
    print(f"✅ 知识库统计: {stats['total_solutions']} 个解决方案")
    
    return True

def test_error_signature():
    """测试错误签名提取"""
    print("\n=== 测试错误签名提取 ===")
    
    extractor = ErrorSignatureExtractor()
    
    # 测试单个错误
    error_text = "java.net.ConnectException: Connection refused"
    signature = extractor.extract_signature(error_text)
    
    print(f"✅ 错误签名提取成功")
    print(f"   原始错误: {error_text}")
    print(f"   签名: {signature.signature}")
    print(f"   类型: {signature.error_type}")
    print(f"   代码: {signature.error_code}")
    print(f"   消息: {signature.error_message}")
    
    # 测试批量提取
    errors = [
        "java.net.ConnectException: Connection refused",
        "MySQLIntegrityConstraintViolationException: Duplicate entry",
        "java.io.IOException: No space left on device"
    ]
    
    signatures = extractor.batch_extract(errors)
    print(f"✅ 批量提取成功，提取了 {len(signatures)} 个签名")
    
    return True

def test_intelligent_analyzer():
    """测试智能分析器"""
    print("\n=== 测试智能分析器 ===")
    
    # 创建测试配置
    config_content = """
database:
  path: "test_intelligent.db"
  auto_backup: false

ai:
  generation:
    min_confidence: 0.5
    auto_confirm: false

workflow:
  analysis:
    extract_signature: true
    search_knowledge_base: true
    generate_if_not_found: true
    require_human_review: false

testing:
  mock_responses: true
"""
    
    # 保存配置
    config_file = "test_config.yaml"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    try:
        # 初始化分析器
        analyzer = IntelligentAnalyzer(config_file)
        print("✅ 智能分析器初始化成功")
        
        # 测试已知错误（应该在知识库中找到）
        print("\n测试1: 分析已知错误")
        result1 = analyzer.analyze_error(
            "Redis connection timeout after 5000ms",
            {"source": "test-redis"}
        )
        print(f"   状态: {result1.get('status')}")
        print(f"   签名: {result1.get('signature')}")
        
        # 测试未知错误（应该触发AI生成）
        print("\n测试2: 分析未知错误")
        result2 = analyzer.analyze_error(
            "CustomApplicationError: Something went wrong in module X",
            {"source": "test-application"}
        )
        print(f"   状态: {result2.get('status')}")
        print(f"   签名: {result2.get('signature')}")
        
        # 获取统计信息
        print("\n测试3: 获取统计信息")
        stats = analyzer.get_statistics()
        print(f"   知识库解决方案: {stats['knowledge_base']['total_solutions']}")
        print(f"   待确认解决方案: {stats['pending_solutions']}")
        
        return True
        
    finally:
        # 清理测试文件
        if os.path.exists(config_file):
            os.remove(config_file)
        if os.path.exists("test_intelligent.db"):
            os.remove("test_intelligent.db")

def main():
    """主测试函数"""
    print("开始智能知识库简单测试")
    print("=" * 50)
    
    tests = [
        ("知识库数据库", test_knowledge_db),
        ("错误签名提取", test_error_signature),
        ("智能分析器", test_intelligent_analyzer),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name}测试通过")
                passed += 1
            else:
                print(f"\n❌ {test_name}测试失败")
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name}测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    
    # 清理测试文件
    for db_file in ["test_simple.db", "test_intelligent.db", "test_config.yaml"]:
        if os.path.exists(db_file):
            os.remove(db_file)
    
    if failed == 0:
        print("\n🎉 所有测试通过！智能知识库功能正常。")
        return 0
    else:
        print("\n⚠️ 有测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())