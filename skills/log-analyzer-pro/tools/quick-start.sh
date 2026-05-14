#!/bin/bash

# log-analyzer-pro 快速启动脚本
# 帮助用户快速开始使用log-analyzer-pro

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_step() {
    echo -e "${CYAN}▶ $*${NC}"
}

# 显示欢迎信息
show_welcome() {
    cat << EOF

╔══════════════════════════════════════════════════════════╗
║             log-analyzer-pro 快速启动向导               ║
║        专业日志分析专家 - 统一SSH和ELK日志分析          ║
╚══════════════════════════════════════════════════════════╝

欢迎使用 log-analyzer-pro！

本向导将帮助您：
1. 初始化配置文件
2. 测试基本功能
3. 设置定时监控任务
4. 开始使用分析功能

请按照提示完成设置。

EOF
}

# 检查依赖
check_dependencies() {
    log_step "1. 检查系统依赖"
    
    local missing_deps=()
    
    # 检查基本命令
    for cmd in curl jq ssh python3; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        log_success "所有依赖已安装"
        return 0
    else
        log_warning "缺少依赖: ${missing_deps[*]}"
        
        echo ""
        echo "请选择安装方式："
        echo "1) 自动安装（Ubuntu/Debian）"
        echo "2) 手动安装"
        echo "3) 跳过（不推荐）"
        echo ""
        read -p "请选择 (1/2/3): " choice
        
        case "$choice" in
            1)
                log_info "正在安装依赖..."
                sudo apt-get update
                sudo apt-get install -y curl jq openssh-client python3 python3-pip
                log_success "依赖安装完成"
                ;;
            2)
                echo ""
                echo "请手动安装以下依赖："
                echo "  Ubuntu/Debian: sudo apt-get install curl jq openssh-client python3 python3-pip"
                echo "  CentOS/RHEL: sudo yum install curl jq openssh-clients python3 python3-pip"
                echo "  macOS: brew install curl jq openssh python3"
                echo ""
                read -p "按回车键继续（安装完成后）..." -n 1
                ;;
            3)
                log_warning "跳过依赖检查，某些功能可能无法使用"
                ;;
            *)
                log_error "无效选择"
                return 1
                ;;
        esac
    fi
    
    return 0
}

# 初始化配置
init_config() {
    log_step "2. 初始化配置文件"
    
    if [ -f "$PROJECT_DIR/config/main-config.yaml" ]; then
        log_info "配置文件已存在"
        read -p "是否重新初始化配置？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "跳过配置初始化"
            return 0
        fi
    fi
    
    # 创建配置目录
    mkdir -p "$PROJECT_DIR/config"
    
    # 初始化配置
    if "$PROJECT_DIR/log-analyzer-pro" config init; then
        log_success "配置初始化完成"
    else
        log_error "配置初始化失败"
        return 1
    fi
    
    echo ""
    log_info "接下来需要编辑配置文件："
    echo "  1. SSH配置: $PROJECT_DIR/config/ssh-config.yaml"
    echo "  2. ELK配置: $PROJECT_DIR/config/elk-config.yaml"
    echo "  3. 告警配置: $PROJECT_DIR/config/alert-config.yaml"
    echo ""
    
    read -p "是否现在编辑SSH配置？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "$PROJECT_DIR/log-analyzer-pro" config edit ssh
    fi
    
    read -p "是否现在编辑ELK配置？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "$PROJECT_DIR/log-analyzer-pro" config edit elk
    fi
    
    return 0
}

