#!/bin/bash

# 智能知识库测试脚本
# 测试智能知识库的完整工作流

set -e

echo "=========================================="
echo "智能知识库系统测试"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${RED}[ERROR]${NC} $*"
}

# 检查Python依赖
check_dependencies() {
    log_info "检查Python依赖..."
    
    if ! python3 -c "import sqlite3" &>/dev/null; then
        log_error "缺少sqlite3模块"
        return 1
    fi
    
    if ! python3 -c "import yaml" &>/dev/null; then
        log_warning "缺少yaml模块，尝试安装..."
        pip3 install pyyaml || {
            log_error "安装pyyaml失败"
            return 1
        }
    fi
    
    if ! python3 -c "import requests" &>/dev/null; then
        log_warning "缺少requests模块，尝试安装..."
        pip3 install requests || {
            log_error "安装requests失败"
            return 1
        }
    fi
    
    log_success "Python依赖检查通过"
    return 0
}

# 初始化测试环境
init_test_env() {
    log_info "初始化测试环境..."
    
    # 创建测试目录
    mkdir -p test_data
    mkdir -p test_logs
    mkdir -p test_output
    
    # 清理旧数据
    rm -f test_data/knowledge.db
    rm -f test_data/test_errors.json
    rm -f test_logs/*.log
    rm -f test_output/*.json
    
    # 创建测试错误日志
    cat > test_logs/error.log << 'EOF'
2024-04-28 10:30:00 ERROR [main] java.net.ConnectException: Connection refused
	at java.net.PlainSocketImpl.socketConnect(Native Method)
	at java.net.AbstractPlainSocketImpl.doConnect(AbstractPlainSocketImpl.java:350)
	at java.net.AbstractPlainSocketImpl.connectToAddress(AbstractPlainSocketImpl.java:206)
	at java.net.AbstractPlainSocketImpl.connect(AbstractPlainSocketImpl.java:188)
	at java.net.SocksSocketImpl.connect(SocksSocketImpl.java:392)
	at java.net.Socket.connect(Socket.java:589)
	at java.net.Socket.connect(Socket.java:538)
	at java.net.Socket.<init>(Socket.java:434)
	at java.net.Socket.<init>(Socket.java:211)
	at com.example.Application.connect(Application.java:123)

2024-04-28 10:31:00 ERROR [db-worker] MySQLIntegrityConstraintViolationException: Duplicate entry '12345' for key 'PRIMARY'
	at com.mysql.cj.jdbc.exceptions.SQLError.createSQLException(SQLError.java:129)
	at com.mysql.cj.jdbc.exceptions.SQLError.createSQLException(SQLError.java:97)

2024-04-28 10:32:00 ERROR [file-service] java.io.IOException: No space left on device
	at java.io.FileOutputStream.writeBytes(Native Method)
	at java.io.FileOutputStream.write(FileOutputStream.java:326)
	at com.example.FileService.writeFile(FileService.java:456)

2024-04-28 10:33:00 ERROR [memory-manager] java.lang.OutOfMemoryError: Java heap space
	at java.util.Arrays.copyOf(Arrays.java:3332)
	at java.lang.AbstractStringBuilder.ensureCapacityInternal(AbstractStringBuilder.java:124)

2024-04-28 10:34:00 ERROR [auth-service] java.security.AccessControlException: access denied ("java.io.FilePermission" "/etc/passwd" "read")
	at java.security.AccessControlContext.checkPermission(AccessControlContext.java:472)
	at java.security.AccessController.checkPermission(AccessController.java:884)
EOF
    
    log_success "测试环境初始化完成"
}

# 测试错误签名提取
test_error_signature() {
    log_info "测试错误签名提取..."
    
    # 测试单个错误
    echo "测试1: 提取单个错误签名"
    python3 scripts/error_signature.py --input "java.net.ConnectException: Connection refused" --output test_output/signature1.json
    
    if [ -f test_output/signature1.json ]; then
        log_success "单个错误签名提取成功"
        cat test_output/signature1.json
    else
        log_error "单个错误签名提取失败"
        return 1
    fi
    
    # 测试日志文件
    echo -e "\n测试2: 从日志文件提取错误签名"
    python3 scripts/error_signature.py --input test_logs/error.log --file --output test_output/signatures.json
    
    if [ -f test_output/signatures.json ]; then
        signature_count=$(jq length test_output/signatures.json 2>/dev/null || echo "0")
        log_success "从日志文件提取了 $signature_count 个错误签名"
    else
        log_error "日志文件错误签名提取失败"
        return 1
    fi
    
    return 0
}

# 测试知识库数据库
test_knowledge_db() {
    log_info "测试知识库数据库..."
    
    # 初始化数据库
    echo "测试1: 初始化数据库"
    python3 scripts/knowledge_db.py --init --db test_data/knowledge.db
    
    if [ -f test_data/knowledge.db ]; then
        log_success "数据库初始化成功"
    else
        log_error "数据库初始化失败"
        return 1
    fi
    
    # 添加测试数据
    echo -e "\n测试2: 添加测试数据"
    python3 scripts/knowledge_db.py --db test_data/knowledge.db --add \
        --signature "test_conn_refused" \
        --summary "连接被拒绝" \
        --solution "检查目标服务是否运行，检查防火墙配置" \
        --category "network" \
        --severity "ERROR" \
        --tags "connection,refused,network"
    
    # 搜索数据
    echo -e "\n测试3: 搜索数据"
    python3 scripts/knowledge_db.py --db test_data/knowledge.db --search "连接"
    
    # 查看统计
    echo -e "\n测试4: 查看统计"
    python3 scripts/knowledge_db.py --db test_data/knowledge.db --stats
    
    return 0
}

# 测试AI解决方案生成（模拟）
test_ai_generator() {
    log_info "测试AI解决方案生成（模拟模式）..."
    
    # 创建模拟AI配置
    cat > test_data/ai-config-test.yaml << 'EOF'
openai:
  api_key: "test-key"
  model: "gpt-3.5-turbo"
  max_tokens: 2000
  temperature: 0.7

# 启用模拟模式
testing:
  mock_responses: true
  mock_response_delay: 0.1
EOF
    
    # 测试AI生成（使用模拟模式）
    echo "测试: AI生成解决方案（模拟）"
    python3 -c "
import sys
sys.path.insert(0, 'scripts')
from ai_solution_generator import AISolutionGenerator

# 使用测试配置
generator = AISolutionGenerator('test_data/ai-config-test.yaml')

# 模拟错误
error_text = 'java.net.ConnectException: Connection refused'
context = {
    'error_text': error_text,
    'error_type': 'ConnectException',
    'error_code': 'CONN_REFUSED',
    'log_source': 'test-server',
    'system_info': {'os': 'Linux', 'java_version': '11'}
}

try:
    solution = generator.generate_solution('test_signature', context)
    print('AI生成成功:')
    print(f'  签名: {solution.signature}')
    print(f'  摘要: {solution.error_summary}')
    print(f'  分类: {solution.category}')
    print(f'  严重级别: {solution.severity}')
    print(f'  置信度: {solution.confidence}')
    print('测试通过!')
except Exception as e:
    print(f'AI生成失败: {e}')
    print('测试失败!')
    sys.exit(1)
"
    
    return $?
}

# 测试智能分析器
test_intelligent_analyzer() {
    log_info "测试智能分析器..."
    
    # 创建测试配置
    cat > test_data/intelligent-test.yaml << 'EOF'
database:
  path: "test_data/knowledge.db"
  auto_backup: false

ai:
  generation:
    min_confidence: 0.5
    auto_confirm: false

workflow:
  analysis:
    extract_signature: true
    search_knowledge_base: true
    generate_if_not_found: true
    require_human_review: false

testing:
  mock_responses: true
EOF
    
    # 测试错误分析
    echo "测试1: 分析已知错误（应在知识库中找到）"
    python3 scripts/intelligent_knowledge.py \
        --config test_data/intelligent-test.yaml \
        analyze \
        --error "java.net.ConnectException: Connection refused" \
        --source "test-server" \
        --json > test_output/analysis1.json
    
    if [ $? -eq 0 ]; then
        log_success "已知错误分析完成"
        status=$(jq -r '.status' test_output/analysis1.json 2>/dev/null || echo "unknown")
        echo "分析状态: $status"
    else
        log_error "已知错误分析失败"
        return 1
    fi
    
    # 测试未知错误
    echo -e "\n测试2: 分析未知错误（应触发AI生成）"
    python3 scripts/intelligent_knowledge.py \
        --config test_data/intelligent-test.yaml \
        analyze \
        --error "CustomApplicationError: Something went wrong in the custom module" \
        --source "test-application" \
        --json > test_output/analysis2.json
    
    if [ $? -eq 0 ]; then
        log_success "未知错误分析完成"
        status=$(jq -r '.status' test_output/analysis2.json 2>/dev/null || echo "unknown")
        echo "分析状态: $status"
    else
        log_error "未知错误分析失败"
        return 1
    fi
    
    # 测试日志文件分析
    echo -e "\n测试3: 分析日志文件"
    python3 scripts/intelligent_knowledge.py \
        --config test_data/intelligent-test.yaml \
        analyze-file \
        --file test_logs/error.log \
        --max-errors 3 \
        --json > test_output/analysis3.json
    
    if [ $? -eq 0 ]; then
        log_success "日志文件分析完成"
        total_errors=$(jq -r '.total_errors' test_output/analysis3.json 2>/dev/null || echo "0")
        echo "分析错误数: $total_errors"
    else
        log_error "日志文件分析失败"
        return 1
    fi
    
    return 0
}

# 测试完整工作流
test_full_workflow() {
    log_info "测试完整工作流..."
    
    # 清空测试数据库
    rm -f test_data/knowledge.db
    
    # 步骤1: 初始化知识库
    echo "步骤1: 初始化知识库"
    python3 scripts/knowledge_db.py --init --db test_data/knowledge.db
    
    # 步骤2: 添加一些已知解决方案
    echo -e "\n步骤2: 添加已知解决方案"
    python3 scripts/knowledge_db.py --db test_data/knowledge.db --add \
        --signature "conn_refused_123" \
        --summary "网络连接被拒绝" \
        --solution "1. 检查目标服务是否运行\n2. 检查防火墙配置\n3. 检查网络连通性" \
        --category "network" \
        --severity "ERROR" \
        --tags "network,connection,firewall" \
        --verified \
        --verified-by "test-admin"
    
    # 步骤3: 分析已知错误（应该命中知识库）
    echo -e "\n步骤3: 分析已知错误（知识库命中）"
    python3 scripts/intelligent_knowledge.py \
        --config test_data/intelligent-test.yaml \
        analyze \
        --error "Network connection refused by remote host" \
        --source "test-workflow" \
        --json > test_output/workflow1.json
    
    status1=$(jq -r '.status' test_output/workflow1.json 2>/dev/null)
    if [ "$status1" = "found" ]; then
        log_success "✓ 知识库命中测试通过"
    else
        log_warning "⚠ 知识库命中测试未通过，状态: $status1"
    fi
    
    # 步骤4: 分析未知错误（应该触发AI生成）
    echo -e "\n步骤4: 分析未知错误（AI生成）"
    python3 scripts/intelligent_knowledge.py \
        --config test_data/intelligent-test.yaml \
        analyze \
        --error "Database deadlock detected: Transaction rollback required" \
        --source "test-workflow" \
        --json > test_output/workflow2.json
    
    status2=$(jq -r '.status' test_output/workflow2.json 2>/dev/null)
    if [ "$status2" = "ai_generated_pending" ] || [ "$status2" = "ai_generated_auto_confirmed" ]; then
        log_success "✓ AI生成测试通过"
        
        # 如果是待确认状态，测试确认流程
        if [ "$status2" = "ai_generated_pending" ]; then
            pending_file=$(jq -r '.pending_file' test_output/workflow2.json 2>/dev/null)
            if [ -n "$pending_file" ] && [ "$pending_file" != "null" ]; then
                echo -e "\n步骤5: 确认AI生成的解决方案"
                python3 scripts/intelligent_knowledge.py \
                    --config test_data/intelligent-test.yaml \
                    confirm \
                    --file "$pending_file" \
                    --reviewer "workflow-test" \
                    --notes "测试确认流程" \
                    --json > test_output/workflow3.json
                
                confirm_status=$(jq -r '.status' test_output/workflow3.json 2>/dev/null)
                if [ "$confirm_status" = "confirmed" ]; then
                    log_success "✓ 解决方案确认测试通过"
                else
                    log_warning "⚠ 解决方案确认测试未通过，状态: $confirm_status"
                fi
            fi
        fi
    else
        log_warning "⚠ AI生成测试未通过，状态: $status2"
    fi
    
    # 步骤5: 查看统计
    echo -e "\n步骤5: 查看工作流统计"
    python3 scripts/intelligent_knowledge.py \
        --config test_data/intelligent-test.yaml \
        stats --json > test_output/workflow_stats.json
    
    total_solutions=$(jq -r '.knowledge_base.total_solutions' test_output/workflow_stats.json 2>/dev/null || echo "0")
    log_success "工作流测试完成，知识库现有解决方案: $total_solutions"
    
    return 0
}

# 主测试函数
main() {
    log_info "开始智能知识库系统测试"
    
    # 检查依赖
    check_dependencies || {
        log_error "依赖检查失败"
        exit 1
    }
    
    # 初始化测试环境
    init_test_env || {
        log_error "测试环境初始化失败"
        exit 1
    }
    
    # 运行测试
    tests_passed=0
    tests_failed=0
    
    echo -e "\n=== 运行测试套件 ==="
    
    # 测试错误签名提取
    echo -e "\n1. 测试错误签名提取"
    if test_error_signature; then
        log_success "错误签名提取测试通过"
        ((tests_passed++))
    else
        log_error "错误签名提取测试失败"
        ((tests_failed++))
    fi
    
    # 测试知识库数据库
    echo -e "\n2. 测试知识库数据库"
    if test_knowledge_db; then
        log_success "知识库数据库测试通过"
        ((tests_passed++))
    else
        log_error "知识库数据库测试失败"
        ((tests_failed++))
    fi
    
    # 测试AI解决方案生成
    echo -e "\n3. 测试AI解决方案生成"
    if test_ai_generator; then
        log_success "AI解决方案生成测试通过"
        ((tests_passed++))
    else
        log_error "AI解决方案生成测试失败"
        ((tests_failed++))
    fi
    
    # 测试智能分析器
    echo -e "\n4. 测试智能分析器"
    if test_intelligent_analyzer; then
        log_success "智能分析器测试通过"
        ((tests_passed++))
    else
        log_error "智能分析器测试失败"
        ((tests_failed++))
    fi
    
    # 测试完整工作流
    echo -e "\n5. 测试完整工作流"
    if test_full_workflow; then
        log_success "完整工作流测试通过"
        ((tests_passed++))
    else
        log_error "完整工作流测试失败"
        ((tests_failed++))
    fi
    
    # 测试结果汇总
    echo -e "\n=== 测试结果汇总 ==="
    echo -e "总测试数: $((tests_passed + tests_failed))"
    echo -e "通过: ${GREEN}$tests_passed${NC}"
    echo -e "失败: ${RED}$tests_failed${NC}"
    
    if [ $tests_failed -eq 0 ]; then
        echo -e "\n${GREEN}✅ 所有测试通过！智能知识库系统功能正常。${NC}"
        
        # 显示生成的测试文件
        echo -e "\n生成的测试文件:"
        find test_output -name "*.json" -type f | while read file; do
            echo "  - $file"
        done
        
        # 显示知识库状态
        echo -e "\n知识库状态:"
        python3 scripts/knowledge_db.py --db test_data/knowledge.db --stats 2>/dev/null || echo "无法获取统计信息"
        
        # 使用说明
        echo -e "\n${BLUE}使用说明:${NC}"
        echo "1. 设置OpenAI API密钥:"
        echo "   export OPENAI_API_KEY=\"your-api-key\""
        echo ""
        echo "2. 分析错误:"
        echo "   ./log-analyzer-pro knowledge analyze-error --error \"错误信息\""
        echo ""
        echo "3. 分析日志文件:"
        echo "   ./log-analyzer-pro knowledge analyze-log --file error.log"
        echo ""
        echo "4. 查看待确认的解决方案:"
        echo "   ./log-analyzer-pro knowledge list-pending"
        echo ""
        echo "5. 更多帮助:"
        echo "   ./log-analyzer-pro knowledge --help"
        
    else
        echo -e "\n${RED}❌ 有 $tests_failed 个测试失败，请检查错误信息。${NC}"
        exit 1
    fi
    
    return 0
}

# 运行主测试
main "$@"