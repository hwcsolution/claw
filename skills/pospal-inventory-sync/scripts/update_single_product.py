#!/usr/bin/env python3
"""
银豹系统 - 单商品库存修改脚本
用法: python3 update_single_product.py --product "商品名称" --stock 数量 [--debug]
"""

import asyncio
import argparse
import json
from pathlib import Path
import sys

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from pospal_client import PospalClient

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='银豹系统单商品库存修改')
    parser.add_argument('--product', '-p', type=str, required=True, help='商品名称')
    parser.add_argument('--stock', '-s', type=int, required=True, help='目标库存数量')
    parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--no-verify', action='store_true', help='不验证修改结果')
    
    args = parser.parse_args()
    
    print("="*60)
    print("银豹系统单商品库存修改")
    print("="*60)
    print(f"商品: {args.product}")
    print(f"目标库存: {args.stock}")
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    print(f"验证结果: {'关闭' if args.no_verify else '开启'}")
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
        
        # 执行库存修改
        success = await client.update_stock(
            product_name=args.product,
            new_stock=args.stock,
            verify=not args.no_verify
        )
        
        # 生成报告
        print("\n" + "="*60)
        print("📋 执行报告")
        print("="*60)
        print(f"执行时间: {asyncio.get_event_loop().time()}")
        print(f"商品: {args.product}")
        print(f"目标库存: {args.stock}")
        print(f"状态: {'成功 ✅' if success else '失败 ❌'}")
        
        if success:
            print("\n🎉 库存修改成功完成！")
        else:
            print("\n❌ 库存修改失败")
            print("💡 请检查:")
            print("  1. 商品名称是否正确")
            print("  2. 网络连接是否正常")
            print("  3. 登录凭据是否正确")
            print("  4. 保存按钮路径是否正确")
        
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