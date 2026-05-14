#!/bin/bash

# 定时任务设置脚本
# 用于设置log-analyzer-pro的定时监控任务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CRON_FILE="/tmp/log-analyzer-pro-cron-$$"

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

# 显示帮助
show_help() {
    cat << EOF
log-analyzer-pro 定时任务设置脚本

用法: $0 [选项]

选项:
  --mode <mode>        设置模式: basic, full, custom (默认: basic)
  --list               列出当前定时任务
  --remove             移除所有定时任务
  --status             查看定时任务状态
  --test               测试定时任务配置（不实际安装）
  --help               显示帮助信息

模式说明:
  basic    基础监控（每5分钟健康检查，每15分钟错误检查，每小时报告）
  full     完整监控（包括性能分析和知识库更新）
  custom   自定义定时任务

示例:
  $0 --mode basic          # 设置基础监控
  $0 --mode full           # 设置完整监控
  $0 --list                # 列出当前定时任务
  $0 --remove              # 移除所有定时任务
  $0 --status              # 查看状态
  $0 --test                # 测试配置

定时任务说明:
  基础监控包含:
    - 每5分钟检查集群健康
    - 每15分钟检查错误日志
    - 每小时生成分析报告
    - 每天8点生成日报

  完整监控包含:
    - 基础监控所有任务
    - 每30分钟性能分析
    - 每6小时知识库更新
    - 每周一生成周报
EOF
}

# 检查cron服务状态
check_cron_status() {
    if systemctl is-active cron >/dev/null 2>&1 || systemctl is-active crond >/dev/null 2>&1; then
        log_info "cron服务正在运行"
        return 0
    else
        log_warning "cron服务未运行"
        return 1
    fi
}

# 列出当前定时任务
list_cron_jobs() {
    log_info "当前用户的定时任务:"
    echo ""
    crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" || echo "暂无定时任务"
    echo ""
    
    log_info "系统定时任务 (/etc/cron.d/):"
    echo ""
    if [ -d /etc/cron.d ]; then
        find /etc/cron.d -name "*log-analyzer*" -type f 2>/dev/null | while read -r file; do
            echo "文件: $file"
            cat "$file" 2>/dev/null | grep -v "^#" | grep -v "^$" || echo "  无内容"
            echo ""
        done
    else
        echo "目录 /etc/cron.d 不存在"
    fi
}

# 移除定时任务
remove_cron_jobs() {
    log_info "正在移除log-analyzer-pro定时任务..."
    
    # 移除用户cron
    if crontab -l 2>/dev/null | grep -q "log-analyzer-pro"; then
        crontab -l 2>/dev/null | grep -v "log-analyzer-pro" | crontab -
        log_success "已从用户cron移除log-analyzer-pro任务"
    else
        log_info "用户cron中未找到log-analyzer-pro任务"
    fi
    
    # 移除系统cron
    if [ -d /etc/cron.d ]; then
        find /etc/cron.d -name "*log-analyzer*" -type f 2>/dev/null | while read -r file; do
            log_info "移除系统cron文件: $file"
            sudo rm -f "$file"
        done
    fi
    
    log_success "所有log-analyzer-pro定时任务已移除"
}

# 测试定时任务配置
test_cron_config() {
    log_info "测试定时任务配置..."
    
    # 检查脚本是否存在
    if [ ! -f "$PROJECT_DIR/log-analyzer-pro" ]; then
        log_error "主脚本不存在: $PROJECT_DIR/log-analyzer-pro"
        return 1
    fi
    
    # 检查脚本可执行权限
    if [ ! -x "$PROJECT_DIR/log-analyzer-pro" ]; then
        log_warning "主脚本不可执行，尝试添加执行权限"
        chmod +x "$PROJECT_DIR/log-analyzer-pro"
    fi
    
    # 检查日志目录
    LOGS_DIR="$PROJECT_DIR/logs"
    if [ ! -d "$LOGS_DIR" ]; then
        log_info "创建日志目录: $LOGS_DIR"
        mkdir -p "$LOGS_DIR"
    fi
    
    # 检查报告目录
    REPORTS_DIR="$PROJECT_DIR/reports"
    if [ ! -d "$REPORTS_DIR" ]; then
        log_info "创建报告目录: $REPORTS_DIR"
        mkdir -p "$REPORTS_DIR"
    fi
    
    # 测试基本命令
    log_info "测试基本命令..."
    if "$PROJECT_DIR/log-analyzer-pro" --version >/dev/null 2>&1; then
        log_success "主脚本测试通过"
    else
        log_error "主脚本测试失败"
        return 1
    fi
    
    log_success "定时任务配置测试通过"
    return 0
}

