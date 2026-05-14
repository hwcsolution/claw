#!/usr/bin/env python3
"""
生成学生成绩报告
"""

import sys
import json
from pathlib import Path

# 导入飞书工具模块
sys.path.insert(0, str(Path(__file__).parent))
from feishu_utils import get_access_token, read_sheet_range, parse_table_data

def get_student_report(student_name, spreadsheet_token, sheets_config):
    """
    生成学生成绩报告
    
    Args:
        student_name: 学生姓名
        spreadsheet_token: 成绩汇总表 token
        sheets_config: 工作表配置 {"日期": "sheet_id"}
    """
    token = get_access_token()
    if not token:
        return None
    
    # 读取各次考试成绩
    all_exams = []
    for exam_date, sheet_id in sheets_config.items():
        print(f"正在读取 {exam_date} 考试数据...")
        values = read_sheet_range(token, spreadsheet_token, sheet_id, "A1:P50")
        records = parse_table_data(values, key_field="学号")
        
        # 查找该学生
        for r in records:
            if r.get("学生姓名") == student_name or r.get("姓名") == student_name:
                r["考试日期"] = exam_date
                all_exams.append(r)
                print(f"  ✅ 找到 {student_name} 的成绩")
                break
        else:
            print(f"  ⚠️ 未找到 {student_name} 的成绩")
    
    if not all_exams:
        print(f"❌ 未找到 {student_name} 的任何考试成绩")
        return None
    
    # 生成报告
    print("\n" + "="*60)
    print(f"📊 {student_name} 同学考试成绩报告")
    print("="*60)
    
    # 基本信息
    latest = all_exams[0]
    print(f"\n【基本信息】")
    print(f"  姓名：{student_name}")
    print(f"  班级：{latest.get('班级', 'N/A')}")
    print(f"  学号：{latest.get('学号', 'N/A')}")
    
    # 最近考试概览
    print(f"\n【最近考试概览】")
    for i, exam in enumerate(all_exams):
        date = exam.get("考试日期", "N/A")
        rank = exam.get("年级排名", "N/A")
        total = exam.get("总分", "N/A")
        avg = exam.get("平均分", "N/A")
        
        # 计算变化
        change_str = ""
        if i < len(all_exams) - 1:
            prev = all_exams[i + 1]
            prev_rank = int(prev.get("年级排名", 0) or 0)
            curr_rank = int(rank or 0)
            prev_total = int(prev.get("总分", 0) or 0)
            curr_total = int(total or 0)
            
            rank_change = prev_rank - curr_rank  # 正数表示进步
            total_change = curr_total - prev_total
            
            if rank_change > 0:
                change_str = f"  [排名↑{rank_change}名, 总分+{total_change}分]"
            elif rank_change < 0:
                change_str = f"  [排名↓{abs(rank_change)}名, 总分{total_change}分]"
            else:
                change_str = f"  [排名持平, 总分+{total_change}分]"
        
        print(f"  {date}: 年级第{rank}名, 总分{total}分, 平均{avg}分{change_str}")
    
    # 各科成绩对比
    print(f"\n【各科成绩对比】")
    subjects = ["语文", "数学", "英语", "政治", "历史", "地理", "生物"]
    
    print(f"  {'科目':<8}", end="")
    for exam in all_exams:
        print(f" {exam.get('考试日期', 'N/A'):>10}", end="")
    print(f"  {'变化':>8}")
    
    print(f"  {'-'*60}")
    
    for subj in subjects:
        print(f"  {subj:<8}", end="")
        scores = []
        for exam in all_exams:
            score = exam.get(subj, "N/A")
            scores.append(int(score) if score and score != "N/A" else 0)
            print(f" {str(score):>10}", end="")
        
        # 计算变化
        if len(scores) >= 2 and scores[0] and scores[1]:
            change = scores[0] - scores[1]
            if change > 0:
                print(f"  +{change:>7}")
            elif change < 0:
                print(f"  {change:>8}")
            else:
                print(f"  {'持平':>8}")
        else:
            print()
    
    # 优势与薄弱学科
    print(f"\n【学科分析】")
    latest_scores = {}
    for subj in subjects:
        score = latest.get(subj)
        if score and score != "N/A":
            latest_scores[subj] = int(score)
    
    if latest_scores:
        sorted_scores = sorted(latest_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"  优势学科：{', '.join([f'{s[0]}({s[1]}分)' for s in sorted_scores[:3]])}")
        print(f"  薄弱学科：{', '.join([f'{s[0]}({s[1]}分)' for s in sorted_scores[-3:]])}")
    
    # 建议
    print(f"\n【教师评语】")
    latest_rank = int(latest.get("年级排名", 0) or 0)
    if latest_rank == 1:
        print(f"  🌟 {student_name}同学本次考试年级第一，表现优异！")
        print(f"  各科成绩均衡，继续保持，争取更大突破！")
    elif latest_rank <= 5:
        print(f"  👍 {student_name}同学本次考试年级前五，表现优秀！")
        if len(all_exams) > 1:
            prev_rank = int(all_exams[1].get("年级排名", 0) or 0)
            if latest_rank < prev_rank:
                print(f"  排名有所提升，进步明显，继续保持！")
    elif latest_rank <= 10:
        print(f"  📈 {student_name}同学本次考试年级前十，表现良好。")
        print(f"  继续努力，争取进入前五！")
    else:
        print(f"  💪 {student_name}同学要继续努力，争取更大进步！")
    
    # 返回数据
    return {
        "student_name": student_name,
        "exams": all_exams,
        "latest_rank": latest_rank,
        "latest_total": int(latest.get("总分", 0) or 0)
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python student_report.py <学生姓名>")
        print("示例: python student_report.py xxx")
        sys.exit(1)
    
    student_name = sys.argv[1]
    
    # 成绩汇总表配置
    spreadsheet_token = "SXlnsuW9rhhbQPtjHQKciZZXnUf"
    sheets_config = {
        "2025-11-12": "CNHOVc",
        "2025-10-25": "iintOO",
        "2025-10-12": "9dd137"
    }
    
    report = get_student_report(student_name, spreadsheet_token, sheets_config)
    
    if report:
        # 保存报告
        output_dir = Path(__file__).parent.parent.parent / "data" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{student_name}_成绩报告.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 报告已保存到: {output_file}")

if __name__ == "__main__":
    main()
