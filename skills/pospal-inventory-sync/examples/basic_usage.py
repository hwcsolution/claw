#!/usr/bin/env python3
"""
银豹库存同步技能使用示例
"""

import asyncio
import sys
from pathlib import Path

# 添加脚本目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from pospal_client import PospalClient

async def example_single_update():
    """单商品更新示例"""
    print("🔄 单商品更新示例")
    print("="*60)
    
    async with PospalClient() as client:
        # 修改鞋子库存为5
        print("修改鞋子库存为5...")
        success = await client.update_stock("鞋子", 5)
        if success:
            print("✅ 鞋子库存修改成功")
        else:
            print("❌ 鞋子库存修改失败")

async def example_batch_update():
    """批量更新示例"""
    print("🔄 批量更新示例")
    print("="*60)
    
    async with PospalClient() as client:
        # 批量修改库存
        products = {
            "鞋子": 5,
            "衣服": 20,
            "裤子": 15
        }
        
        print(f"批量修改 {len(products)} 个商品...")
        results = await client.batch_update_stock(products)
        
        print(f"批量修改完成:")
        for product, result in results.items():
            if result.get('success'):
                if 'skipped' in result:
                    print(f"  {product}: ⏭️ 跳过 (库存已是目标值)")
                else:
                    print(f"  {product}: ✅ 成功")
            else:
                print(f"  {product}: ❌ 失败")

async def example_check_inventory():
    """库存检查示例"""
    print("🔄 库存检查示例")
    print("="*60)
    
    async with PospalClient() as client:
        # 获取所有商品库存
        print("获取所有商品库存...")
        inventory = await client.get_inventory()
        if inventory:
            print(f"📦 共找到 {len(inventory)} 个商品:")
            for i, product in enumerate(inventory[:10], 1):  # 显示前10个
                print(f"  {i}. {product.get('name', '未知')}: {product.get('stock', '未知')}")
            
            if len(inventory) > 10:
                print(f"  ... 还有 {len(inventory) - 10} 个商品")
            
            # 库存统计
            total_stock = 0
            low_stock = []
            for product in inventory:
                stock = product.get('stock', '0')
                if stock.isdigit():
                    stock_int = int(stock)
                    total_stock += stock_int
                    if stock_int < 10:
                        low_stock.append((product.get('name', '未知'), stock_int))
            
            print(f"\n📊 库存统计:")
            print(f"  商品总数: {len(inventory)}")
            print(f"  总库存量: {total_stock}")
            
            if low_stock:
                print(f"⚠️  低库存商品 ({len(low_stock)} 个):")
                for name, stock in low_stock[:5]:
                    print(f"    {name}: {stock}")
                if len(low_stock) > 5:
                    print(f"    ... 还有 {len(low_stock) - 5} 个")
        else:
            print("❌ 未找到任何商品")
        
        # 查找特定商品
        print("\n🔍 查找鞋子库存...")
        shoes = await client.get_inventory("鞋子")
        if shoes:
            for shoe in shoes:
                print(f"  商品: {shoe.get('name', '未知')}")
                print(f"  库存: {shoe.get('stock', '未知')}")
                print(f"  条码: {shoe.get('barcode', '未知')}")
        else:
            print("⚠️  未找到鞋子商品")

async def example_custom_config():
    """自定义配置示例"""
    print("🔄 自定义配置示例")
    print("="*60)
    print("⚠️  注意：此示例演示如何使用自定义配置文件")
    print("     实际使用时，凭据应通过环境变量管理")
    print("="*60)
    
    # 创建自定义配置（不包含凭据，凭据通过环境变量管理）
    custom_config = {
        "urls": {
            "login": "https://beta74.pospal.cn/account/signin",
            "product_manage": "https://beta74.pospal.cn/Product/Manage"
        },
        "selectors": {
            "username_input": "#txt_userName",
            "password_input": "#txt_password",
            "login_button": "#submitLoginBtn",
            "stock_input": "#edit_stock",
            "save_button_xpath": "/html/body/div[1]/div[2]/div[2]/div[1]/div[7]/div[2]/div[1]"
        },
        "settings": {
            "headless": True,
            "timeout": 30,
            "wait_time": 3,
            "retry_attempts": 3
        }
    }
    
    # 保存临时配置文件
    import json
    import tempfile
    import os
    
    temp_dir = tempfile.gettempdir()
    config_path = os.path.join(temp_dir, "pospal_config_temp.json")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, ensure_ascii=False, indent=2)
    
    print(f"📁 使用临时配置文件: {config_path}")
    print("💡 提示：实际使用时，凭据通过环境变量 POSPAL_USERNAME 和 POSPAL_PASSWORD 管理")
    
    # 检查环境变量
    from env_utils import verify_env_vars
    
    try:
        username, password = verify_env_vars()
        print(f"✅ 环境变量验证成功")
        print(f"   用户名: {username}")
        print(f"   密码长度: {len(password)} 个字符")
    except SystemExit:
        print("❌ 环境变量未设置，无法运行此示例")
        print("💡 请先设置环境变量：")
        print("   export POSPAL_USERNAME='你的用户名'")
        print("   export POSPAL_PASSWORD='你的密码'")
        return
    
    # 使用自定义配置
    async with PospalClient(config_path) as client:
        # 测试连接
        print("测试连接...")
        if await client.login():
            print("✅ 连接成功")
        else:
            print("❌ 连接失败")
    
    # 清理临时文件
    os.remove(config_path)

async def main():
    """主函数"""
    print("银豹库存同步技能使用示例")
    print("="*60)
    print("选择要运行的示例:")
    print("1. 单商品更新")
    print("2. 批量更新")
    print("3. 库存检查")
    print("4. 自定义配置")
    print("5. 全部运行")
    print("="*60)
    
    choice = input("请输入选择 (1-5): ").strip()
    
    if choice == "1":
        await example_single_update()
    elif choice == "2":
        await example_batch_update()
    elif choice == "3":
        await example_check_inventory()
    elif choice == "4":
        await example_custom_config()
    elif choice == "5":
        print("\n运行所有示例...")
        print("\n" + "="*60)
        await example_single_update()
        print("\n" + "="*60)
        await example_batch_update()
        print("\n" + "="*60)
        await example_check_inventory()
        print("\n" + "="*60)
        await example_custom_config()
    else:
        print("❌ 无效选择")
        return
    
    print("\n" + "="*60)
    print("示例执行完成")
    print("="*60)
    
    print("\n💡 更多用法:")
    print("1. 单商品修改:")
    print("   python3 ../scripts/update_single_product.py --product \"鞋子\" --stock 10")
    print("\n2. 批量修改:")
    print("   python3 ../scripts/batch_update.py --file ../scripts/example_products.csv")
    print("\n3. 库存检查:")
    print("   python3 ../scripts/check_inventory.py --export csv")
    print("\n4. 连接测试:")
    print("   python3 ../scripts/test_connection.py")

if __name__ == "__main__":
    asyncio.run(main())