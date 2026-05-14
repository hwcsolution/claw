#!/usr/bin/env python3
"""
银豹POS系统客户端 - 核心类
提供银豹系统的自动化操作接口
"""

import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright

# 导入环境变量工具
from env_utils import verify_env_vars

class PospalClient:
    """银豹POS系统客户端"""
    
    def __init__(self, config_path=None):
        """初始化客户端"""
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 从环境变量读取凭据
        self.username, self.password = verify_env_vars()
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config["settings"]["headless"]
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1400, "height": 900}
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.config["settings"]["timeout"] * 1000)
        
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def login(self):
        """登录银豹系统"""
        print("🔐 登录系统...")
        
        await self.page.goto(
            self.config["urls"]["login"],
            wait_until="networkidle"
        )
        await asyncio.sleep(2)
        
        # 填写用户名密码（从环境变量读取）
        await self.page.fill(
            self.config["selectors"]["username_input"],
            self.username
        )
        await self.page.fill(
            self.config["selectors"]["password_input"],
            self.password
        )
        
        # 点击登录按钮
        await self.page.click(self.config["selectors"]["login_button"])
        await asyncio.sleep(5)
        
        # 验证登录成功
        current_url = self.page.url
        if "Product/Manage" in current_url or "account/signin" not in current_url:
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录失败")
            return False
    
    async def navigate_to_products(self):
        """导航到商品管理页面"""
        print("📦 进入商品页面...")
        
        await self.page.goto(
            self.config["urls"]["product_manage"],
            wait_until="networkidle"
        )
        await asyncio.sleep(self.config["settings"]["wait_time"])
        print("✅ 进入商品管理页面")
        
    async def find_product(self, product_name):
        """查找商品并返回库存信息"""
        print(f"🔍 查找商品: {product_name}...")
        
        result = await self.page.evaluate(f'''(productName) => {{
            const tables = document.querySelectorAll('table');
            for (const table of tables) {{
                const rows = table.querySelectorAll('tr');
                for (let i = 1; i < rows.length; i++) {{
                    const cells = rows[i].querySelectorAll('td');
                    if (cells.length > 3) {{
                        const nameCell = cells[3];
                        if (nameCell.textContent.includes(productName) && cells.length > 11) {{
                            return {{
                                success: true,
                                stock: cells[11].textContent.trim(),
                                rowIndex: i,
                                productName: nameCell.textContent.trim()
                            }};
                        }}
                    }}
                }}
            }}
            return {{ success: false, message: "未找到商品" }};
        }}''', product_name)
        
        if result.get('success'):
            print(f"✅ 找到商品: {result.get('productName')}")
            print(f"   当前库存: {result.get('stock')}")
            return result
        else:
            print(f"❌ {result.get('message')}: {product_name}")
            return result
    
    async def edit_product(self, row_index):
        """点击编辑按钮"""
        print("✏️ 点击编辑按钮...")
        
        result = await self.page.evaluate('''(rowIndex) => {
            const tables = document.querySelectorAll('table');
            for (const table of tables) {
                const rows = table.querySelectorAll('tr');
                if (rowIndex < rows.length) {
                    const cells = rows[rowIndex].querySelectorAll('td');
                    if (cells.length > 1) {
                        const buttons = cells[1].querySelectorAll('button, a, span');
                        for (const btn of buttons) {
                            if (btn.textContent.includes('编辑')) {
                                btn.click();
                                return { success: true };
                            }
                        }
                    }
                }
            }
            return { success: false, message: "未找到编辑按钮" };
        }''', row_index)
        
        if result.get('success'):
            print("✅ 点击编辑按钮成功")
            await asyncio.sleep(self.config["settings"]["wait_time"])
            return True
        else:
            print(f"❌ {result.get('message')}")
            return False
    
    async def update_stock_field(self, new_stock):
        """修改库存字段"""
        print(f"🔧 修改库存字段为: {new_stock}...")
        
        result = await self.page.evaluate('''(newStock) => {
            const stockInput = document.querySelector('#edit_stock');
            if (stockInput) {
                const oldValue = stockInput.value;
                stockInput.value = newStock;
                stockInput.setAttribute('value', newStock);
                
                // 触发事件
                ['input', 'change', 'blur'].forEach(eventName => {
                    const event = new Event(eventName, { bubbles: true, cancelable: true });
                    stockInput.dispatchEvent(event);
                });
                
                return { success: true, oldValue: oldValue, newValue: newStock };
            }
            return { success: false, message: "未找到库存输入框" };
        }''', str(new_stock))
        
        if result.get('success'):
            print(f"✅ 库存已修改: {result['oldValue']} -> {result['newValue']}")
            return True
        else:
            print(f"❌ {result.get('message')}")
            return False
    
    async def save_changes(self):
        """保存修改"""
        print("💾 点击保存按钮...")
        
        save_button_xpath = self.config["selectors"]["save_button_xpath"]
        
        try:
            save_button = await self.page.wait_for_selector(
                f'xpath={save_button_xpath}',
                timeout=5000
            )
            if save_button:
                await save_button.click()
                print("✅ 点击保存按钮成功")
                return True
            else:
                print("❌ 未找到保存按钮")
                return False
        except Exception as e:
            print(f"❌ 点击保存按钮失败: {e}")
            return False
    
    async def confirm_dialog(self):
        """处理确认对话框"""
        print("⏳ 处理确认对话框...")
        await asyncio.sleep(2)
        
        result = await self.page.evaluate('''() => {
            const elements = document.querySelectorAll('*');
            for (const el of elements) {
                const text = el.textContent || el.innerText || '';
                if (text.trim() === '确定' || text.trim() === '确认' || text.trim() === '是' || text.trim() === 'OK') {
                    console.log('找到确认按钮:', text.trim());
                    el.click();
                    return { success: true, text: text.trim() };
                }
            }
            return { success: false, message: "未找到确认按钮" };
        }''')
        
        if result.get('success'):
            print(f"✅ 已点击确认按钮: '{result.get('text')}'")
            return True
        else:
            print(f"⚠️ {result.get('message')}")
            return False
    
    async def update_stock(self, product_name, new_stock, verify=True):
        """更新商品库存"""
        print(f"\n🔄 开始修改库存: {product_name} -> {new_stock}")
        print("="*60)
        
        try:
            # 登录系统
            if not await self.login():
                return False
            
            # 进入商品页面
            await self.navigate_to_products()
            
            # 查找商品
            product_info = await self.find_product(product_name)
            if not product_info.get('success'):
                return False
            
            initial_stock = product_info.get('stock')
            
            # 点击编辑
            if not await self.edit_product(product_info.get('rowIndex')):
                return False
            
            # 修改库存
            if not await self.update_stock_field(new_stock):
                return False
            
            # 保存修改
            if not await self.save_changes():
                return False
            
            # 确认对话框
            await self.confirm_dialog()
            
            # 等待保存完成
            print("⏳ 等待保存完成...")
            await asyncio.sleep(10)
            
            # 验证修改
            if verify:
                print("🔄 验证修改...")
                await self.navigate_to_products()
                
                verify_info = await self.find_product(product_name)
                if verify_info.get('success'):
                    final_stock = verify_info.get('stock')
                    print(f"📊 验证库存: {final_stock}")
                    
                    if final_stock == str(new_stock):
                        print(f"\n🎉 {product_name} 库存修改成功！")
                        print(f"✅ 库存已从 {initial_stock} 改为 {new_stock}")
                        return True
                    else:
                        print(f"\n⚠️ 库存仍为 {final_stock}")
                        return False
                else:
                    print(f"⚠️ 未找到商品: {product_name}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_inventory(self, product_name=None):
        """获取库存信息"""
        try:
            # 登录系统
            if not await self.login():
                return None
            
            # 进入商品页面
            await self.navigate_to_products()
            
            # 获取所有商品信息
            result = await self.page.evaluate('''() => {
                const products = [];
                const tables = document.querySelectorAll('table');
                
                for (const table of tables) {
                    const rows = table.querySelectorAll('tr');
                    for (let i = 1; i < rows.length; i++) {
                        const cells = rows[i].querySelectorAll('td');
                        if (cells.length > 11) {
                            const product = {
                                name: cells[3]?.textContent?.trim() || '',
                                barcode: cells[4]?.textContent?.trim() || '',
                                stock: cells[11]?.textContent?.trim() || '',
                                buyPrice: cells[13]?.textContent?.trim() || '',
                                sellPrice: cells[14]?.textContent?.trim() || ''
                            };
                            products.push(product);
                        }
                    }
                }
                return products;
            }''')
            
            if product_name:
                # 过滤指定商品
                filtered = [p for p in result if product_name in p['name']]
                return filtered
            else:
                # 返回所有商品
                return result
                
        except Exception as e:
            print(f"❌ 获取库存失败: {e}")
            return None
    
    async def batch_update_stock(self, product_stock_dict, verify=True):
        """批量更新库存"""
        print(f"🔄 开始批量修改库存")
        print("="*60)
        
        results = {}
        
        for product_name, new_stock in product_stock_dict.items():
            print(f"\n📦 处理商品: {product_name} -> {new_stock}")
            
            success = await self.update_stock(product_name, new_stock, verify)
            results[product_name] = {
                'success': success,
                'target_stock': new_stock
            }
            
            # 等待一下再处理下一个
            if success:
                await asyncio.sleep(3)
        
        # 生成报告
        print("\n" + "="*60)
        print("📋 批量修改报告")
        print("="*60)
        
        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)
        
        print(f"总计: {total_count} 个商品")
        print(f"成功: {success_count} 个")
        print(f"失败: {total_count - success_count} 个")
        
        for product_name, result in results.items():
            status = "✅ 成功" if result['success'] else "❌ 失败"
            print(f"  {product_name}: {status} (目标库存: {result['target_stock']})")
        
        return results