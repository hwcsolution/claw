#!/usr/bin/env python3
"""
银豹系统 - 批量库存修改脚本
用法: 
  python3 batch_update.py --file products.csv
  python3 batch_update.py --json '{"鞋子": 5, "衣服": 20}'
"""

import asyncio
import argparse
import json
import csv
from pathlib import Path
import sys

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from pospal_client import PospalClient

def load_products_from_csv(file_path):
    """从CSV文件加载商品信息"""
    products = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'product' in row and 'stock' in row:
                    products[row['product']] = int(row['stock'])
        return products
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {e}")
        return None

def load_products_from_json(json_str):
    """从JSON字符串加载商品信息"""
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"❌ 解析JSON失败: {e}")
        return None

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='银豹系统批量库存修改')
    parser.add_argument('--file', '-f', type=str, help='CSV文件路径（包含product,stock列）')
    parser.add_argument('--json', '-j', type=str, help='JSON字符串，格式: {"商品1": 库存1, "商品2": 库存2}')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    parser.add_argument('--no-verify', action='store_true', help='不验证修改结果')
    
    args = parser.parse_args()
    
    # 检查输入参数
    if not args.file and not args.json:
        print("❌ 请指定商品数据源：--file 或 --json")
        parser.print_help()
        return
    
    print("="*60)
    print("银豹系统批量库存修改")
    print("="*60)
    
    # 加载商品数据
    products = {}
    
    if args.file:
        print(f"📁 从CSV文件加载: {args.file}")
        products = load_products_from_csv(args.file)
    elif args.json:
        print("📋 从JSON加载商品数据")
        products = load_products_from_json(args.json)
    
    if not products:
        print("❌ 未加载到商品数据")
        return
    
    print(f"📦 商品数量: {len(products)}")
    for product, stock in products.items():
        print(f"  {product}: {stock}")
    
    print(f"🔍 调试模式: {'开启' if args.debug else '关闭'}")
    print(f"✅ 验证结果: {'关闭' if args.no_verify else '开启'}")
    print("="*60)
    
    # 加载配置
    config_path = args.config or (Path(__file__).parent / "config.json")
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("💡 请创建配置文件或使用 --config 参数指定配置文件")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if args.debug:
        print("🔍 调试模式: 显示详细日志")
        config["settings"]["headless"] = False  # 显示浏览器窗口
    
    # 创建客户端
    client = PospalClient(config_path)
    
    try:
        # 启动浏览器
        await client.start()
        
        # 登录系统
        if not await client.login():
            print("❌ 登录失败，停止批量操作")
            return
        
        # 进入商品页面
        await client.navigate_to_products()
        
        results = {}
        
        # 批量修改库存
        for product_name, new_stock in products.items():
            print(f"\n🔄 处理商品: {product_name} -> {new_stock}")
            
            # 查找商品
            product_info = await client.find_product(product_name)
            if not product_info.get('success'):
                print(f"❌ 未找到商品: {product_name}")
                results[product_name] = {'success': False, 'error': '商品未找到'}
                continue
            
            initial_stock = product_info.get('stock')
            
            # 如果库存已经是目标值，跳过
            if initial_stock == str(new_stock):
                print(f"✅ 库存已经是目标值: {new_stock}，跳过修改")
                results[product_name] = {'success': True, 'skipped': True, 'stock': initial_stock}
                continue
            
            # 点击编辑
            if not await client.edit_product(product_info.get('rowIndex')):
                results[product_name] = {'success': False, 'error': '编辑失败'}
                continue
            
            # 修改库存
            if not await client.update_stock_field(new_stock):
                results[product_name] = {'success': False, 'error': '修改库存失败'}
                continue
            
            # 保存修改
            if not await client.save_changes():
                results[product_name] = {'success': False, 'error': '保存失败'}
                continue
            
            # 确认对话框
            await client.confirm_dialog()
            
            # 等待保存完成
            print("⏳ 等待保存完成...")
            await asyncio.sleep(10)
            
            # 验证修改
            if not args.no_verify:
                print("🔄 验证修改...")
                await client.navigate_to_products()
                
                verify_info = await client.find_product(product_name)
                if verify_info.get('success'):
                    final_stock = verify_info.get('stock')
                    
                    if final_stock == str(new_stock):
                        print(f"✅ {product_name} 库存修改成功: {initial_stock} -> {final_stock}")
                        results[product_name] = {'success': True, 'initial': initial_stock, 'final': final_stock}
                    else:
                        print(f"⚠️ {product_name} 库存未更新: {initial_stock} -> {final_stock}")
                        results[product_name] = {'success': False, 'initial': initial_stock, 'final': final_stock}
                else:
                    print(f"⚠️ 验证时未找到商品: {product_name}")
                    results[product_name] = {'success': False, 'error': '验证失败'}
            else:
                print(f"✅ {product_name} 库存修改已提交")
                results[product_name] = {'success': True, 'initial': initial_stock, 'final': '未验证'}
            
            # 等待一下再处理下一个
            await asyncio.sleep(3)
        
        # 生成报告
        print("\n" + "="*60)
        print("📋 批量修改报告")
        print("="*60)
        
        success_count = sum(1 for r in results.values() if r.get('success'))
        total_count = len(results)
        skipped_count = sum(1 for r in results.values() if r.get('skipped'))
        
        print(f"总计: {total_count} 个商品")
        print(f"成功: {success_count} 个")
        print(f"跳过: {skipped_count} 个")
        print(f"失败: {total_count - success_count - skipped_count} 个")
        print()
        
        for product_name, result in results.items():
            if result.get('skipped'):
                print(f"  {product_name}: ⏭️ 跳过 (库存: {result.get('stock')})")
            elif result.get('success'):
                if 'final' in result:
                    print(f"  {product_name}: ✅ 成功 ({result.get('initial')} -> {result.get('final')})")
                else:
                    print(f"  {product_name}: ✅ 成功")
            else:
                error = result.get('error', '未知错误')
                print(f"  {product_name}: ❌ 失败 ({error})")
        
        # 保存结果到文件
        result_file = Path(__file__).parent / "batch_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细结果已保存到: {result_file}")
        
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 关闭浏览器
        await client.close()
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())