# 测试基本功能
test_basic_functions() {
    log_step "3. 测试基本功能"
    
    echo ""
    echo "请选择要测试的功能："
    echo "1) 测试配置验证"
    echo "2) 测试SSH连接"
    echo "3) 测试ELK连接"
    echo "4) 测试知识库"
    echo "5) 跳过测试"
    echo ""
    read -p "请选择 (1/2/3/4/5): " choice
    
    case "$choice" in
        1)
            log_info "测试配置验证..."
            if "$PROJECT_DIR/log-analyzer-pro" config validate; then
                log_success "配置验证通过"
            else
                log_error "配置验证失败"
            fi
            ;;
        2)
            log_info "测试SSH连接..."
            read -p "请输入要测试的服务器名称（参考ssh-config.yaml）: " server_name
            if [ -n "$server_name" ]; then
                "$PROJECT_DIR/log-analyzer-pro" ssh test --server "$server_name"
            else
                log_warning "未输入服务器名称，跳过SSH测试"
            fi
            ;;
        3)
            log_info "测试ELK连接..."
            "$PROJECT_DIR/log-analyzer-pro" elk health
            ;;
        4)
            log_info "测试知识库..."
            "$PROJECT_DIR/log-analyzer-pro" knowledge list
            ;;
        5)
            log_info "跳过功能测试"
            ;;
        *)
            log_error "无效选择"
            ;;
    esac
    
    return 0
}

# 设置定时任务
setup_cron_jobs() {
    log_step "4. 设置定时监控任务"
    
    echo ""
    echo "请选择定时任务模式："
    echo "1) 基础监控（每5分钟健康检查，每15分钟错误检查，每小时报告）"
    echo "2) 完整监控（包括性能分析和知识库更新）"
    echo "3) 自定义定时任务"
    echo "4) 跳过定时任务设置"
    echo ""
    read -p "请选择 (1/2/3/4): " choice
    
    case "$choice" in
        1)
            log_info "设置基础监控..."
            "$PROJECT_DIR/tools/setup-cron.sh" --mode basic
            ;;
        2)
            log_info "设置完整监控..."
            "$PROJECT_DIR/tools/setup-cron.sh" --mode full
            ;;
        3)
            log_info "设置自定义定时任务..."
            "$PROJECT_DIR/tools/setup-cron.sh" --mode custom
            ;;
        4)
            log_info "跳过定时任务设置"
            ;;
        *)
            log_error "无效选择"
            ;;
    esac
    
    return 0
}

# 显示使用示例
show_examples() {
    log_step "5. 使用示例"
    
    cat << EOF

📖 基本使用示例：

1. SSH日志分析
   # 分析远程服务器系统日志
   $PROJECT_DIR/log-analyzer-pro ssh analyze --server server01 --log /var/log/syslog --time "1 hour ago"

   # 实时监控Nginx错误日志
   $PROJECT_DIR/log-analyzer-pro ssh monitor --server server01 --log /var/log/nginx/error.log --follow

2. ELK日志分析
   # 检查ELK集群健康
   $PROJECT_DIR/log-analyzer-pro elk health

   # 搜索错误日志
   $PROJECT_DIR/log-analyzer-pro elk errors --time 2h --level ERROR

   # 性能分析
   $PROJECT_DIR/log-analyzer-pro elk performance --time 24h

3. 统一分析
   # 智能分析（自动选择数据源）
   $PROJECT_DIR/log-analyzer-pro analyze --target server01:syslog --time 1h

   # 混合分析
   $PROJECT_DIR/log-analyzer-pro analyze --ssh-host server01 --elk-index logstash-* --time 30m

4. 知识库管理
   # 列出所有解决方案
   $PROJECT_DIR/log-analyzer-pro knowledge list

   # 搜索解决方案
   $PROJECT_DIR/log-analyzer-pro knowledge search "磁盘空间不足"

   # 添加新解决方案
   $PROJECT_DIR/log-analyzer-pro knowledge add --title "新问题" --category system

5. 报告生成
   # 生成日报
   $PROJECT_DIR/log-analyzer-pro report daily --time 24h --output daily-report.md

   # 生成HTML报告
   $PROJECT_DIR/log-analyzer-pro report comprehensive --time 7d --output weekly-report.html --format html

6. 告警管理
   # 测试告警配置
   $PROJECT_DIR/log-analyzer-pro alert test

   # 查看告警状态
   $PROJECT_DIR/log-analyzer-pro alert status

📚 更多帮助：
   # 查看完整帮助
   $PROJECT_DIR/log-analyzer-pro --help

   # 查看特定命令帮助
   $PROJECT_DIR/log-analyzer-pro ssh --help
   $PROJECT_DIR/log-analyzer-pro elk --help
   $PROJECT_DIR/log-analyzer-pro analyze --help

🚀 开始使用：
   现在您可以开始使用log-analyzer-pro进行日志分析了！

   建议从以下步骤开始：
   1. 测试SSH连接：$PROJECT_DIR/log-analyzer-pro ssh test --server <服务器名>
   2. 测试ELK连接：$PROJECT_DIR/log-analyzer-pro elk health
   3. 运行首次分析：$PROJECT_DIR/log-analyzer-pro analyze --target <目标> --time 1h

💡 提示：
   - 使用 --verbose 参数查看详细输出
   - 使用 --quiet 参数减少输出
   - 使用 --output 参数保存结果到文件
   - 使用 --format 参数指定输出格式（text/json/html/markdown）

EOF
}

