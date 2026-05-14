#!/usr/bin/env python3
"""
环境变量工具模块
统一处理银豹系统环境变量相关功能
"""

import os
import sys
from pathlib import Path

def check_env_vars(exit_on_error=True):
    """
    检查必要的环境变量是否已设置
    
    Args:
        exit_on_error: 如果环境变量未设置，是否退出程序
    
    Returns:
        tuple: (username, password) 如果环境变量已设置
        None: 如果环境变量未设置且 exit_on_error=False
    
    Raises:
        SystemExit: 如果环境变量未设置且 exit_on_error=True
    """
    username = os.getenv('POSPAL_USERNAME')
    password = os.getenv('POSPAL_PASSWORD')
    
    if not username or not password:
        if exit_on_error:
            print("❌ 错误：环境变量 POSPAL_USERNAME 和 POSPAL_PASSWORD 未设置")
            print("💡 请先设置环境变量：")
            print("   1. 运行 ./setup_env.sh 设置凭据")
            print("   2. 或者直接设置环境变量：")
            print("      export POSPAL_USERNAME='你的用户名'")
            print("      export POSPAL_PASSWORD='你的密码'")
            print("   3. 或者运行：source ~/.pospal_env")
            sys.exit(1)
        else:
            return None
    
    return username, password

def load_env_from_file(env_file=None):
    """
    从配置文件加载环境变量
    
    Args:
        env_file: 环境变量文件路径，默认为 ~/.pospal_env
    
    Returns:
        bool: 是否成功加载
    """
    if env_file is None:
        env_file = Path.home() / ".pospal_env"
    
    if not env_file.exists():
        print(f"❌ 环境变量文件不存在: {env_file}")
        print("💡 请运行 setup_env.sh 创建配置文件")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        os.environ[key] = value
                        print(f"✅ 加载环境变量: {key}")
        
        return True
    except Exception as e:
        print(f"❌ 加载环境变量文件失败: {e}")
        return False

def verify_env_vars():
    """
    验证环境变量并返回凭据
    
    Returns:
        tuple: (username, password)
    """
    # 首先检查环境变量是否已设置
    result = check_env_vars(exit_on_error=False)
    if result:
        username, password = result
        print("✅ 环境变量检查通过")
        print(f"   用户名: {username}")
        print(f"   密码: {'*' * len(password)}")
        return username, password
    
    # 如果未设置，尝试从配置文件加载
    print("🔍 尝试从配置文件加载环境变量...")
    if load_env_from_file():
        result = check_env_vars(exit_on_error=False)
        if result:
            username, password = result
            print("✅ 从配置文件加载成功")
            print(f"   用户名: {username}")
            print(f"   密码: {'*' * len(password)}")
            return username, password
    
    # 如果都失败，显示错误信息并退出
    print("❌ 无法获取银豹系统凭据")
    print("💡 请使用以下方法之一设置凭据：")
    print("   1. 运行 ./setup_env.sh 设置凭据")
    print("   2. 设置环境变量：")
    print("      export POSPAL_USERNAME='你的用户名'")
    print("      export POSPAL_PASSWORD='你的密码'")
    print("   3. 创建 ~/.pospal_env 文件：")
    print("      echo 'POSPAL_USERNAME=\"你的用户名\"' > ~/.pospal_env")
    print("      echo 'POSPAL_PASSWORD=\"你的密码\"' >> ~/.pospal_env")
    print("      chmod 600 ~/.pospal_env")
    sys.exit(1)

if __name__ == "__main__":
    """命令行入口：检查环境变量"""
    print("="*60)
    print("银豹系统环境变量检查")
    print("="*60)
    
    try:
        username, password = verify_env_vars()
        print(f"\n✅ 环境变量验证成功！")
        print(f"   用户名: {username}")
        print(f"   密码长度: {len(password)} 个字符")
    except SystemExit:
        pass  # 错误信息已在 verify_env_vars 中显示