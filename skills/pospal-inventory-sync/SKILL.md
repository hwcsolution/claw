# 银豹系统库存同步技能

## 技能概述
自动化银豹POS系统（beta74.pospal.cn）的商品库存管理，包括登录、查找商品、修改库存、批量操作等功能。

## 功能特性
- ✅ 自动登录银豹系统
- ✅ 查找指定商品
- ✅ 修改商品库存
- ✅ 批量修改库存
- ✅ 验证修改结果
- ✅ 多店铺同步支持

## 使用场景
- 单商品库存调整
- 批量库存更新
- 定时库存同步
- 多店铺库存管理

## 快速开始

### 1. 单商品库存修改
```bash
# 修改鞋子库存为5
python3 /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts/update_single_product.py --product "鞋子" --stock 5

# 修改衣服库存为20
python3 /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts/update_single_product.py --product "衣服" --stock 20
```

### 2. 批量库存修改
```bash
# 批量修改库存（从CSV文件）
python3 /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts/batch_update.py --file products.csv

# 批量修改库存（JSON格式）
python3 /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts/batch_update.py --json '{"鞋子": 5, "衣服": 20}'
```

### 3. 检查库存状态
```bash
# 查看所有商品库存
python3 /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts/check_inventory.py

# 查看指定商品库存
python3 /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts/check_inventory.py --product "鞋子"
```

## 环境变量配置
为了安全，用户名和密码不再明文存储在配置文件中，而是通过环境变量传递。

### 1. 设置环境变量
有以下几种方式设置环境变量：

#### 方法1：使用设置脚本（推荐）
```bash
cd /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts
./setup_env.sh
```

#### 方法2：手动设置环境变量
```bash
# 临时设置（当前终端会话有效）
export POSPAL_USERNAME="你的用户名"
export POSPAL_PASSWORD="你的密码"

# 永久设置（添加到 ~/.bashrc）
echo 'export POSPAL_USERNAME="你的用户名"' >> ~/.bashrc
echo 'export POSPAL_PASSWORD="你的密码"' >> ~/.bashrc
source ~/.bashrc
```

#### 方法3：创建配置文件
```bash
# 创建配置文件
echo 'POSPAL_USERNAME="你的用户名"' > ~/.pospal_env
echo 'POSPAL_PASSWORD="你的密码"' >> ~/.pospal_env
chmod 600 ~/.pospal_env

# 使用前加载配置文件
source ~/.pospal_env
```

### 2. 配置文件
配置文件仅包含非敏感设置：

```json
{
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
    "headless": true,
    "timeout": 30,
    "wait_time": 3,
    "retry_attempts": 3
  }
}
```

## 脚本说明

### 核心脚本
1. **`pospal_client.py`** - 核心客户端类（从环境变量读取凭据）
2. **`update_single_product.py`** - 单商品库存修改
3. **`batch_update.py`** - 批量库存修改
4. **`check_inventory.py`** - 库存检查
5. **`test_connection.py`** - 连接测试

### 辅助脚本
1. **`env_utils.py`** - 环境变量工具模块（统一处理环境变量）
2. **`setup_env.sh`** - 环境变量设置脚本（推荐）
3. **`setup.py`** - 技能安装脚本
4. **`config.json`** - 配置文件（不含敏感信息）
5. **`example_products.csv`** - 批量操作示例文件

## 技能路径
```
/home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/
├── SKILL.md                    # 技能说明文档
├── scripts/                    # 脚本目录
│   ├── pospal_client.py           # 核心客户端（环境变量读取）
│   ├── env_utils.py               # 环境变量工具模块
│   ├── update_single_product.py   # 单商品修改
│   ├── batch_update.py            # 批量修改
│   ├── check_inventory.py         # 库存检查
│   ├── test_connection.py         # 连接测试
│   ├── setup_env.sh               # 环境变量设置脚本
│   ├── config.json                # 配置文件（不含敏感信息）
│   └── example_products.csv       # 示例文件
└── examples/                     # 使用示例
    ├── basic_usage.py            # 基本用法
    └── env_usage_example.sh      # 环境变量使用示例
```

## 依赖要求
```bash
pip install playwright
playwright install chromium
```

## 使用方法

### 第一步：设置环境变量
```bash
# 进入技能目录
cd /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts

# 运行设置脚本（推荐）
./setup_env.sh

# 或者手动设置环境变量
export POSPAL_USERNAME="你的用户名"
export POSPAL_PASSWORD="你的密码"
```

### 第二步：使用技能
```bash
# 修改鞋子库存为5
python3 update_single_product.py --product "鞋子" --stock 5

# 批量修改
python3 batch_update.py --file ../examples/products.csv

# 检查库存
python3 check_inventory.py

# 测试连接
python3 test_connection.py
```

### 第三步：验证环境变量
```bash
# 检查环境变量是否设置正确
python3 env_utils.py

# 或者手动检查
echo "用户名: $POSPAL_USERNAME"
echo "密码: ${#POSPAL_PASSWORD}个字符"  # 不显示实际密码
```

### 通过Python代码
```python
from pospal_client import PospalClient

# 创建客户端
client = PospalClient()

# 修改单个商品
client.update_stock("鞋子", 5)

# 批量修改
products = {"鞋子": 5, "衣服": 20}
client.batch_update_stock(products)

# 检查库存
inventory = client.get_inventory()
print(inventory)
```

## 故障排除

### 常见问题
1. **环境变量未设置** - 运行 `./setup_env.sh` 或手动设置环境变量
2. **登录失败** - 检查用户名密码是否正确
3. **找不到商品** - 确认商品名称是否正确
4. **保存失败** - 检查保存按钮XPath是否正确
5. **网络超时** - 增加timeout设置

### 环境变量问题
```bash
# 检查环境变量
python3 env_utils.py

# 如果为空，重新设置
./setup_env.sh

# 或者手动设置
export POSPAL_USERNAME="你的用户名"
export POSPAL_PASSWORD="你的密码"
```

### 调试模式
```bash
# 启用调试模式
python3 update_single_product.py --product "鞋子" --stock 5 --debug

# 显示详细日志
python3 update_single_product.py --product "鞋子" --stock 5 --verbose
```

## 安全说明
- ✅ **凭据安全**：用户名和密码不再明文存储在配置文件中
- ✅ **环境变量**：使用环境变量存储敏感信息，避免泄露
- ✅ **配置文件安全**：配置文件仅包含非敏感设置信息
- ✅ **权限控制**：环境变量配置文件建议设置 `chmod 600`
- 🔒 **定期更新**：建议定期更新密码
- 🔒 **安全存储**：不要在公共环境或版本控制中存储凭据

### 最佳实践
1. **使用环境变量**：避免在脚本中硬编码凭据
2. **配置文件权限**：设置配置文件权限为 `600`（仅所有者可读写）
3. **定期轮换**：定期更新密码
4. **访问控制**：限制对脚本目录的访问权限
5. **日志安全**：避免在日志中输出敏感信息

## 更新日志
- v1.1.0 (2026-05-12): 安全增强版本
  - ✅ 移除配置文件中的明文凭据
  - ✅ 使用环境变量存储用户名和密码
  - ✅ 新增环境变量设置脚本 `setup_env.sh`
  - ✅ 新增环境变量加载脚本 `load_env.py`
  - ✅ 增强安全性，避免凭据泄露
  - ✅ 更新文档和故障排除指南

- v1.0.0 (2026-04-30): 初始版本发布
  - 支持单商品库存修改
  - 支持批量库存修改
  - 支持库存检查
  - 配置文件管理

## 联系方式
如有问题，请参考脚本内的帮助文档或联系开发者。