#!/usr/bin/env python3
"""
发送学生成绩报告邮件（纯文本版本）
"""

import sys
import json
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from datetime import datetime

# 导入飞书工具模块
sys.path.insert(0, str(Path(__file__).parent))
from feishu_utils import get_access_token, read_sheet_range, parse_table_data

def get_student_data(student_name, spreadsheet_token, sheets_config):
    """获取学生成绩数据"""
    token = get_access_token()
    if not token:
        return None
    
    all_exams = []
    for exam_date, sheet_id in sheets_config.items():
        values = read_sheet_range(token, spreadsheet_token, sheet_id, "A1:P50")
        records = parse_table_data(values, key_field="学号")
        
        for r in records:
            if r.get("学生姓名") == student_name or r.get("姓名") == student_name:
                r["考试日期"] = exam_date
                all_exams.append(r)
                break
    
    return all_exams

def send_email(to_email, subject, body, smtp_config):
    """发送邮件"""
    from email.utils import formataddr
    
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = formataddr((smtp_config['sender_name'], smtp_config['email']))
    msg['To'] = to_email
    msg['Subject'] = subject
    
    with smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port']) as server:
        server.login(smtp_config['email'], smtp_config['auth_code'])
        server.send_message(msg)
    
    return True

def main():
    if len(sys.argv) < 2:
        print("用法: python send_email_report.py <学生姓名> [家长邮箱]")
        sys.exit(1)
    
    student_name = sys.argv[1]
    parent_email = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 读取配置
    config_path = Path(__file__).parent.parent.parent.parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    smtp_config = config.get("smtp", {})
    
    if not smtp_config.get("email"):
        print("❌ SMTP 未配置")
        sys.exit(1)
    
    # 成绩汇总表配置
    spreadsheet_token = "SXlnsuW9rhhbQPtjHQKciZZXnUf"
    sheets_config = {
        "2025-11-12": "CNHOVc",
        "2025-10-25": "iintOO",
        "2025-10-12": "9dd137"
    }
    
    # 获取学生数据
    print(f"正在获取 {student_name} 的成绩数据...")
    exams = get_student_data(student_name, spreadsheet_token, sheets_config)
    
    if not exams:
        print(f"❌ 未找到 {student_name} 的成绩数据")
        sys.exit(1)
    
    print(f"✅ 找到 {len(exams)} 次考试成绩")
    
    # 生成邮件内容
    latest = exams[0]
    subjects = ["语文", "数学", "英语", "政治", "历史", "地理", "生物"]
    
    # 构建邮件正文
    body = f"""
{'='*50}
{student_name}同学考试成绩报告
{'='*50}

【基本信息】
姓名：{student_name}
班级：{latest.get('班级', 'N/A')}
学号：{latest.get('学号', 'N/A')}
报告日期：{datetime.now().strftime('%Y年%m月%d日')}

【最近考试概览】
"""
    
    for i, exam in enumerate(exams):
        date = exam.get("考试日期", "N/A")
        rank = exam.get("年级排名", "N/A")
        total = exam.get("总分", "N/A")
        avg = exam.get("平均分", "N/A")
        
        change_str = ""
        if i < len(exams) - 1:
            prev = exams[i+1]
            prev_rank = int(prev.get("年级排名", 0) or 0)
            curr_rank = int(rank or 0)
            prev_total = int(prev.get("总分", 0) or 0)
            curr_total = int(total or 0)
            
            rank_change = prev_rank - curr_rank
            total_change = curr_total - prev_total
            
            if rank_change > 0:
                change_str = f" [排名↑{rank_change}名, 总分+{total_change}分]"
            elif rank_change < 0:
                change_str = f" [排名↓{abs(rank_change)}名, 总分{total_change}分]"
            else:
                change_str = f" [排名持平, 总分+{total_change}分]"
        
        body += f"  {date}: 年级第{rank}名, 总分{total}分, 平均{avg}分{change_str}\n"
    
    body += f"""
【各科成绩对比】
"""
    
    # 表头
    header = f"  {'科目':<6}"
    for exam in exams:
        header += f" {exam.get('考试日期', 'N/A'):>10}"
    header += f" {'变化':>8}"
    body += header + "\n"
    body += f"  {'-'*50}\n"
    
    for subj in subjects:
        line = f"  {subj:<6}"
        scores = []
        for exam in exams:
            score = exam.get(subj, "N/A")
            scores.append(int(score) if score and score != "N/A" else 0)
            line += f" {str(score):>10}"
        
        if len(scores) >= 2 and scores[0] and scores[1]:
            change = scores[0] - scores[1]
            line += f" {'+' if change >= 0 else ''}{change:>7}"
        else:
            line += f" {'-':>8}"
        
        body += line + "\n"
    
    # 学科分析
    latest_scores = {}
    for subj in subjects:
        score = latest.get(subj)
        if score and score != "N/A":
            latest_scores[subj] = int(score)
    
    if latest_scores:
        sorted_scores = sorted(latest_scores.items(), key=lambda x: x[1], reverse=True)
        body += f"""
【学科分析】
  优势学科：{', '.join([f'{s[0]}({s[1]}分)' for s in sorted_scores[:3]])}
  薄弱学科：{', '.join([f'{s[0]}({s[1]}分)' for s in sorted_scores[-3:]])}
"""
    
    # 教师评语
    latest_rank = int(latest.get("年级排名", 0) or 0)
    body += f"""
【教师评语】
"""
    if latest_rank == 1:
        body += f"  🌟 {student_name}同学本次考试年级第一，表现优异！\n  各科成绩均衡，继续保持，争取更大突破！"
    elif latest_rank <= 5:
        body += f"  👍 {student_name}同学本次考试年级前五，表现优秀！"
    elif latest_rank <= 10:
        body += f"  📈 {student_name}同学本次考试年级前十，表现良好。\n  继续努力，争取进入前五！"
    else:
        body += f"  💪 {student_name}同学要继续努力，争取更大进步！"
    
    body += f"""

【家校沟通】
如需详细了解孩子学习情况，欢迎与老师联系沟通。
让我们共同关注孩子的成长！

祝好！
{smtp_config.get('sender_name', '老师')}
{datetime.now().strftime('%Y年%m月%d日')}
"""
    
    # 发送邮件
    if parent_email:
        print(f"\n正在发送邮件给 {parent_email}...")
        
        subject = f"【成绩报告】{student_name}同学最近考试成绩报告"
        
        send_email(parent_email, subject, body, smtp_config)
        print(f"✅ 邮件已发送成功！")
        
        # 保存报告
        output_dir = Path(__file__).parent.parent.parent / "data" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{student_name}_成绩报告.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"✅ 报告已保存到: {output_file}")
    else:
        print(f"\n⚠️ 未提供家长邮箱")
        print(body)

if __name__ == "__main__":
    main()
