#!/usr/bin/env python3
"""
智能日志分析器
整合错误签名提取、知识库匹配、AI解决方案生成和人工确认流程
"""

import os
import sys
import json
import argparse
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from knowledge_db import KnowledgeDatabase
from error_signature import ErrorSignatureExtractor, ErrorSignature
from ai_solution_generator import AISolutionGenerator, AISolution


class IntelligentAnalyzer:
    """智能日志分析器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        
        # 初始化组件
        self.knowledge_db = KnowledgeDatabase(self.config.get('db_path', 'knowledge.db'))
        self.signature_extractor = ErrorSignatureExtractor()
        self.ai_generator = AISolutionGenerator(self.config.get('ai_config'))
        
        # 工作目录
        self.work_dir = Path(self.config.get('work_dir', './work'))
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 待确认解决方案目录
        self.pending_dir = self.work_dir / 'pending_solutions'
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        
        # 已验证解决方案目录
        self.verified_dir = self.work_dir / 'verified_solutions'
        self.verified_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            'db_path': 'knowledge.db',
            'work_dir': './work',
            'ai_config': 'config/ai-config.yaml',
            'auto_confirm': False,  # 是否自动确认AI生成的解决方案
            'min_confidence': 0.7,  # 最小置信度阈值
            'max_ai_retries': 3,    # AI生成最大重试次数
            'log_level': 'INFO',
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    import yaml
                    user_config = yaml.safe_load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"加载配置文件失败: {config_path} - {e}")
        
        return default_config
    
    def analyze_error(self, error_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析错误并生成解决方案
        
        Args:
            error_text: 错误文本
            context: 上下文信息
            
        Returns:
            分析结果
        """
        if context is None:
            context = {}
        
        print(f"开始分析错误...")
        
        # 1. 提取错误签名
        print(f"步骤1: 提取错误签名")
        error_signature = self.signature_extractor.extract_signature(error_text, context)
        print(f"  错误签名: {error_signature.signature}")
        print(f"  错误类型: {error_signature.error_type}")
        print(f"  错误代码: {error_signature.error_code}")
        
        # 2. 在知识库中查找
        print(f"步骤2: 在知识库中查找")
        existing_solution = self.knowledge_db.find_solution(error_signature.signature)
        
        if existing_solution:
            print(f"  找到现有解决方案（命中次数: {existing_solution['hit_count']}）")
            
            # 更新命中次数
            self.knowledge_db.increment_hit_count(error_signature.signature)
            
            return {
                'status': 'found',
                'signature': error_signature.signature,
                'solution': existing_solution,
                'source': 'knowledge_base',
                'confidence': 1.0,
                'message': '在知识库中找到现有解决方案'
            }
        
        print(f"  知识库中未找到匹配的解决方案")
        
        # 3. 调用AI生成解决方案
        print(f"步骤3: 调用AI生成解决方案")
        ai_context = {
            'error_text': error_text,
            'error_type': error_signature.error_type,
            'error_code': error_signature.error_code,
            'log_source': context.get('source', 'unknown'),
            'system_info': context.get('system_info', {})
        }
        
        try:
            ai_solution = self.ai_generator.generate_solution(
                error_signature.signature, 
                ai_context
            )
            
            print(f"  AI生成完成（置信度: {ai_solution.confidence:.2f}）")
            
            # 4. 检查置信度
            if ai_solution.confidence >= self.config['min_confidence']:
                if self.config['auto_confirm']:
                    # 自动确认并保存到知识库
                    print(f"步骤4: 自动确认AI解决方案（置信度达标）")
                    
                    # 保存到知识库
                    solution_id = self.knowledge_db.add_solution(
                        signature=error_signature.signature,
                        error_summary=ai_solution.error_summary,
                        solution=ai_solution.solution,
                        category=ai_solution.category,
                        severity=ai_solution.severity,
                        tags=ai_solution.tags,
                        ai_generated=True
                    )
                    
                    # 标记为已验证
                    self.knowledge_db.verify_solution(
                        error_signature.signature,
                        verified_by='auto_confirm',
                        notes=f'AI生成，置信度{ai_solution.confidence:.2f}'
                    )
                    
                    return {
                        'status': 'ai_generated_auto_confirmed',
                        'signature': error_signature.signature,
                        'solution': ai_solution.to_dict(),
                        'solution_id': solution_id,
                        'source': 'ai_auto_confirmed',
                        'confidence': ai_solution.confidence,
                        'message': 'AI生成解决方案已自动确认并保存到知识库'
                    }
                else:
                    # 需要人工确认
                    print(f"步骤4: AI解决方案需要人工确认")
                    
                    # 保存到待确认目录
                    pending_file = self._save_pending_solution(ai_solution, error_signature)
                    
                    return {
                        'status': 'ai_generated_pending',
                        'signature': error_signature.signature,
                        'solution': ai_solution.to_dict(),
                        'pending_file': str(pending_file),
                        'source': 'ai_pending_review',
                        'confidence': ai_solution.confidence,
                        'message': 'AI生成解决方案需要人工确认',
                        'review_instructions': self._get_review_instructions(pending_file)
                    }
            else:
                # 置信度不足，需要人工处理
                print(f"步骤4: AI解决方案置信度不足（{ai_solution.confidence:.2f} < {self.config['min_confidence']}）")
                
                # 保存到待确认目录
                pending_file = self._save_pending_solution(ai_solution, error_signature)
                
                return {
                    'status': 'ai_low_confidence',
                    'signature': error_signature.signature,
                    'solution': ai_solution.to_dict(),
                    'pending_file': str(pending_file),
                    'source': 'ai_low_confidence',
                    'confidence': ai_solution.confidence,
                    'message': 'AI生成解决方案置信度不足，需要人工处理',
                    'review_instructions': self._get_review_instructions(pending_file)
                }
                
        except Exception as e:
            print(f"  AI生成失败: {e}")
            
            # AI生成失败，返回错误
            return {
                'status': 'ai_failed',
                'signature': error_signature.signature,
                'error': str(e),
                'source': 'ai_failed',
                'confidence': 0.0,
                'message': 'AI生成解决方案失败，需要人工处理',
                'manual_instructions': self._get_manual_instructions(error_signature, error_text)
            }
    
    def _save_pending_solution(self, ai_solution: AISolution, 
                              error_signature: ErrorSignature) -> Path:
        """保存待确认的解决方案"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pending_{error_signature.signature}_{timestamp}.json"
        filepath = self.pending_dir / filename
        
        data = {
            'ai_solution': ai_solution.to_dict(),
            'error_signature': error_signature.to_dict(),
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'reviewed': False,
            'reviewed_by': None,
            'reviewed_at': None,
            'decision': None,
            'notes': None
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _get_review_instructions(self, pending_file: Path) -> str:
        """获取审核指令"""
        return f"""
