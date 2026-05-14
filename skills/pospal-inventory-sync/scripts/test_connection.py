#!/usr/bin/env python3
"""
银豹系统连接测试脚本
测试系统连接和基本功能
"""

import asyncio
import json
from pathlib import Path
import sys

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from pospal_client import PospalClient

async def test_connection():
    """测试连接"""
    print("🔍 测试银豹系统连接")
    print("="*60)
    
    try:
        # 创建客户端
        client = PospalClient()
        
        # 启动浏览器
        print("1. 🚀 启动浏览器...")
        await client.start()
        print("✅ 浏览器启动成功")
        
        # 测试登录
        print("\n2. 🔐 测试登录...")
        login_success = await client.login()
        if not login_success:
            print("❌ 登录失败")
            return False
        print("✅ 登录成功")
        
        # 测试导航到商品页面
        print("\n3. 📦 测试导航到商品页面...")
        await client.navigate_to_products()
        print("✅ 导航成功")
        
        # 测试查找商品
        print("\n4. 🔍 测试查找商品...")
        product_info = await client.find_product("鞋子")
        if product_info.get('success'):
            print(f"✅ 找到商品: 鞋子")
            print(f"   当前库存: {product_info.get('stock')}")
        else:
            print("⚠️  未找到商品: 鞋子")
            print("💡 尝试查找其他商品...")
            
            # 查找所有商品
            print("\n5. 📋 测试获取所有商品...")
            inventory = await client.get_inventory()
            if inventory:
                print(f"✅ 找到 {len(inventory)} 个商品")
                print("前5个商品:")
                for i, product in enumerate(inventory[:5], 1):
                    print(f"  {i}. {product.get('name', '未知')}: {product.get('stock', '未知')}")
            else:
                print("❌ 未找到任何商品")
                return False
        
        # 测试配置
        print("\n6. ⚙️ 测试配置文件...")
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("✅ 配置文件加载成功")
            print(f"   用户名: {config['credentials']['username']}")
            print(f"   登录URL: {config['urls']['login']}")
            print(f"   商品管理URL: {config['urls']['product_manage']}")
            print(f"   保存按钮XPath: {config['selectors']['save_button_xpath']}")
        else:
            print("❌ 配置文件不存在")
            return False
        
        print("\n" + "="*60)
        print("🎉 连接测试通过！")
        print("="*60)
        
        # 显示可用功能
        print("\n🚀 可用功能:")
        print("1. 单商品库存修改:")
        print("   python3 update_single_product.py --product \"鞋子\" --stock 10")
        
        print("\n2. 批量库存修改:")
        print("   python3 batch_update.py --file example_products.csv")
        
        print("\n3. 库存检查:")
        print("   python3 check_inventory.py")
        print("   python3 check_inventory.py --product \"鞋子\" --export csv")
        
        print("\n4. 使用示例:")
        print("   python3 ../examples/basic_usage.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 关闭浏览器
        if client:
            await client.close()
            print("\n✅ 浏览器已关闭")

async def main():
    """主函数"""
    print("银豹系统连接测试")
    print("="*60)
    print("测试系统连接、登录、商品查找等基本功能")
    print("="*60)
    
    success = await test_connection()
    
    if success:
        print("\n✅ 所有测试通过！技能可以正常使用。")
    else:
        print("\n❌ 测试失败，请检查以下问题:")
        print("  1. 网络连接是否正常")
        print("  2. 用户名密码是否正确")
        print("  3. 配置文件是否正确")
        print("  4. 系统URL是否可访问")
        
        # 检查依赖
        print("\n🔧 检查依赖...")
        try:
            import playwright
            print("✅ playwright 已安装")
        except ImportError:
            print("❌ playwright 未安装")
            print("💡 请运行: pip install playwright")
            print("💡 然后运行: python -m playwright install chromium")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())