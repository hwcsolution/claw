#!/usr/bin/env python3
"""
考试成绩对比分析脚本
支持命令行调用和模块导入
"""

import json
import sys
from pathlib import Path

# 导入飞书工具模块
sys.path.insert(0, str(Path(__file__).parent))
from feishu_utils import get_access_token, read_sheet_range, parse_table_data

def analyze_exams(spreadsheet_token, sheet1_id, sheet2_id, exam1_name, exam2_name, output_dir=None):
    """
    对比分析两次考试成绩
    
    Args:
        spreadsheet_token: 电子表格 token
        sheet1_id: 第一次考试的工作表 ID
        sheet2_id: 第二次考试的工作表 ID
        exam1_name: 第一次考试名称
        exam2_name: 第二次考试名称
        output_dir: 输出目录（可选）
    
    Returns:
        dict: 分析结果
    """
    # 获取 access_token
    token = get_access_token()
    if not token:
        return None
    
    # 读取两次考试数据
    print(f"正在读取 {exam1_name} 考试数据...")
    values1 = read_sheet_range(token, spreadsheet_token, sheet1_id)
    students1 = parse_table_data(values1, key_field="学号")
    # 确保学号是字符串
    for s in students1:
        if "学号" in s:
            s["学号"] = str(s["学号"])
    print(f"✅ 读取到 {len(students1)} 条记录\n")
    
    print(f"正在读取 {exam2_name} 考试数据...")
    values2 = read_sheet_range(token, spreadsheet_token, sheet2_id)
    students2 = parse_table_data(values2, key_field="学号")
    for s in students2:
        if "学号" in s:
            s["学号"] = str(s["学号"])
    print(f"✅ 读取到 {len(students2)} 条记录\n")
    
    # 对比分析
    result = compare_exams(students1, students2, exam1_name, exam2_name)
    
    # 保存结果
    if output_dir and result:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "考试对比分析.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 分析结果已保存到: {output_file}")
    
    return result

