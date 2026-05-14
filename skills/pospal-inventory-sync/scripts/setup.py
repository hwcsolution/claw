#!/usr/bin/env python3
"""
银豹库存同步技能安装脚本
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    # 检查playwright
    try:
        import playwright
        print("✅ playwright 已安装")
    except ImportError:
        print("❌ playwright 未安装")
        return False
    
    return True

def install_playwright():
    """安装playwright"""
    print("📦 安装playwright...")
    
    try:
        # 安装playwright
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        print("✅ playwright 安装成功")
        
        # 安装浏览器
        print("🌐 安装浏览器...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ 浏览器安装成功")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

def create_config_file():
    """创建配置文件"""
    print("⚙️ 创建配置文件...")
    
    config_path = Path(__file__).parent / "config.json"
    
    if config_path.exists():
        print(f"✅ 配置文件已存在: {config_path}")
        return True
    
    # 默认配置（不包含凭据）
    config = {
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
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✅ 配置文件创建成功: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def create_example_files():
    """创建示例文件"""
    print("📝 创建示例文件...")
    
    # 创建示例CSV文件
    example_csv = Path(__file__).parent / "example_products.csv"
    if not example_csv.exists():
        csv_content = """product,stock
鞋子,5
衣服,20
裤子,15
"""
        try:
            with open(example_csv, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            print(f"✅ 示例CSV文件创建成功: {example_csv}")
        except Exception as e:
            print(f"❌ 创建示例CSV文件失败: {e}")
    
    # 创建使用示例
    example_dir = Path(__file__).parent.parent / "examples"
    example_dir.mkdir(exist_ok=True)
    
    example_py = example_dir / "basic_usage.py"
    if not example_py.exists():
        py_content = '''#!/usr/bin/env python3
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
        
        results = await client.batch_update_stock(products)
        print(f"批量修改完成: {len(results)} 个商品")

async def example_check_inventory():
    """库存检查示例"""
    print("🔄 库存检查示例")
    print("="*60)
    
    async with PospalClient() as client:
        # 获取所有商品库存
        inventory = await client.get_inventory()
        if inventory:
            print(f"📦 共找到 {len(inventory)} 个商品:")
            for product in inventory[:5]:  # 显示前5个
                print(f"  {product.get('name', '未知')}: {product.get('stock', '未知')}")
            
            # 查找特定商品
            shoes = await client.get_inventory("鞋子")
            if shoes:
                print(f"\n🔍 鞋子库存: {shoes[0].get('stock', '未知')}")

async def main():
    """主函数"""
    print("银豹库存同步技能使用示例")
    print("="*60)
    
    # 示例1: 单商品更新
    await example_single_update()
    
    # 示例2: 批量更新
    # await example_batch_update()
    
    # 示例3: 库存检查
    # await example_check_inventory()
    
    print("="*60)
    print("示例执行完成")

if __name__ == "__main__":
    asyncio.run(main())
'''
        try:
            with open(example_py, 'w', encoding='utf-8') as f:
                f.write(py_content)
            print(f"✅ 使用示例创建成功: {example_py}")
        except Exception as e:
            print(f"❌ 创建使用示例失败: {e}")
    
    return True

def set_executable_permissions():
    """设置执行权限"""
    print("🔧 设置执行权限...")
    
    script_dir = Path(__file__).parent
    
    scripts = [
        "update_single_product.py",
        "batch_update.py",
        "check_inventory.py",
        "setup.py"
    ]
    
    for script in scripts:
        script_path = script_dir / script
        if script_path.exists():
            try:
                script_path.chmod(0o755)
                print(f"✅ 设置执行权限: {script}")
            except Exception as e:
                print(f"⚠️  无法设置权限 {script}: {e}")
    
    return True

def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎯 银豹库存同步技能安装完成")
    print("="*60)
    
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    
    print(f"\n📁 技能目录: {skill_dir}")
    print(f"📁 脚本目录: {script_dir}")
    
    print("\n🚀 使用方法:")
    
    print("\n1. 📝 设置环境变量:")
    print(f"   cd {script_dir}")
    print(f"   ./setup_env.sh")
    print("   或手动设置:")
    print("   export POSPAL_USERNAME='你的用户名'")
    print("   export POSPAL_PASSWORD='你的密码'")
    
    print("\n2. ✅ 验证环境变量:")
    print(f"   python3 {script_dir}/env_utils.py")
    
    print("\n3. 🔗 测试连接:")
    print(f"   python3 {script_dir}/test_connection.py")
    
    print("\n4. 🛒 单商品库存修改:")
    print(f"   python3 {script_dir}/update_single_product.py --product \"鞋子\" --stock 5")
    
    print("\n5. 📦 批量库存修改:")
    print(f"   python3 {script_dir}/batch_update.py --file {script_dir}/example_products.csv")
    print(f"   python3 {script_dir}/batch_update.py --json '\"{{\"鞋子\": 5, \"衣服\": 20}}\"'")
    
    print("\n6. 📊 库存检查:")
    print(f"   python3 {script_dir}/check_inventory.py")
    print(f"   python3 {script_dir}/check_inventory.py --product \"鞋子\"")
    print(f"   python3 {script_dir}/check_inventory.py --export csv")
    
    print("\n⚙️  配置文件:")
    print(f"   {script_dir}/config.json")
    print("   配置文件不包含敏感信息，仅包含URL和选择器设置")
    
    print("\n📝 示例文件:")
    print(f"   {script_dir}/example_products.csv")
    print(f"   {skill_dir}/examples/basic_usage.py")
    print(f"   {skill_dir}/examples/env_usage_example.sh")
    
    print("\n🔧 常用参数:")
    print("   --debug: 启用调试模式（显示浏览器窗口）")
    print("   --no-verify: 不验证修改结果")
    print("   --config: 指定配置文件路径")
    
    print("\n💡 提示:")
    print("   1. 首次运行可能需要安装依赖: pip install playwright")
    print("   2. 使用前必须先设置环境变量")
    print("   3. 批量操作建议先测试单个商品")
    print("   4. 凭据通过环境变量管理，更安全")
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("银豹库存同步技能安装程序")
    print("="*60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n📦 安装缺失的依赖...")
        if not install_playwright():
            print("❌ 依赖安装失败")
            return False
    
    # 创建配置文件
    if not create_config_file():
        print("❌ 配置文件创建失败")
        return False
    
    # 创建示例文件
    if not create_example_files():
        print("⚠️  示例文件创建失败，但技能仍可使用")
    
    # 设置执行权限
    if not set_executable_permissions():
        print("⚠️  权限设置失败，但技能仍可使用")
    
    # 显示使用说明
    show_usage()
    
    print("\n✅ 安装完成！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)