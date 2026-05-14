#!/bin/bash
# 银豹系统环境变量使用示例

echo "=========================================="
echo "银豹系统环境变量使用示例"
echo "=========================================="

# 进入脚本目录
cd "$(dirname "$0")/../scripts" || exit 1

echo ""
echo "1. 📝 设置环境变量"
echo "------------------------------------------"

# 方法1: 使用设置脚本（推荐）
echo "方法1: 使用设置脚本"
echo "运行: ./setup_env.sh"
echo ""
echo "方法2: 手动设置环境变量"
echo "export POSPAL_USERNAME='你的用户名'"
echo "export POSPAL_PASSWORD='你的密码'"
echo ""
echo "方法3: 使用配置文件"
echo "echo 'POSPAL_USERNAME=\"你的用户名\"' > ~/.pospal_env"
echo "echo 'POSPAL_PASSWORD=\"你的密码\"' >> ~/.pospal_env"
echo "chmod 600 ~/.pospal_env"
echo "source ~/.pospal_env"

echo ""
echo "2. ✅ 验证环境变量"
echo "------------------------------------------"
echo "运行: python3 load_env.py"
echo ""
echo "或者手动检查:"
echo "echo \$POSPAL_USERNAME"
echo "echo \$POSPAL_PASSWORD"

echo ""
echo "3. 🚀 使用技能"
echo "------------------------------------------"

echo "测试连接:"
echo "python3 test_connection.py"
echo ""
echo "检查库存:"
echo "python3 check_inventory.py"
echo ""
echo "修改单个商品库存:"
echo "python3 update_single_product.py --product \"测试商品\" --stock 10"
echo ""
echo "批量修改库存:"
echo "python3 batch_update.py --json '{\"商品1\": 5, \"商品2\": 10}'"

echo ""
echo "4. 🔧 故障排除"
echo "------------------------------------------"

echo "如果遇到环境变量问题:"
echo "1. 检查环境变量是否设置:"
echo "   env | grep POSPAL"
echo ""
echo "2. 重新加载配置文件:"
echo "   source ~/.pospal_env"
echo ""
echo "3. 运行环境变量检查:"
echo "   python3 load_env.py"
echo ""
echo "4. 查看错误信息:"
echo "   python3 update_single_product.py --product \"测试\" --stock 1 2>&1"

echo ""
echo "5. 📋 完整示例"
echo "------------------------------------------"

cat << 'EOF'
#!/bin/bash
# 完整的银豹系统使用示例

# 1. 设置环境变量
export POSPAL_USERNAME="your_username"
export POSPAL_PASSWORD="your_password"

# 2. 进入脚本目录
cd /home/openclaw/.openclaw/workspace/skills/pospal-inventory-sync/scripts

# 3. 测试连接
echo "测试连接..."
python3 test_connection.py

# 4. 检查库存
echo "检查库存..."
python3 check_inventory.py

# 5. 修改库存
echo "修改库存..."
python3 update_single_product.py --product "鞋子" --stock 5

# 6. 批量修改
echo "批量修改..."
python3 batch_update.py --json '{"鞋子": 5, "衣服": 10}'
EOF

echo ""
echo "=========================================="
echo "示例结束"
echo "=========================================="