def compare_exams(students1, students2, exam1_name, exam2_name):
    """对比分析两次考试"""
    print(f"\n{'='*60}")
    print(f"📊 最近两次考试成绩对比分析")
    print(f"{'='*60}")
    print(f"第一次考试：{exam1_name}")
    print(f"第二次考试：{exam2_name}")
    print(f"{'='*60}\n")
    
    # 创建学号到学生的映射
    map1 = {s.get("学号"): s for s in students1}
    map2 = {s.get("学号"): s for s in students2}
    
    # 找出共同的学生
    common_ids = set(map1.keys()) & set(map2.keys())
    
    # 计算进退步
    improvements = []
    declines = []
    stable = []
    
    for sid in common_ids:
        s1 = map1[sid]
        s2 = map2[sid]
        
        rank1 = int(s1.get("年级排名", 0) or 0)
        rank2 = int(s2.get("年级排名", 0) or 0)
        
        # 排名越小越好，所以 rank2 < rank1 表示进步
        rank_change = rank1 - rank2  # 正数表示进步
        
        total1 = int(s1.get("总分", 0) or 0)
        total2 = int(s2.get("总分", 0) or 0)
        total_change = total2 - total1
        
        result = {
            "学号": sid,
            "姓名": s1.get("学生姓名"),
            "班级": s1.get("班级"),
            f"{exam1_name}_排名": rank1,
            f"{exam2_name}_排名": rank2,
            "排名变化": rank_change,
            f"{exam1_name}_总分": total1,
            f"{exam2_name}_总分": total2,
            "总分变化": total_change
        }
        
        if rank_change > 0:
            improvements.append(result)
        elif rank_change < 0:
            declines.append(result)
        else:
            stable.append(result)
    
    # 排序
    improvements.sort(key=lambda x: x["排名变化"], reverse=True)
    declines.sort(key=lambda x: x["排名变化"])
    
    # 输出统计
    print(f"📈 总体统计")
    print(f"   学生总数：{len(common_ids)} 人")
    print(f"   进步人数：{len(improvements)} 人")
    print(f"   退步人数：{len(declines)} 人")
    print(f"   持平人数：{len(stable)} 人")
    print()
    
    # 进步明星
    print(f"🌟 进步明星（TOP 10）")
    print(f"   {'姓名':<8} {'班级':<10} {exam1_name+'排名':>8} {exam2_name+'排名':>8} {'排名变化':>8} {'总分变化':>8}")
    print(f"   {'-'*60}")
    for s in improvements[:10]:
        print(f"   {s['姓名']:<8} {s['班级']:<10} {s[f'{exam1_name}_排名']:>8} {s[f'{exam2_name}_排名']:>8} +{s['排名变化']:>7} +{s['总分变化']:>7}")
    print()
    
    # 重点关注
    print(f"⚠️ 重点关注（退步 TOP 10）")
    print(f"   {'姓名':<8} {'班级':<10} {exam1_name+'排名':>8} {exam2_name+'排名':>8} {'排名变化':>8} {'总分变化':>8}")
    print(f"   {'-'*60}")
    for s in declines[:10]:
        print(f"   {s['姓名']:<8} {s['班级']:<10} {s[f'{exam1_name}_排名']:>8} {s[f'{exam2_name}_排名']:>8} {s['排名变化']:>8} {s['总分变化']:>8}")
    print()
    
    # 各科分析
    print(f"📚 各科平均分对比")
    subjects = ["语文", "数学", "英语", "政治", "历史", "地理", "生物"]
    print(f"   {'科目':<8} {exam1_name+'平均分':>12} {exam2_name+'平均分':>12} {'变化':>8}")
    print(f"   {'-'*50}")
    
    subject_avg1 = {}
    subject_avg2 = {}
    
    for subj in subjects:
        scores1 = [int(s1.get(subj, 0) or 0) for s1 in students1 if s1.get(subj)]
        scores2 = [int(s2.get(subj, 0) or 0) for s2 in students2 if s2.get(subj)]
        
        avg1 = sum(scores1) / len(scores1) if scores1 else 0
        avg2 = sum(scores2) / len(scores2) if scores2 else 0
        change = avg2 - avg1
        
        subject_avg1[subj] = avg1
        subject_avg2[subj] = avg2
        
        print(f"   {subj:<8} {avg1:>12.1f} {avg2:>12.1f} {'+' if change >= 0 else ''}{change:>7.1f}")
    
    print()
    
    # 分数段分布
    print(f"📊 分数段分布")
    def get_distribution(students):
        ranges = {
            "600+": 0,
            "550-599": 0,
            "500-549": 0,
            "450-499": 0,
            "400-449": 0,
            "400以下": 0
        }
        for s in students:
            total = int(s.get("总分", 0) or 0)
            if total >= 600:
                ranges["600+"] += 1
            elif total >= 550:
                ranges["550-599"] += 1
            elif total >= 500:
                ranges["500-549"] += 1
            elif total >= 450:
                ranges["450-499"] += 1
            elif total >= 400:
                ranges["400-449"] += 1
            else:
                ranges["400以下"] += 1
        return ranges
    
    dist1 = get_distribution(students1)
    dist2 = get_distribution(students2)
    
    print(f"   {'分数段':<12} {exam1_name:>10} {exam2_name:>10} {'变化':>8}")
    print(f"   {'-'*40}")
    for key in dist1:
        change = dist2[key] - dist1[key]
        print(f"   {key:<12} {dist1[key]:>10} {dist2[key]:>10} {'+' if change >= 0 else ''}{change:>7}")
    
    # 返回结果
    return {
        "exam1": exam1_name,
        "exam2": exam2_name,
        "total_students": len(common_ids),
        "improvements": len(improvements),
        "declines": len(declines),
        "stable": len(stable),
        "improvement_list": improvements[:20],
        "decline_list": declines[:20],
        "subject_avg1": subject_avg1,
        "subject_avg2": subject_avg2,
        "distribution1": dist1,
        "distribution2": dist2
    }

def main():
    if len(sys.argv) < 5:
        print("用法: python analyze_exams.py <spreadsheet_token> <sheet1_id> <sheet2_id> <exam1_name> <exam2_name>")
        print("示例: python analyze_exams.py SXlnsuW9rhhbQPtjHQKciZZXnUf CNHOVc iintOO 2025-11-12 2025-10-25")
        sys.exit(1)
    
    spreadsheet_token = sys.argv[1]
    sheet1_id = sys.argv[2]
    sheet2_id = sys.argv[3]
    exam1_name = sys.argv[4]
    exam2_name = sys.argv[5]
    
    # 默认输出目录
    output_dir = Path(__file__).parent.parent.parent / "data"
    
    analyze_exams(spreadsheet_token, sheet1_id, sheet2_id, exam1_name, exam2_name, output_dir)

if __name__ == "__main__":
    main()
