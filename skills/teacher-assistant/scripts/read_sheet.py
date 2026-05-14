#!/usr/bin/env python3
"""
飞书电子表格读取脚本
支持命令行调用和模块导入
"""

import json
import sys
from pathlib import Path

# 导入飞书工具模块
sys.path.insert(0, str(Path(__file__).parent))
from feishu_utils import get_access_token, get_spreadsheet_sheets, read_sheet_range, parse_table_data

def read_spreadsheet(spreadsheet_token, sheet_id=None, output_dir=None):
    """
    读取飞书电子表格
    
    Args:
        spreadsheet_token: 电子表格 token
        sheet_id: 工作表 ID（可选，默认第一个）
        output_dir: 输出目录（可选）
    
    Returns:
        dict: {"sheets": [...], "data": [...], "records": [...]}
    """
    # 获取 access_token
    token = get_access_token()
    if not token:
        return None
    
    # 获取工作表列表
    sheets = get_spreadsheet_sheets(token, spreadsheet_token)
    if not sheets:
        print(f"❌ 未找到工作表")
        return None
    
    print(f"✅ 找到 {len(sheets)} 个工作表:")
    for s in sheets:
        print(f"   - {s.get('title')} (sheet_id: {s.get('sheet_id')})")
    
    # 如果没有指定 sheet_id，使用第一个工作表
    if not sheet_id and sheets:
        sheet_id = sheets[0].get("sheet_id")
        print(f"\n使用工作表: {sheets[0].get('title')}")
    
    # 读取数据
    print(f"\n正在读取数据...")
    values = read_sheet_range(token, spreadsheet_token, sheet_id)
    
    if not values:
        print(f"❌ 未读取到数据")
        return None
    
    print(f"✅ 读取到 {len(values)} 行数据")
    
    # 解析数据
    records = parse_table_data(values)
    print(f"✅ 解析出 {len(records)} 条记录")
    
    result = {
        "spreadsheet_token": spreadsheet_token,
        "sheet_id": sheet_id,
        "sheets": sheets,
        "data": values,
        "records": records
    }
    
    # 保存到文件
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{spreadsheet_token}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存到: {output_file}")
    
    return result

def main():
    if len(sys.argv) < 2:
        print("用法: python read_feishu_sheet.py <spreadsheet_token> [sheet_id]")
        print("示例: python read_feishu_sheet.py GSDVskQu1hygMDtGJGTcDzYan6b")
        sys.exit(1)
    
    spreadsheet_token = sys.argv[1]
    sheet_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 默认输出目录
    output_dir = Path(__file__).parent.parent.parent / "data"
    
    result = read_spreadsheet(spreadsheet_token, sheet_id, output_dir)
    
    if result:
        print("\n数据预览（前5条）:")
        for i, record in enumerate(result["records"][:5]):
            print(f"  {i+1}. {record}")

if __name__ == "__main__":
    main()
