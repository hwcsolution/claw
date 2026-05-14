#!/usr/bin/env python3
"""
智能知识库数据库管理
使用SQLite存储知识库，支持签名匹配、命中统计等功能
"""

import os
import sys
import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

class KnowledgeDatabase:
    """知识库数据库管理类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化知识库数据库
        
        Args:
            db_path: SQLite数据库文件路径
        """
        if db_path is None:
            # 默认路径：技能目录下的knowledge.db
            script_dir = Path(__file__).parent
            self.db_path = script_dir.parent / "knowledge.db"
        else:
            self.db_path = Path(db_path)
        
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建知识库表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signature TEXT UNIQUE NOT NULL,
            error_summary TEXT NOT NULL,
            solution TEXT NOT NULL,
            hit_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            severity TEXT,
            tags TEXT,
            verified BOOLEAN DEFAULT 0,
            ai_generated BOOLEAN DEFAULT 0,
            verified_by TEXT,
            verified_at TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signature ON knowledge_base(signature)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON knowledge_base(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON knowledge_base(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hit_count ON knowledge_base(hit_count DESC)')
        
        # 创建使用记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signature TEXT NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN,
            feedback TEXT,
            user TEXT,
            log_source TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_solution(self, signature: str, error_summary: str, solution: str, 
                    category: str = None, severity: str = None, 
                    tags: List[str] = None, ai_generated: bool = False) -> int:
        """
        添加解决方案到知识库
        
        Args:
            signature: 错误签名
            error_summary: 错误摘要
            solution: 解决方案
            category: 分类
            severity: 严重级别
            tags: 标签列表
            ai_generated: 是否AI生成
            
        Returns:
            插入的ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else '[]'
        
        try:
            cursor.execute('''
            INSERT INTO knowledge_base 
            (signature, error_summary, solution, category, severity, tags, ai_generated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (signature, error_summary, solution, category, severity, tags_json, ai_generated))
            
            solution_id = cursor.lastrowid
            conn.commit()
            return solution_id
            
        except sqlite3.IntegrityError:
            # 签名已存在，更新现有记录
            cursor.execute('''
            UPDATE knowledge_base 
            SET error_summary = ?, solution = ?, category = ?, severity = ?, tags = ?, 
                ai_generated = ?, updated_at = CURRENT_TIMESTAMP
            WHERE signature = ?
            ''', (error_summary, solution, category, severity, tags_json, ai_generated, signature))
            
            cursor.execute('SELECT id FROM knowledge_base WHERE signature = ?', (signature,))
            solution_id = cursor.fetchone()[0]
            conn.commit()
            return solution_id
            
        finally:
            conn.close()
    
    def find_solution(self, signature: str) -> Optional[Dict[str, Any]]:
        """
        根据签名查找解决方案
        
        Args:
            signature: 错误签名
            
        Returns:
            解决方案字典，如果未找到返回None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM knowledge_base 
        WHERE signature = ? AND verified = 1
        ''', (signature,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 增加命中次数
            self.increment_hit_count(signature)
            
            # 记录使用日志
            self.log_usage(signature, matched=True)
            
            # 转换为字典
            result = dict(row)
            result['tags'] = json.loads(result['tags']) if result['tags'] else []
            return result
        
        return None
    
    def search_solutions(self, query: str, category: str = None, 
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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = ["verified = 1"]
        params = []
        
        if query:
            conditions.append("(signature LIKE ? OR error_summary LIKE ? OR solution LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f'''
        SELECT * FROM knowledge_base 
        WHERE {where_clause}
        ORDER BY hit_count DESC, updated_at DESC
        LIMIT ?
        ''', params + [limit])
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['tags'] = json.loads(result['tags']) if result['tags'] else []
            results.append(result)
        
        return results
    
    def increment_hit_count(self, signature: str, success: bool = None):
        """
        增加命中次数
        
        Args:
            signature: 错误签名
            success: 是否成功解决（可选）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE knowledge_base 
        SET hit_count = hit_count + 1,
            success_count = success_count + ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE signature = ?
        ''', (1 if success else 0, signature))
        
        conn.commit()
        conn.close()
    
    def log_usage(self, signature: str, matched: bool = True, 
                 success: bool = None, feedback: str = None, 
                 user: str = None, log_source: str = None):
        """
        记录使用日志
        
        Args:
            signature: 错误签名
            matched: 是否匹配成功
            success: 是否成功解决
            feedback: 用户反馈
            user: 用户标识
            log_source: 日志来源
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO usage_log (signature, matched_at, success, feedback, user, log_source)
        VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
        ''', (signature, success, feedback, user, log_source))
        
        conn.commit()
        conn.close()
    
    def verify_solution(self, signature: str, verified_by: str, notes: str = None):
        """
        验证解决方案
        
        Args:
            signature: 错误签名
            verified_by: 验证人
            notes: 验证备注
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE knowledge_base 
        SET verified = 1, verified_by = ?, verified_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE signature = ?
        ''', (verified_by, signature))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 总记录数
        cursor.execute('SELECT COUNT(*) FROM knowledge_base')
        stats['total_solutions'] = cursor.fetchone()[0]
        
        # 已验证记录数
        cursor.execute('SELECT COUNT(*) FROM knowledge_base WHERE verified = 1')
        stats['verified_solutions'] = cursor.fetchone()[0]
        
        # AI生成记录数
        cursor.execute('SELECT COUNT(*) FROM knowledge_base WHERE ai_generated = 1')
        stats['ai_generated_solutions'] = cursor.fetchone()[0]
        
        # 总命中次数
        cursor.execute('SELECT SUM(hit_count) FROM knowledge_base')
        stats['total_hits'] = cursor.fetchone()[0] or 0
        
        # 总成功次数
        cursor.execute('SELECT SUM(success_count) FROM knowledge_base')
        stats['total_successes'] = cursor.fetchone()[0] or 0
        
        # 成功率
        if stats['total_hits'] > 0:
            stats['success_rate'] = stats['total_successes'] / stats['total_hits']
        else:
            stats['success_rate'] = 0.0
        
        # 按分类统计
        cursor.execute('''
        SELECT category, COUNT(*) as count, SUM(hit_count) as hits
        FROM knowledge_base 
        WHERE verified = 1
        GROUP BY category
        ORDER BY count DESC
        ''')
        
        stats['by_category'] = []
        for row in cursor.fetchall():
            stats['by_category'].append({
                'category': row[0] or '未分类',
                'count': row[1],
                'hits': row[2] or 0
            })
        
        # 最常用解决方案
        cursor.execute('''
        SELECT signature, error_summary, hit_count, success_count
        FROM knowledge_base 
        WHERE verified = 1
        ORDER BY hit_count DESC
        LIMIT 10
        ''')
        
        stats['top_solutions'] = []
        for row in cursor.fetchall():
            stats['top_solutions'].append({
                'signature': row[0],
                'error_summary': row[1],
                'hit_count': row[2],
                'success_count': row[3] or 0
            })
        
        conn.close()
        return stats
    
    def export_to_json(self, output_path: str = None):
        """
        导出知识库为JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.db_path.parent / "knowledge_export.json"
        
        # 获取所有已验证的解决方案
        solutions = self.search_solutions("", limit=1000)
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_solutions': len(solutions),
            'solutions': solutions
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def import_from_json(self, json_path: str, merge: bool = True):
        """
        从JSON文件导入知识库
        
        Args:
            json_path: JSON文件路径
            merge: 是否合并现有数据（True=合并，False=清空后导入）
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not merge:
            # 清空现有数据
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM knowledge_base')
            conn.commit()
            conn.close()
        
        imported_count = 0
        for solution in data.get('solutions', []):
            try:
                self.add_solution(
                    signature=solution.get('signature', ''),
                    error_summary=solution.get('error_summary', ''),
                    solution=solution.get('solution', ''),
                    category=solution.get('category'),
                    severity=solution.get('severity'),
                    tags=solution.get('tags', []),
                    ai_generated=solution.get('ai_generated', False)
                )
                imported_count += 1
            except Exception as e:
                print(f"导入失败: {solution.get('signature', '未知')} - {e}")
        
        return imported_count


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='知识库数据库管理工具')
    parser.add_argument('--db', help='数据库文件路径', default='knowledge.db')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--export', help='导出为JSON文件')
    parser.add_argument('--import', dest='import_file', help='从JSON文件导入')
    parser.add_argument('--search', help='搜索解决方案')
    parser.add_argument('--category', help='按分类过滤')
    parser.add_argument('--severity', help='按严重级别过滤')
    parser.add_argument('--add', action='store_true', help='添加解决方案')
    parser.add_argument('--signature', help='错误签名')
    parser.add_argument('--summary', help='错误摘要')
    parser.add_argument('--solution', help='解决方案')
    parser.add_argument('--tags', help='标签（逗号分隔）')
    parser.add_argument('--verified', action='store_true', help='标记为已验证')
    parser.add_argument('--verified-by', help='验证人')
    
    args = parser.parse_args()
    
    db = KnowledgeDatabase(args.db)
    
    if args.init:
        print("数据库已初始化")
    
    if args.add:
        if not args.signature or not args.summary or not args.solution:
            print("错误: --add 需要 --signature, --summary 和 --solution 参数")
            return 1
        
        tags = args.tags.split(',') if args.tags else None
        
        solution_id = db.add_solution(
            signature=args.signature,
            error_summary=args.summary,
            solution=args.solution,
            category=args.category,
            severity=args.severity,
            tags=tags,
            ai_generated=False
        )
        
        if args.verified and args.verified_by:
            db.verify_solution(
                args.signature,
                verified_by=args.verified_by,
                notes="命令行添加"
            )
        
        print(f"解决方案已添加，ID: {solution_id}")
    
    if args.stats:
        stats = db.get_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    if args.export:
        output_path = db.export_to_json(args.export)
        print(f"已导出到: {output_path}")
    
    if args.import_file:
        count = db.import_from_json(args.import_file)
        print(f"已导入 {count} 条记录")
    
    if args.search:
        results = db.search_solutions(args.search, args.category, args.severity)
        for result in results:
            print(f"签名: {result['signature']}")
            print(f"摘要: {result['error_summary']}")
            print(f"命中: {result['hit_count']} 次")
            print(f"分类: {result['category']}")
            print(f"严重级别: {result['severity']}")
            print("-" * 50)


if __name__ == '__main__':
    main()