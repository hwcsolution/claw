#!/usr/bin/env python3
"""
智能知识库管理器
提供命令行接口，整合知识库、错误签名提取和AI生成功能
"""

import os
import sys
import json
import argparse
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from knowledge_db import KnowledgeDatabase
from error_signature import ErrorSignatureExtractor
from ai_solution_generator import AISolutionGenerator
from intelligent_analyzer import IntelligentAnalyzer


class IntelligentKnowledgeManager:
    """智能知识库管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or (SCRIPT_DIR.parent / "config" / "intelligent-analyzer.yaml")
        self.analyzer = IntelligentAnalyzer(str(self.config_path))
    
    def add_solution(self, signature: str, error_summary: str, solution: str, 
                    category: str = None, severity: str = None, 
                    tags: List[str] = None, verified: bool = False,
                    verified_by: str = None) -> Dict[str, Any]:
        """
        添加解决方案到知识库
        
        Args:
            signature: 错误签名
            error_summary: 错误摘要
            solution: 解决方案
            category: 分类
            severity: 严重级别
            tags: 标签列表
            verified: 是否已验证
            verified_by: 验证人
            
        Returns:
            添加结果
        """
        # 添加到知识库
        solution_id = self.analyzer.knowledge_db.add_solution(
            signature=signature,
            error_summary=error_summary,
            solution=solution,
            category=category,
            severity=severity,
            tags=tags,
            ai_generated=False
        )
        
        # 如果需要验证
        if verified and verified_by:
            self.analyzer.knowledge_db.verify_solution(
                signature,
                verified_by=verified_by,
                notes="手动添加并验证"
            )
        
        return {
            'status': 'success',
            'solution_id': solution_id,
            'signature': signature,
            'message': '解决方案已添加到知识库'
        }
    
    def search_solutions(self, query: str = None, category: str = None, 
                        severity: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索解决方案
        
        Args:
            query: 搜索关键词
            category: 分类过滤
            severity: 严重级别过滤
            limit: 返回结果数量限制
            
        Returns:
            解决方案列表
        """
        return self.analyzer.knowledge_db.search_solutions(
            query=query,
            category=category,
            severity=severity,
            limit=limit
        )
    
    def analyze_error(self, error_text: str, source: str = None, 
                     auto_confirm: bool = False) -> Dict[str, Any]:
        """
        分析错误并生成解决方案
        
        Args:
            error_text: 错误文本
            source: 错误来源
            auto_confirm: 是否自动确认AI生成的解决方案
            
        Returns:
            分析结果
        """
        context = {'source': source} if source else {}
        
        # 临时修改配置（如果需要自动确认）
        if auto_confirm:
            self.analyzer.config['auto_confirm'] = True
        
        result = self.analyzer.analyze_error(error_text, context)
        
        return result
    
    def analyze_log_file(self, log_file: str, max_errors: int = 100, 
                        auto_confirm: bool = False) -> Dict[str, Any]:
        """
        分析日志文件
        
        Args:
            log_file: 日志文件路径
            max_errors: 最大分析错误数
            auto_confirm: 是否自动确认AI生成的解决方案
            
        Returns:
            分析结果
        """
        # 临时修改配置（如果需要自动确认）
        if auto_confirm:
            self.analyzer.config['auto_confirm'] = True
        
        results = self.analyzer.batch_analyze(log_file, max_errors)
        
        # 生成统计
        stats = self.analyzer._generate_stats(results)
        
        return {
            'status': 'completed',
            'log_file': log_file,
            'total_errors': len(results),
            'results': results,
            'statistics': stats
        }
    
    def confirm_solution(self, pending_file: str, reviewer: str = "system", 
                        notes: str = None) -> Dict[str, Any]:
        """
        确认待审核的解决方案
        
        Args:
            pending_file: 待审核文件路径
            reviewer: 审核人
            notes: 审核备注
            
        Returns:
            确认结果
        """
        return self.analyzer.confirm_solution(pending_file, reviewer, notes)
    
    def reject_solution(self, pending_file: str, reviewer: str = "system", 
                       reason: str = None) -> Dict[str, Any]:
        """
        拒绝待审核的解决方案
        
        Args:
            pending_file: 待审核文件路径
            reviewer: 审核人
            reason: 拒绝原因
            
        Returns:
            拒绝结果
        """
        return self.analyzer.reject_solution(pending_file, reviewer, reason)
    
    def list_pending(self) -> List[Dict[str, Any]]:
        """列出所有待确认的解决方案"""
        return self.analyzer.list_pending_solutions()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.analyzer.get_statistics()
    
    def export_knowledge(self, output_file: str = None) -> str:
        """
        导出知识库
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            导出文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.analyzer.work_dir / f"knowledge_export_{timestamp}.json"
        
        return self.analyzer.knowledge_db.export_to_json(output_file)
    
    def import_knowledge(self, input_file: str, merge: bool = True) -> int:
        """
        导入知识库
        
        Args:
            input_file: 输入文件路径
            merge: 是否合并现有数据
            
        Returns:
            导入的记录数
        """
        return self.analyzer.knowledge_db.import_from_json(input_file, merge)
    
    def rebuild_index(self) -> Dict[str, Any]:
        """重建知识库索引"""
        # 这里可以添加索引重建逻辑
        return {
            'status': 'success',
            'message': '索引重建功能待实现'
        }


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description='智能知识库管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 添加解决方案
  python intelligent_knowledge.py add --signature "ERR001" --summary "连接超时" --solution "检查网络配置"
  
  # 搜索解决方案
  python intelligent_knowledge.py search --query "超时"
  
  # 分析错误
  python intelligent_knowledge.py analyze --error "java.net.ConnectException: Connection refused"
  
  # 分析日志文件
  python intelligent_knowledge.py analyze-file --file error.log
  
  # 确认解决方案
  python intelligent_knowledge.py confirm --file pending_xxxx.json --reviewer "admin"
  
  # 查看统计
  python intelligent_knowledge.py stats
  
  # 列出待确认
  python intelligent_knowledge.py list-pending
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加解决方案')
    add_parser.add_argument('--signature', required=True, help='错误签名')
    add_parser.add_argument('--summary', required=True, help='错误摘要')
    add_parser.add_argument('--solution', required=True, help='解决方案')
    add_parser.add_argument('--category', help='分类')
    add_parser.add_argument('--severity', help='严重级别')
    add_parser.add_argument('--tags', help='标签（逗号分隔）')
    add_parser.add_argument('--verified', action='store_true', help='标记为已验证')
    add_parser.add_argument('--verified-by', help='验证人')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索解决方案')
    search_parser.add_argument('--query', help='搜索关键词')
    search_parser.add_argument('--category', help='分类')
    search_parser.add_argument('--severity', help='严重级别')
    search_parser.add_argument('--limit', type=int, default=10, help='返回数量限制')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析错误')
    analyze_parser.add_argument('--error', required=True, help='错误文本')
    analyze_parser.add_argument('--source', help='错误来源')
    analyze_parser.add_argument('--auto-confirm', action='store_true', help='自动确认AI解决方案')
    
    # analyze-file 命令
    analyze_file_parser = subparsers.add_parser('analyze-file', help='分析日志文件')
    analyze_file_parser.add_argument('--file', required=True, help='日志文件路径')
    analyze_file_parser.add_argument('--max-errors', type=int, default=100, help='最大分析错误数')
    analyze_file_parser.add_argument('--auto-confirm', action='store_true', help='自动确认AI解决方案')
    
    # confirm 命令
    confirm_parser = subparsers.add_parser('confirm', help='确认解决方案')
    confirm_parser.add_argument('--file', required=True, help='待审核文件路径')
    confirm_parser.add_argument('--reviewer', default='system', help='审核人')
    confirm_parser.add_argument('--notes', help='审核备注')
    
    # reject 命令
    reject_parser = subparsers.add_parser('reject', help='拒绝解决方案')
    reject_parser.add_argument('--file', required=True, help='待审核文件路径')
    reject_parser.add_argument('--reviewer', default='system', help='审核人')
    reject_parser.add_argument('--reason', help='拒绝原因')
    
    # list-pending 命令
    list_parser = subparsers.add_parser('list-pending', help='列出待确认的解决方案')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出知识库')
    export_parser.add_argument('--output', help='输出文件路径')
    
    # import 命令
    import_parser = subparsers.add_parser('import', help='导入知识库')
    import_parser.add_argument('--file', required=True, help='导入文件路径')
    import_parser.add_argument('--merge', action='store_true', help='合并到现有数据')
    
    # rebuild 命令
    rebuild_parser = subparsers.add_parser('rebuild', help='重建索引')
    
    # 通用参数
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    # 初始化管理器
    manager = IntelligentKnowledgeManager(args.config)
    
    # 执行命令
    if args.command == 'add':
        tags = args.tags.split(',') if args.tags else None
        result = manager.add_solution(
            signature=args.signature,
            error_summary=args.summary,
            solution=args.solution,
            category=args.category,
            severity=args.severity,
            tags=tags,
            verified=args.verified,
            verified_by=args.verified_by
        )
        
    elif args.command == 'search':
        results = manager.search_solutions(
            query=args.query,
            category=args.category,
            severity=args.severity,
            limit=args.limit
        )
        result = {'solutions': results, 'count': len(results)}
        
    elif args.command == 'analyze':
        result = manager.analyze_error(
            error_text=args.error,
            source=args.source,
            auto_confirm=args.auto_confirm
        )
        
    elif args.command == 'analyze-file':
        result = manager.analyze_log_file(
            log_file=args.file,
            max_errors=args.max_errors,
            auto_confirm=args.auto_confirm
        )
        
    elif args.command == 'confirm':
        result = manager.confirm_solution(
            pending_file=args.file,
            reviewer=args.reviewer,
            notes=args.notes
        )
        
    elif args.command == 'reject':
        result = manager.reject_solution(
            pending_file=args.file,
            reviewer=args.reviewer,
            reason=args.reason
        )
        
    elif args.command == 'list-pending':
        pending = manager.list_pending()
        result = {'pending_solutions': pending, 'count': len(pending)}
        
    elif args.command == 'stats':
        result = manager.get_statistics()
        
    elif args.command == 'export':
        output_file = manager.export_knowledge(args.output)
        result = {'status': 'success', 'output_file': output_file}
        
    elif args.command == 'import':
        count = manager.import_knowledge(args.file, args.merge)
        result = {'status': 'success', 'imported_count': count}
        
    elif args.command == 'rebuild':
        result = manager.rebuild_index()
        
    else:
        # 没有命令，显示帮助
        parser.print_help()
        return
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 美化输出
        if args.verbose:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            self._print_result(result, args.command)
    
    return result
    
    def _print_result(self, result: Dict[str, Any], command: str):
        """美化输出结果"""
        if command == 'add':
            print(f"✅ 解决方案已添加")
            print(f"   ID: {result.get('solution_id')}")
            print(f"   签名: {result.get('signature')}")
            
        elif command == 'search':
            solutions = result.get('solutions', [])
            count = result.get('count', 0)
            print(f"🔍 找到 {count} 个解决方案:")
            for i, sol in enumerate(solutions, 1):
                print(f"{i}. {sol.get('signature')} - {sol.get('error_summary')}")
                print(f"   分类: {sol.get('category')}, 严重级别: {sol.get('severity')}")
                print(f"   命中次数: {sol.get('hit_count')}, 成功率: {sol.get('success_count', 0)}/{sol.get('hit_count', 1)}")
                print()
                
        elif command == 'analyze':
            status = result.get('status')
            if status == 'found':
                print(f"✅ 在知识库中找到解决方案")
                solution = result.get('solution', {})
                print(f"   签名: {solution.get('signature')}")
                print(f"   摘要: {solution.get('error_summary')}")
                print(f"   命中次数: {solution.get('hit_count')}")
                
            elif status == 'ai_generated_auto_confirmed':
                print(f"🤖 AI生成解决方案（已自动确认）")
                solution = result.get('solution', {})
                print(f"   签名: {solution.get('signature')}")
                print(f"   摘要: {solution.get('error_summary')}")
                print(f"   置信度: {solution.get('confidence', 0):.2f}")
                
            elif status == 'ai_generated_pending':
                print(f"⏳ AI生成解决方案（需要人工确认）")
                print(f"   签名: {result.get('signature')}")
                print(f"   文件: {result.get('pending_file')}")
                print(f"   请审核文件并运行确认命令")
                
            elif status == 'ai_low_confidence':
                print(f"⚠️  AI生成解决方案（置信度不足）")
                print(f"   签名: {result.get('signature')}")
                print(f"   置信度: {result.get('confidence', 0):.2f}")
                print(f"   需要人工处理")
                
            elif status == 'ai_failed':
                print(f"❌ AI生成失败")
                print(f"   错误: {result.get('error')}")
                print(f"   需要人工处理")
                
        elif command == 'analyze-file':
            stats = result.get('statistics', {})
            print(f"📊 日志分析完成")
            print(f"   文件: {result.get('log_file')}")
            print(f"   总错误数: {result.get('total_errors', 0)}")
            print(f"   知识库命中: {stats.get('found', 0)}")
            print(f"   AI生成: {stats.get('ai_generated', 0)}")
            print(f"   需要人工确认: {stats.get('pending', 0)}")
            
        elif command == 'confirm':
            print(f"✅ 解决方案已确认")
            print(f"   ID: {result.get('solution_id')}")
            print(f"   文件: {result.get('verified_file')}")
            
        elif command == 'reject':
            print(f"❌ 解决方案已被拒绝")
            print(f"   文件: {result.get('rejected_file')}")
            
        elif command == 'list-pending':
            pending = result.get('pending_solutions', [])
            count = result.get('count', 0)
            if count > 0:
                print(f"⏳ 有 {count} 个待确认的解决方案:")
                for i, sol in enumerate(pending, 1):
                    print(f"{i}. {sol.get('file')}")
                    print(f"   签名: {sol.get('signature')}")
                    print(f"   摘要: {sol.get('error_summary')}")
                    print(f"   置信度: {sol.get('confidence', 0):.2f}")
                    print()
            else:
                print("✅ 没有待确认的解决方案")
                
        elif command == 'stats':
            kb_stats = result.get('knowledge_base', {})
            print(f"📈 知识库统计:")
            print(f"   总解决方案数: {kb_stats.get('total_solutions', 0)}")
            print(f"   已验证解决方案: {kb_stats.get('verified_solutions', 0)}")
            print(f"   AI生成解决方案: {kb_stats.get('ai_generated_solutions', 0)}")
            print(f"   总命中次数: {kb_stats.get('total_hits', 0)}")
            print(f"   总成功次数: {kb_stats.get('total_successes', 0)}")
            print(f"   成功率: {kb_stats.get('success_rate', 0):.2%}")
            print()
            print(f"📊 待处理统计:")
            print(f"   待确认解决方案: {result.get('pending_solutions', 0)}")
            print(f"   已验证解决方案: {result.get('verified_solutions', 0)}")
            print(f"   被拒绝解决方案: {result.get('rejected_solutions', 0)}")
            print(f"   总分析次数: {result.get('total_analyzed', 0)}")
            
        elif command == 'export':
            print(f"💾 知识库已导出")
            print(f"   文件: {result.get('output_file')}")
            
        elif command == 'import':
            print(f"📥 知识库已导入")
            print(f"   导入记录数: {result.get('imported_count', 0)}")
            
        elif command == 'rebuild':
            print(f"🔧 {result.get('message', '操作完成')}")


if __name__ == '__main__':
    main()