# 创建示例配置文件
create_example_configs() {
    log_step "创建示例配置文件..."
    
    # 创建SSH配置示例
    cat > "$PROJECT_DIR/examples/ssh-config-example.yaml" << 'EOF'
# SSH服务器配置示例
servers:
  # 生产Web服务器
  production-web:
    host: "192.168.1.100"
    port: 22
    username: "admin"
    authentication:
      type: "key"  # key, password, agent
      key_path: "~/.ssh/id_rsa"
      password: ""  # 留空使用key认证
    logs:
      - path: "/var/log/syslog"
        type: "system"
        parser: "syslog"
      - path: "/var/log/nginx/access.log"
        type: "nginx_access"
        parser: "nginx"
      - path: "/var/log/nginx/error.log"
        type: "nginx_error"
        parser: "nginx"
      - path: "/var/log/auth.log"
        type: "auth"
        parser: "syslog"
    commands:
      health: "systemctl status nginx"
      disk: "df -h"
      memory: "free -m"
      cpu: "top -bn1 | grep 'Cpu(s)'"
  
  # 生产数据库服务器
  production-db:
    host: "192.168.1.101"
    port: 22
    username: "root"
    authentication:
      type: "password"
      password: "your_password_here"  # 实际使用时请使用加密密码
    logs:
      - path: "/var/log/mysql/error.log"
        type: "mysql_error"
        parser: "mysql"
      - path: "/var/log/syslog"
        type: "system"
        parser: "syslog"
    commands:
      health: "systemctl status mysql"
      connections: "mysqladmin status"
      processes: "mysqladmin processlist"
  
  # 测试服务器
  test-server:
    host: "test.example.com"
    port: 22
    username: "ubuntu"
    authentication:
      type: "key"
      key_path: "~/.ssh/test_key"
      password: ""
    logs:
      - path: "/var/log/syslog"
        type: "system"
        parser: "syslog"
      - path: "/var/log/docker.log"
        type: "docker"
        parser: "json"
    commands:
      health: "docker ps"
      disk: "df -h"
      memory: "free -m"

# 全局SSH配置
global:
  connection_timeout: 30
  command_timeout: 300
  retry_attempts: 3
  retry_delay: 5
EOF
    
    # 创建ELK配置示例
    cat > "$PROJECT_DIR/examples/elk-config-example.yaml" << 'EOF'
# ELK集群配置示例
elasticsearch:
  # 集群节点配置
  hosts:
    - "http://elk-prod-01:9200"
    - "http://elk-prod-02:9200"
    - "http://elk-prod-03:9200"
  
  # 认证配置
  authentication:
    enabled: true
    type: "basic"  # basic, api_key, ssl
    username: "elastic"
    password: "your_password_here"  # 实际使用时请使用加密密码
  
  # SSL配置（如果启用）
  ssl:
    enabled: false
    ca_cert: "/path/to/ca.crt"
    client_cert: "/path/to/client.crt"
    client_key: "/path/to/client.key"
  
  # 连接配置
  connection:
    timeout: 30
    max_retries: 3
    retry_on_timeout: true
    sniff_on_start: true
    sniff_on_connection_fail: true
  
  # 索引配置
  indices:
    logs: "logstash-*"
    metrics: "metricbeat-*"
    application: "app-*"
    system: "system-*"
  
  # 查询配置
  query:
    default_size: 1000
    max_size: 10000
    scroll_time: "5m"
  
  # 监控配置
  monitoring:
    enabled: true
    cluster_health_interval: 30
    node_stats_interval: 60

# Kibana配置
kibana:
  host: "http://kibana-prod:5601"
  authentication:
    enabled: true
    username: "kibana_user"
    password: "your_password_here"  # 实际使用时请使用加密密码
  
  # 仪表板配置
  dashboards:
    - id: "nginx-access"
      name: "Nginx Access Logs"
    - id: "system-metrics"
      name: "System Metrics"
    - id: "application-errors"
      name: "Application Errors"

# Logstash配置
logstash:
  hosts:
    - "logstash-prod:5044"
    - "logstash-prod:5000"
  
  monitoring:
    enabled: true
    port: 9600
  
  # 管道配置
  pipelines:
    - name: "nginx-access"
      description: "Nginx access logs pipeline"
    - name: "system-logs"
      description: "System logs pipeline"
    - name: "application-logs"
      description: "Application logs pipeline"

# 数据保留策略
retention:
  logs: 30  # 日志保留30天
  metrics: 90  # 指标保留90天
  reports: 365  # 报告保留365天

# 性能优化配置
performance:
  # 查询优化
  query_optimization:
    enabled: true
    max_concurrent_searches: 5
    max_result_window: 10000
  
  # 缓存配置
  cache:
    enabled: true
    ttl: 300  # 5分钟
    max_size: 1000
  
  # 批量处理
  bulk:
    enabled: true
    size: 1000
    interval: 5
EOF
    
    log_success "示例配置文件已创建: $PROJECT_DIR/examples/"
}