# 生成基础监控定时任务
generate_basic_cron() {
    cat > "$CRON_FILE" << EOF
# ============================================
# log-analyzer-pro 基础监控定时任务
# 生成时间: $(date)
# ============================================

# 每5分钟检查集群健康
*/5 * * * * cd $PROJECT_DIR && ./log-analyzer-pro elk health --quiet >> logs/health-\$(date +\%Y\%m\%d).log 2>&1

# 每15分钟检查错误日志
*/15 * * * * cd $PROJECT_DIR && ./log-analyzer-pro elk errors --time 15m --quiet >> logs/errors-\$(date +\%Y\%m\%d).log 2>&1

# 每小时运行完整分析
0 * * * * cd $PROJECT_DIR && ./log-analyzer-pro analyze --time 1h --output reports/hourly-\$(date +\%Y\%m\%d_\%H).md >> logs/analyze-\$(date +\%Y\%m\%d).log 2>&1

# 每天8点生成日报
0 8 * * * cd $PROJECT_DIR && ./log-analyzer-pro report daily --time 24h --output reports/daily-\$(date +\%Y\%m\%d).md >> logs/report-\$(date +\%Y\%m\%d).log 2>&1

# 每周一9点生成周报
0 9 * * 1 cd $PROJECT_DIR && ./log-analyzer-pro report weekly --time 7d --output reports/weekly-\$(date +\%Y\%m\%d).md >> logs/report-\$(date +\%Y\%m\%d).log 2>&1
EOF
}

# 生成完整监控定时任务
generate_full_cron() {
    cat > "$CRON_FILE" << EOF
# ============================================
# log-analyzer-pro 完整监控定时任务
# 生成时间: $(date)
# ============================================

# 每5分钟检查集群健康
*/5 * * * * cd $PROJECT_DIR && ./log-analyzer-pro elk health --quiet >> logs/health-\$(date +\%Y\%m\%d).log 2>&1

# 每10分钟检查SSH服务器健康
*/10 * * * * cd $PROJECT_DIR && ./log-analyzer-pro ssh analyze --server all --quiet >> logs/ssh-health-\$(date +\%Y\%m\%d).log 2>&1

# 每15分钟检查错误日志
*/15 * * * * cd $PROJECT_DIR && ./log-analyzer-pro elk errors --time 15m --quiet >> logs/errors-\$(date +\%Y\%m\%d).log 2>&1

# 每30分钟性能分析
*/30 * * * * cd $PROJECT_DIR && ./log-analyzer-pro elk performance --time 30m --quiet >> logs/performance-\$(date +\%Y\%m\%d).log 2>&1

# 每小时运行完整分析
0 * * * * cd $PROJECT_DIR && ./log-analyzer-pro analyze --time 1h --output reports/hourly-\$(date +\%Y\%m\%d_\%H).md >> logs/analyze-\$(date +\%Y\%m\%d).log 2>&1

# 每6小时更新知识库
0 */6 * * * cd $PROJECT_DIR && ./log-analyzer-pro knowledge update --auto >> logs/knowledge-\$(date +\%Y\%m\%d).log 2>&1

# 每天8点生成日报
0 8 * * * cd $PROJECT_DIR && ./log-analyzer-pro report daily --time 24h --output reports/daily-\$(date +\%Y\%m\%d).md >> logs/report-\$(date +\%Y\%m\%d).log 2>&1

# 每周一9点生成周报
0 9 * * 1 cd $PROJECT_DIR && ./log-analyzer-pro report weekly --time 7d --output reports/weekly-\$(date +\%Y\%m\%d).md >> logs/report-\$(date +\%Y\%m\%d).log 2>&1

# 每月1号10点生成月报
0 10 1 * * cd $PROJECT_DIR && ./log-analyzer-pro report monthly --time 30d --output reports/monthly-\$(date +\%Y\%m).md >> logs/report-\$(date +\%Y\%m).log 2>&1

# 每天23点清理旧日志（保留7天）
0 23 * * * find $PROJECT_DIR/logs -name "*.log" -mtime +7 -delete
0 23 * * * find $PROJECT_DIR/reports -name "*.md" -mtime +30 -delete
EOF
}

# 生成自定义定时任务
generate_custom_cron() {
    log_info "生成自定义定时任务"
    
    echo "# ============================================" > "$CRON_FILE"
    echo "# log-analyzer-pro 自定义定时任务" >> "$CRON_FILE"
    echo "# 生成时间: $(date)" >> "$CRON_FILE"
    echo "# ============================================" >> "$CRON_FILE"
    echo "" >> "$CRON_FILE"
    
    echo "请编辑以下定时任务配置（按Ctrl+D保存）:"
    echo ""
    echo "可用变量:"
    echo "  \$PROJECT_DIR - 项目目录: $PROJECT_DIR"
    echo "  \$(date +\%Y\%m\%d) - 当前日期: $(date +%Y%m%d)"
    echo "  \$(date +\%Y\%m\%d_\%H) - 当前日期和时间: $(date +%Y%m%d_%H)"
    echo ""
    echo "示例:"
    echo "  # 每5分钟检查健康"
    echo "  */5 * * * * cd \$PROJECT_DIR && ./log-analyzer-pro elk health --quiet >> logs/health-\$(date +\%Y\%m\%d).log 2>&1"
    echo ""
    echo "请输入定时任务配置:"
    
    # 读取用户输入
    cat >> "$CRON_FILE"
}

