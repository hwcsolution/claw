#!/bin/bash
# 银豹系统环境变量设置脚本

echo "=========================================="
echo "银豹系统环境变量设置"
echo "=========================================="

# 检查是否已设置环境变量
if [ -n "$POSPAL_USERNAME" ] && [ -n "$POSPAL_PASSWORD" ]; then
    echo "✅ 环境变量已设置："
    echo "   POSPAL_USERNAME: $POSPAL_USERNAME"
    echo "   POSPAL_PASSWORD: (已隐藏)"
    echo ""
    echo "💡 如果要重新设置，请先取消设置："
    echo "   unset POSPAL_USERNAME POSPAL_PASSWORD"
    exit 0
fi

# 获取用户名和密码
echo "请输入银豹系统登录信息："
read -p "用户名: " username
read -sp "密码: " password
echo

# 验证输入
if [ -z "$username" ] || [ -z "$password" ]; then
    echo "❌ 用户名和密码不能为空"
    exit 1
fi

# 写入配置文件
CONFIG_FILE="$HOME/.pospal_env"
echo "POSPAL_USERNAME=\"$username\"" > "$CONFIG_FILE"
echo "POSPAL_PASSWORD=\"$password\"" >> "$CONFIG_FILE"
chmod 600 "$CONFIG_FILE"

echo ""
echo "✅ 凭据已保存到 $CONFIG_FILE"
echo ""
echo "使用方法："
echo "1. 加载环境变量："
echo "   source ~/.pospal_env"
echo ""
echo "2. 测试连接："
echo "   python3 test_connection.py"
echo ""
echo "3. 验证环境变量："
echo "   python3 env_utils.py"
echo ""
echo "=========================================="
echo "设置完成！"
echo "=========================================="