#!/usr/bin/env python3
"""
飞书工具模块 - 自动读取 OpenClaw 配置
"""

import json
import os
import requests
from pathlib import Path

def get_feishu_credentials():
    """
    从 OpenClaw 配置文件自动读取飞书凭证
    
    Returns:
        dict: {"app_id": "...", "app_secret": "..."} 或 None
    """
    # 尝试多个可能的配置文件路径
    config_paths = [
        Path.home() / ".openclaw" / "openclaw.json",
        Path("/home/openclaw/.openclaw/openclaw.json"),
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 查找飞书账号配置
                feishu_config = config.get("channels", {}).get("feishu", {})
                accounts = feishu_config.get("accounts", {})
                
                # 返回第一个账号的凭证
                for account_id, account in accounts.items():
                    if "appId" in account and "appSecret" in account:
                        return {
                            "app_id": account["appId"],
                            "app_secret": account["appSecret"],
                            "account_id": account_id
                        }
            except Exception as e:
                print(f"读取配置文件失败: {e}")
    
    return None

def get_access_token():
    """
    获取飞书 tenant_access_token
    
    Returns:
        str: access_token 或 None
    """
    creds = get_feishu_credentials()
    if not creds:
        print("❌ 未找到飞书凭证，请检查 openclaw.json 配置")
        return None
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": creds["app_id"],
        "app_secret": creds["app_secret"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            return result.get("tenant_access_token")
        else:
            print(f"❌ 获取 access_token 失败: {result.get('msg', result)}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def get_spreadsheet_sheets(token, spreadsheet_token):
    """
    获取电子表格的工作表列表
    
    Args:
        token: tenant_access_token
        spreadsheet_token: 电子表格 token
    
    Returns:
        list: 工作表列表
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            return result.get("data", {}).get("sheets", [])
        else:
            print(f"❌ 获取工作表列表失败: {result.get('msg', result)}")
            return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def read_sheet_range(token, spreadsheet_token, sheet_id, range_str="A1:Z1000"):
    """
    读取工作表数据范围
    
    Args:
        token: tenant_access_token
        spreadsheet_token: 电子表格 token
        sheet_id: 工作表 ID
        range_str: 数据范围（如 "A1:Z100"）
    
    Returns:
        list: 二维数组数据
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}!{range_str}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        result = response.json()
        
        if result.get("code") == 0:
            return result.get("data", {}).get("valueRange", {}).get("values", [])
        else:
            print(f"❌ 读取数据失败: {result.get('msg', result)}")
            return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def parse_table_data(values, key_field=None):
    """
    解析表格数据为字典列表
    
    Args:
        values: 二维数组数据
        key_field: 用作主键的字段名（可选）
    
    Returns:
        list[dict]: 解析后的数据列表
    """
    if not values or len(values) < 2:
        return []
    
    # 获取表头
    headers = values[0]
    
    # 解析数据行
    records = []
    for row in values[1:]:
        if not row or all(v is None or v == "" for v in row):
            continue
        
        record = {}
        for i, header in enumerate(headers):
            if header and i < len(row):
                record[header] = row[i]
        
        # 如果指定了主键字段，检查是否存在
        if key_field and not record.get(key_field):
            continue
        
        records.append(record)
    
    return records

# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("飞书工具模块测试")
    print("=" * 50)
    
    # 测试读取凭证
    creds = get_feishu_credentials()
    if creds:
        print(f"✅ 找到飞书凭证:")
        print(f"   账号ID: {creds['account_id']}")
        print(f"   App ID: {creds['app_id'][:10]}...")
    else:
        print("❌ 未找到飞书凭证")
    
    # 测试获取 token
    token = get_access_token()
    if token:
        print(f"✅ 获取 access_token 成功: {token[:20]}...")
    else:
        print("❌ 获取 access_token 失败")