# 显示完成信息
show_completion() {
    cat << EOF

🎉 设置完成！

log-analyzer-pro 已成功配置并准备就绪。

📁 重要目录：
   配置文件：$PROJECT_DIR/config/
   知识库：$PROJECT_DIR/../knowledge-base/
   日志文件：$PROJECT_DIR/logs/
   报告文件：$PROJECT_DIR/reports/
   示例文件：$PROJECT_DIR/examples/

🔧 管理命令：
   查看配置：$PROJECT_DIR/log-analyzer-pro config show
   编辑配置：$PROJECT_DIR/log-analyzer-pro config edit <类型>
   验证配置：$PROJECT_DIR/log-analyzer-pro config validate
   管理定时任务：$PROJECT_DIR/tools/setup-cron.sh

📊 监控状态：
   查看定时任务：$PROJECT_DIR/tools/setup-cron.sh --status
   测试功能：$PROJECT_DIR/log-analyzer-pro --help

🚨 下一步：
   1. 编辑配置文件以适配您的环境
   2. 测试SSH和ELK连接
   3. 设置定时监控任务
   4. 开始分析日志！

💡 提示：
   - 定期检查日志文件：$PROJECT_DIR/logs/
   - 查看生成的报告：$PROJECT_DIR/reports/
   - 使用知识库搜索解决方案：$PROJECT_DIR/log-analyzer-pro knowledge search <关键词>

如有问题，请参考文档：$PROJECT_DIR/SKILL.md

祝您使用愉快！
EOF
}

# 主函数
main() {
    # 显示欢迎信息
    show_welcome
    
    # 创建示例目录
    mkdir -p "$PROJECT_DIR/examples"
    
    # 检查依赖
    if ! check_dependencies; then
        log_error "依赖检查失败"
        exit 1
    fi
    
    # 初始化配置
    if ! init_config; then
        log_error "配置初始化失败"
        exit 1
    fi
    
    # 创建示例配置文件
    create_example_configs
    
    # 测试基本功能
    test_basic_functions
    
    # 设置定时任务
    setup_cron_jobs
    
    # 显示使用示例
    show_examples
    
    # 显示完成信息
    show_completion
}

# 运行主函数
main "$@"