# 安装定时任务
install_cron_jobs() {
    local mode="$1"
    
    log_info "正在安装 $mode 模式的定时任务..."
    
    # 测试配置
    if ! test_cron_config; then
        log_error "配置测试失败，请先修复问题"
        return 1
    fi
    
    # 生成定时任务
    case "$mode" in
        "basic")
            generate_basic_cron
            ;;
        "full")
            generate_full_cron
            ;;
        "custom")
            generate_custom_cron
            ;;
        *)
            log_error "未知的模式: $mode"
            return 1
            ;;
    esac
    
    # 显示生成的定时任务
    log_info "生成的定时任务:"
    echo ""
    cat "$CRON_FILE"
    echo ""
    
    # 确认安装
    read -p "是否安装上述定时任务？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "已取消安装"
        rm -f "$CRON_FILE"
        return 0
    fi
    
    # 安装定时任务
    if crontab -l 2>/dev/null > /tmp/current_cron; then
        # 移除旧的log-analyzer-pro任务
        grep -v "log-analyzer-pro" /tmp/current_cron > /tmp/new_cron 2>/dev/null || true
        cat "$CRON_FILE" >> /tmp/new_cron
        crontab /tmp/new_cron
    else
        crontab "$CRON_FILE"
    fi
    
    # 清理临时文件
    rm -f "$CRON_FILE" /tmp/current_cron /tmp/new_cron 2>/dev/null || true
    
    log_success "定时任务安装完成"
    log_info "使用 'crontab -l' 查看当前定时任务"
    log_info "使用 '$0 --status' 查看定时任务状态"
    
    return 0
}

# 查看定时任务状态
show_cron_status() {
    log_info "定时任务状态检查"
    echo ""
    
    # 检查cron服务
    check_cron_status
    echo ""
    
    # 列出定时任务
    list_cron_jobs
    echo ""
    
    # 检查最近执行情况
    log_info "最近执行情况:"
    
    # 检查日志文件
    LOGS_DIR="$PROJECT_DIR/logs"
    if [ -d "$LOGS_DIR" ]; then
        latest_log=$(find "$LOGS_DIR" -name "*.log" -type f -exec ls -lt {} + | head -5)
        if [ -n "$latest_log" ]; then
            echo "最近日志文件:"
            echo "$latest_log" | while read -r line; do
                echo "  $line"
            done
        else
            echo "  未找到日志文件"
        fi
    else
        echo "  日志目录不存在: $LOGS_DIR"
    fi
    
    echo ""
    
    # 检查报告文件
    REPORTS_DIR="$PROJECT_DIR/reports"
    if [ -d "$REPORTS_DIR" ]; then
        latest_report=$(find "$REPORTS_DIR" -name "*.md" -type f -exec ls -lt {} + | head -5)
        if [ -n "$latest_report" ]; then
            echo "最近报告文件:"
            echo "$latest_report" | while read -r line; do
                echo "  $line"
            done
        else
            echo "  未找到报告文件"
        fi
    else
        echo "  报告目录不存在: $REPORTS_DIR"
    fi
    
    echo ""
    
    # 检查脚本状态
    log_info "脚本状态:"
    if [ -f "$PROJECT_DIR/log-analyzer-pro" ]; then
        echo "  主脚本: 存在 ($PROJECT_DIR/log-analyzer-pro)"
        if [ -x "$PROJECT_DIR/log-analyzer-pro" ]; then
            echo "  权限: 可执行"
        else
            echo "  权限: 不可执行（需要 chmod +x）"
        fi
    else
        echo "  主脚本: 不存在"
    fi
    
    if [ -d "$PROJECT_DIR/config" ]; then
        config_count=$(find "$PROJECT_DIR/config" -name "*.yaml" -type f | wc -l)
        echo "  配置文件: $config_count 个"
    else
        echo "  配置目录: 不存在"
    fi
}

# 主函数
main() {
    local mode="basic"
    local action="install"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --mode)
                mode="$2"
                shift 2
                ;;
            --list)
                action="list"
                shift
                ;;
            --remove)
                action="remove"
                shift
                ;;
            --status)
                action="status"
                shift
                ;;
            --test)
                action="test"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 执行动作
    case "$action" in
        "install")
            if [[ ! "$mode" =~ ^(basic|full|custom)$ ]]; then
                log_error "无效的模式: $mode，可选值: basic, full, custom"
                exit 1
            fi
            install_cron_jobs "$mode"
            ;;
        "list")
            list_cron_jobs
            ;;
        "remove")
            remove_cron_jobs
            ;;
        "status")
            show_cron_status
            ;;
        "test")
            test_cron_config
            ;;
    esac
}

# 运行主函数
main "$@"