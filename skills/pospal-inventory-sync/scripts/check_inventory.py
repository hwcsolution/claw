#!/usr/bin/env python3
"""
银豹系统 - 库存检查脚本
用法: 
  python3 check_inventory.py                     # 查看所有商品
  python3 check_inventory.py --product "鞋子"    # 查看指定商品
  python3 check_inventory.py --export csv        # 导出为CSV
"""

import asyncio
import argparse
import json
import csv
from pathlib import Path
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from pospal_client import PospalClient

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='银豹系统库存检查')
    parser.add_argument('--product', '-p', type=str, help='商品名称（支持模糊匹配）')
    parser.add_argument('--export', '-e', choices=['csv', 'json'], help='导出格式')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print("="*60)
    print("银豹系统库存检查")
    print("="*60)
    
    if args.product:
        print(f"🔍 查找商品: {args.product}")
    else:
        print("📋 查看所有商品库存")
    
    if args.export:
        print(f"💾 导出格式: {args.export.upper()}")
    
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
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
        
        # 获取库存信息
        print("📊 获取库存信息...")
        inventory = await client.get_inventory(args.product)
        
        if not inventory:
            print("❌ 未获取到库存信息")
            return
        
        # 显示库存信息
        print(f"\n📦 找到 {len(inventory)} 个商品:")
        print("-"*60)
        
        # 表头
        print(f"{'序号':<4} {'商品名称':<20} {'条码':<15} {'库存':<10} {'进价':<10} {'售价':<10}")
        print("-"*60)
        
        for i, product in enumerate(inventory, 1):
            name = product.get('name', '未知')[:18] + '..' if len(product.get('name', '')) > 18 else product.get('name', '未知')
            barcode = product.get('barcode', '未知')[:13] + '..' if len(product.get('barcode', '')) > 13 else product.get('barcode', '未知')
            stock = product.get('stock', '未知')
            buy_price = product.get('buyPrice', '未知')
            sell_price = product.get('sellPrice', '未知')
            
            print(f"{i:<4} {name:<20} {barcode:<15} {stock:<10} {buy_price:<10} {sell_price:<10}")
        
        print("-"*60)
        
        # 统计信息
        if inventory:
            total_stock = sum(float(p.get('stock', 0)) for p in inventory if p.get('stock', '').replace('.', '').isdigit())
            print(f"📊 库存统计:")
            print(f"  商品总数: {len(inventory)}")
            print(f"  总库存量: {total_stock}")
            
            # 低库存预警
            low_stock_items = [p for p in inventory if p.get('stock', '').isdigit() and int(p.get('stock', 0)) < 10]
            if low_stock_items:
                print(f"⚠️  低库存商品 ({len(low_stock_items)} 个):")
                for item in low_stock_items[:5]:  # 显示前5个
                    print(f"    {item.get('name', '未知')}: {item.get('stock')}")
                if len(low_stock_items) > 5:
                    print(f"    ... 还有 {len(low_stock_items) - 5} 个")
        
        # 导出数据
        if args.export:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = args.output or f"inventory_{timestamp}.{args.export}"
            
            if args.export == 'csv':
                with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=['商品名称', '条码', '库存', '进价', '售价', '检查时间'])
                    writer.writeheader()
                    for product in inventory:
                        product['检查时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow(product)
                print(f"\n💾 数据已导出为CSV: {output_file}")
                
            elif args.export == 'json':
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_items': len(inventory),
                    'inventory': inventory
                }
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                print(f"\n💾 数据已导出为JSON: {output_file}")
        
        # 如果指定了商品，显示详细信息
        if args.product and inventory:
            print(f"\n🔍 商品 '{args.product}' 的详细信息:")
            print("-"*60)
            
            matched_products = [p for p in inventory if args.product in p.get('name', '')]
            
            if matched_products:
                for product in matched_products:
                    print(f"商品名称: {product.get('name', '未知')}")
                    print(f"条码: {product.get('barcode', '未知')}")
                    print(f"库存: {product.get('stock', '未知')}")
                    print(f"进价: {product.get('buyPrice', '未知')}")
                    print(f"售价: {product.get('sellPrice', '未知')}")
                    print("-"*60)
            else:
                print(f"⚠️  未找到完全匹配的商品: {args.product}")
                print("💡 尝试模糊匹配的商品:")
                for product in inventory[:10]:  # 显示前10个
                    print(f"  {product.get('name', '未知')}")
        
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