请审核AI生成的解决方案:

1. 查看文件: {pending_file}
2. 检查解决方案的准确性和完整性
3. 如果需要修改，编辑解决方案
4. 确认后运行: python scripts/intelligent_analyzer.py --confirm {pending_file}
5. 拒绝则运行: python scripts/intelligent_analyzer.py --reject {pending_file}

审核完成后，解决方案将保存到知识库中。
"""
    
    def _get_manual_instructions(self, error_signature: ErrorSignature, 
                                error_text: str) -> str:
        """获取人工处理指令"""
        return f"""
AI无法生成解决方案，请人工处理:

错误签名: {error_signature.signature}
错误类型: {error_signature.error_type}
错误代码: {error_signature.error_code}

错误详情:
{error_text[:500]}...

请按以下步骤处理:
1. 分析错误原因
2. 制定解决方案
3. 手动添加到知识库:
   python scripts/knowledge_db.py --add --signature "{error_signature.signature}" --summary "错误摘要" --solution "解决方案"
"""
    
    def confirm_solution(self, pending_file: str, reviewer: str = None, 
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
        pending_path = Path(pending_file)
        if not pending_path.exists():
            return {'status': 'error', 'message': f'文件不存在: {pending_file}'}
        
        try:
            with open(pending_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ai_solution_dict = data['ai_solution']
            error_signature_dict = data['error_signature']
            
            # 创建对象
            ai_solution = AISolution(**ai_solution_dict)
            
            # 保存到知识库
            solution_id = self.knowledge_db.add_solution(
                signature=ai_solution.signature,
                error_summary=ai_solution.error_summary,
                solution=ai_solution.solution,
                category=ai_solution.category,
                severity=ai_solution.severity,
                tags=ai_solution.tags,
                ai_generated=True
            )
            
            # 标记为已验证
            self.knowledge_db.verify_solution(
                ai_solution.signature,
                verified_by=reviewer or 'unknown',
                notes=notes or '人工审核通过'
            )
            
            # 移动文件到已验证目录
            verified_file = self.verified_dir / pending_path.name
            pending_path.rename(verified_file)
            
            # 更新文件状态
            data['status'] = 'confirmed'
            data['reviewed'] = True
            data['reviewed_by'] = reviewer
            data['reviewed_at'] = datetime.now().isoformat()
            data['decision'] = 'confirmed'
            data['notes'] = notes
            
            with open(verified_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                'status': 'confirmed',
                'solution_id': solution_id,
                'signature': ai_solution.signature,
                'verified_file': str(verified_file),
                'message': '解决方案已确认并保存到知识库'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'确认失败: {e}'}
    
    def reject_solution(self, pending_file: str, reviewer: str = None, 
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
        pending_path = Path(pending_file)
        if not pending_path.exists():
            return {'status': 'error', 'message': f'文件不存在: {pending_file}'}
        
        try:
            with open(pending_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新文件状态
            data['status'] = 'rejected'
            data['reviewed'] = True
            data['reviewed_by'] = reviewer
            data['reviewed_at'] = datetime.now().isoformat()
            data['decision'] = 'rejected'
            data['reject_reason'] = reason
            
            # 移动到拒绝目录
            rejected_dir = self.work_dir / 'rejected_solutions'
            rejected_dir.mkdir(parents=True, exist_ok=True)
            rejected_file = rejected_dir / pending_path.name
            pending_path.rename(rejected_file)
            
            with open(rejected_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                'status': 'rejected',
                'rejected_file': str(rejected_file),
                'message': '解决方案已被拒绝'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'拒绝失败: {e}'}
    
    def batch_analyze(self, log_file: str, max_errors: int = 100) -> List[Dict[str, Any]]:
        """
        批量分析日志文件
        
        Args:
            log_file: 日志文件路径
            max_errors: 最大分析错误数
            
        Returns:
            分析结果列表
        """
        print(f"开始批量分析日志文件: {log_file}")
        
        # 提取错误签名
        error_signatures = self.signature_extractor.extract_from_log_file(log_file, max_errors)
        
        print(f"提取到 {len(error_signatures)} 个错误")
        
        results = []
        for i, error_sig in enumerate(error_signatures, 1):
            print(f"\n分析错误 {i}/{len(error_signatures)}: {error_sig.signature}")
            
            result = self.analyze_error(
                error_sig.original_error,
                {
                    'source': log_file,
                    'error_type': error_sig.error_type,
                    'error_code': error_sig.error_code
                }
            )
            
            results.append(result)
        
        # 生成统计报告
        stats = self._generate_stats(results)
        
        print(f"\n分析完成!")
        print(f"总计: {stats['total']} 个错误")
        print(f"知识库命中: {stats['found']} 个")
        print(f"AI生成: {stats['ai_generated']} 个")
        print(f"需要人工确认: {stats['pending']} 个")
        print(f"AI失败: {stats['ai_failed']} 个")
        
        return results
    
    def _generate_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成统计信息"""
        stats = {
            'total': len(results),
            'found': 0,
            'ai_generated_auto_confirmed': 0,
            'ai_generated_pending': 0,
            'ai_low_confidence': 0,
            'ai_failed': 0
        }
        
        for result in results:
            status = result.get('status', 'unknown')
            if status in stats:
                stats[status] += 1
            elif status == 'found':
                stats['found'] += 1
        
        # 计算需要人工确认的数量
        stats['pending'] = (stats['ai_generated_pending'] + 
                          stats['ai_low_confidence'] + 
                          stats['ai_failed'])
        
        # 计算AI生成的数量
        stats['ai_generated'] = (stats['ai_generated_auto_confirmed'] + 
                               stats['ai_generated_pending'] + 
                               stats['ai_low_confidence'])
        
        return stats
    
    def list_pending_solutions(self) -> List[Dict[str, Any]]:
        """列出所有待确认的解决方案"""
        pending_files = list(self.pending_dir.glob('pending_*.json'))
        
        solutions = []
        for filepath in pending_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                solutions.append({
                    'file': str(filepath),
                    'signature': data['ai_solution']['signature'],
                    'error_summary': data['ai_solution']['error_summary'],
                    'confidence': data['ai_solution']['confidence'],
                    'created_at': data['created_at'],
                    'status': data['status']
                })
            except Exception as e:
                print(f"读取待确认文件失败: {filepath} - {e}")
        
        return solutions
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        # 知识库统计
        kb_stats = self.knowledge_db.get_statistics()
        
        # 待确认统计
        pending_solutions = self.list_pending_solutions()
        
        # 文件统计
        pending_count = len(pending_solutions)
        verified_count = len(list(self.verified_dir.glob('*.json')))
        rejected_count = len(list((self.work_dir / 'rejected_solutions').glob('*.json')))
        
        return {
            'knowledge_base': kb_stats,
            'pending_solutions': pending_count,
            'verified_solutions': verified_count,
            'rejected_solutions': rejected_count,
            'total_analyzed': kb_stats['total_hits'] + pending_count + rejected_count,
            'success_rate': kb_stats.get('success_rate', 0.0)
        }


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='智能日志分析器')
    parser.add_argument('--config', help='配置文件路径', default='config/intelligent-analyzer.yaml')
    parser.add_argument('--analyze', help='分析错误文本')
    parser.add_argument('--file', help='分析日志文件')
    parser.add_argument('--max-errors', type=int, default=100, help='最大分析错误数（默认: 100）')
    parser.add_argument('--confirm', help='确认待审核的解决方案')
    parser.add_argument('--reject', help='拒绝待审核的解决方案')
    parser.add_argument('--reviewer', help='审核人名称')
    parser.add_argument('--notes', help='审核备注')
    parser.add_argument('--reason', help='拒绝原因')
    parser.add_argument('--list-pending', action='store_true', help='列出待确认的解决方案')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--auto-confirm', action='store_true', help='自动确认AI解决方案')
    
    args = parser.parse_args()
    
    # 更新配置
    config = {}
    if args.auto_confirm:
        config['auto_confirm'] = True
    
    analyzer = IntelligentAnalyzer(args.config)
    
    if args.analyze:
        # 分析单个错误
        result = analyzer.analyze_error(args.analyze)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.file:
        # 批量分析日志文件
        results = analyzer.batch_analyze(args.file, args.max_errors)
        
        # 保存结果
        output_file = Path(args.file).with_suffix('.analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析结果已保存到: {output_file}")
    
    elif args.confirm:
        # 确认解决方案
        result = analyzer.confirm_solution(args.confirm, args.reviewer, args.notes)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.reject:
        # 拒绝解决方案
        result = analyzer.reject_solution(args.reject, args.reviewer, args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.list_pending:
        # 列出待确认的解决方案
        pending = analyzer.list_pending_solutions()
        if pending:
            print(f"待确认的解决方案 ({len(pending)} 个):")
            for i, sol in enumerate(pending, 1):
                print(f"{i}. {sol['file']}")
                print(f"   签名: {sol['signature']}")
                print(f"   摘要: {sol['error_summary']}")
                print(f"   置信度: {sol['confidence']:.2f}")
                print(f"   创建时间: {sol['created_at']}")
                print()
        else:
            print("没有待确认的解决方案")
    
    elif args.stats:
        # 显示统计信息
        stats = analyzer.get_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        # 显示帮助
        print("智能日志分析器 - 使用示例:")
        print("  分析单个错误: python intelligent_analyzer.py --analyze \"错误文本\"")
        print("  分析日志文件: python intelligent_analyzer.py --file error.log")
        print("  确认解决方案: python intelligent_analyzer.py --confirm pending_xxxx.json --reviewer \"审核人\"")
        print("  拒绝解决方案: python intelligent_analyzer.py --reject pending_xxxx.json --reason \"原因\"")
        print("  列出待确认: python intelligent_analyzer.py --list-pending")
        print("  显示统计: python intelligent_analyzer.py --stats")
        print("  自动确认: python intelligent_analyzer.py --analyze \"错误文本\" --auto-confirm")


if __name__ == '__main__':
    main()