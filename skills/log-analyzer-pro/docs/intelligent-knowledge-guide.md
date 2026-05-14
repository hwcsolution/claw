# 智能知识库使用指南

## 概述

智能知识库是 `log-analyzer-pro` 的核心功能，它结合了错误签名提取、知识库匹配和AI解决方案生成，实现了您描述的完整工作流：

1. **提取错误签名** - 从错误日志中提取唯一签名
2. **知识库搜索** - 在SQLite知识库中查找匹配的解决方案
3. **AI生成** - 如果未找到，调用AI接口生成解决方案
4. **人工确认** - 需要人工审核确认AI生成的解决方案
5. **归档存储** - 确认后的解决方案存入知识库

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                   智能知识库系统                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  错误日志   │─────▶│ 签名提取器  │─────▶│  知识库查询 │ │
│  │             │      │             │      │             │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│         │                        │                  │       │
│         ▼                        ▼                  ▼       │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  原始错误   │      │  错误签名   │      │  匹配结果   │ │
│  │             │      │             │      │             │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│                                    │                        │
│                                    ▼                        │
│                            ┌─────────────┐                 │
│                            │    AI生成    │                 │
│                            │             │                 │
│                            └─────────────┘                 │
│                                    │                        │
│                                    ▼                        │
│                            ┌─────────────┐                 │
│                            │  人工审核   │                 │
│                            │             │                 │
│                            └─────────────┘                 │
│                                    │                        │
│                                    ▼                        │
│                            ┌─────────────┐                 │
│                            │  知识库存储 │                 │
│                            │             │                 │
│                            └─────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 数据库结构

智能知识库使用SQLite数据库，表结构如下：

### knowledge_base 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| signature | TEXT | 错误签名（唯一） |
| error_summary | TEXT | 错误摘要 |
| solution | TEXT | 解决方案 |
| hit_count | INTEGER | 命中次数 |
| success_count | INTEGER | 成功次数 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| category | TEXT | 分类 |
| severity | TEXT | 严重级别 |
| tags | TEXT | 标签（JSON数组） |
| verified | BOOLEAN | 是否已验证 |
| ai_generated | BOOLEAN | 是否AI生成 |
| verified_by | TEXT | 验证人 |
| verified_at | TIMESTAMP | 验证时间 |

### usage_log 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| signature | TEXT | 错误签名 |
| matched_at | TIMESTAMP | 匹配时间 |
| success | BOOLEAN | 是否成功 |
| feedback | TEXT | 用户反馈 |
| user | TEXT | 用户标识 |
| log_source | TEXT | 日志来源 |

## 快速开始

### 1. 初始化知识库

```bash
# 初始化数据库
python scripts/knowledge_db.py --init --db knowledge.db

# 添加示例数据
python scripts/knowledge_db.py --add \
  --signature "ERR001" \
  --summary "连接Redis超时" \
  --solution "检查防火墙配置，重启Redis Sentinel" \
  --category "database" \
  --severity "ERROR" \
  --tags "redis,connection,timeout"
```

### 2. 配置AI接口

编辑 `config/ai-config.yaml` 文件：

```yaml
openai:
  api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
  model: "gpt-3.5-turbo"
  max_tokens: 2000
  temperature: 0.7
```

设置环境变量：
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. 使用智能分析

#### 分析单个错误
```bash
# 使用命令行工具
python scripts/intelligent_knowledge.py analyze \
  --error "java.net.ConnectException: Connection refused" \
  --source "production-server"

# 或使用主脚本
./log-analyzer-pro knowledge analyze-error \
  --error "java.net.ConnectException: Connection refused" \
  --source "production-server"
```

#### 分析日志文件
```bash
# 分析日志文件中的错误
python scripts/intelligent_knowledge.py analyze-file \
  --file /var/log/application.log \
  --max-errors 50

# 或使用主脚本
./log-analyzer-pro knowledge analyze-log \
  --file /var/log/application.log \
  --max-errors 50
```

#### 查看待确认的解决方案
```bash
# 列出所有待确认的解决方案
python scripts/intelligent_knowledge.py list-pending

# 或使用主脚本
./log-analyzer-pro knowledge list-pending
```

#### 确认解决方案
```bash
# 确认AI生成的解决方案
python scripts/intelligent_knowledge.py confirm \
  --file work/pending_solutions/pending_abc123.json \
  --reviewer "admin" \
  --notes "解决方案正确，已验证"

# 或使用主脚本
./log-analyzer-pro knowledge confirm-solution \
  --file work/pending_solutions/pending_abc123.json \
  --reviewer "admin" \
  --notes "解决方案正确，已验证"
```

#### 拒绝解决方案
```bash
# 拒绝不正确的解决方案
python scripts/intelligent_knowledge.py reject \
  --file work/pending_solutions/pending_abc123.json \
  --reviewer "admin" \
  --reason "解决方案不完整，需要更多细节"

# 或使用主脚本
./log-analyzer-pro knowledge reject-solution \
  --file work/pending_solutions/pending_abc123.json \
  --reviewer "admin" \
  --reason "解决方案不完整，需要更多细节"
```

## 完整工作流示例

### 示例1：分析Redis连接错误

```bash
# 1. 提取错误签名
python scripts/error_signature.py --input "RedisConnectionException: Connection timeout after 9000ms"

# 输出:
# 签名: 7a8b9c0d1e2f
# 类型: RedisConnectionException
# 代码: 
# 消息: Connection timeout after 9000ms

# 2. 在知识库中搜索
python scripts/knowledge_db.py --search "RedisConnectionException"

# 3. 如果没有找到，使用AI生成解决方案
python scripts/intelligent_knowledge.py analyze \
  --error "RedisConnectionException: Connection timeout after 9000ms" \
  --source "production-redis"

# 4. 查看生成的解决方案
cat work/pending_solutions/pending_7a8b9c0d1e2f_20240428_143022.json

# 5. 确认解决方案
python scripts/intelligent_knowledge.py confirm \
  --file work/pending_solutions/pending_7a8b9c0d1e2f_20240428_143022.json \
  --reviewer "ops-team"

# 6. 验证解决方案已存入知识库
python scripts/knowledge_db.py --search "7a8b9c0d1e2f"
```

### 示例2：批量分析应用日志

```bash
# 1. 分析日志文件
python scripts/intelligent_knowledge.py analyze-file \
  --file /var/log/app/error.log \
  --max-errors 100 \
  --auto-confirm

# 2. 查看统计信息
python scripts/intelligent_knowledge.py stats

# 输出:
# 知识库统计:
#   总解决方案数: 45
#   已验证解决方案: 38
#   AI生成解决方案: 7
#   总命中次数: 123
#   总成功次数: 115
#   成功率: 93.50%

# 3. 导出知识库
python scripts/intelligent_knowledge.py export --output knowledge_backup.json

# 4. 搜索特定类型的错误
python scripts/intelligent_knowledge.py search --query "timeout" --category "network"
```

## 配置说明

### AI配置 (`config/ai-config.yaml`)

```yaml
# OpenAI配置
openai:
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-3.5-turbo"  # 或 "gpt-4"
  max_tokens: 2000
  temperature: 0.7

# 本地模型配置（可选）
local:
  enabled: false
  base_url: "http://localhost:8000/v1"
  model: "local-llm"
```

### 智能分析器配置 (`config/intelligent-analyzer.yaml`)

```yaml
# 数据库配置
database:
  path: "knowledge.db"
  auto_backup: true

# AI配置
ai:
  generation:
    min_confidence: 0.7      # 最小置信度阈值
    auto_confirm: false      # 是否自动确认AI生成的解决方案

# 工作流配置
workflow:
  analysis:
    extract_signature: true
    search_knowledge_base: true
    generate_if_not_found: true
    require_human_review: true
```

## 高级功能

### 1. 自定义错误模式

编辑 `config/intelligent-analyzer.yaml` 中的 `example_patterns` 部分：

```yaml
example_patterns:
  - pattern: "MySQLIntegrityConstraintViolationException: Duplicate entry"
    category: "database"
    severity: "ERROR"
    tags: ["mysql", "constraint", "duplicate"]
  
  - pattern: "No space left on device"
    category: "storage"
    severity: "CRITICAL"
    tags: ["disk", "space", "full"]
```

### 2. 定时分析任务

创建定时任务脚本 `cron/intelligent-analysis.sh`：

```bash
#!/bin/bash

# 设置环境变量
export OPENAI_API_KEY="your-api-key"
export LOG_DIR="/var/log/app"

# 分析错误日志
cd /path/to/log-analyzer-pro
python scripts/intelligent_knowledge.py analyze-file \
  --file "$LOG_DIR/error.log" \
  --max-errors 50 \
  --auto-confirm

# 发送通知（如果有待确认的解决方案）
PENDING_COUNT=$(python scripts/intelligent_knowledge.py list-pending --json | jq '.count')
if [ "$PENDING_COUNT" -gt 0 ]; then
  echo "有 $PENDING_COUNT 个待确认的解决方案需要审核" | mail -s "待审核解决方案" admin@example.com
fi
```

添加到crontab：
```bash
# 每天凌晨2点运行
0 2 * * * /path/to/cron/intelligent-analysis.sh
```

### 3. 集成到现有系统

在Python代码中集成：

```python
from scripts.intelligent_knowledge import IntelligentKnowledgeManager

# 初始化管理器
manager = IntelligentKnowledgeManager("config/intelligent-analyzer.yaml")

# 分析错误
result = manager.analyze_error(
    error_text="java.lang.OutOfMemoryError: Java heap space",
    source="production-java-app"
)

if result['status'] == 'found':
    # 使用知识库中的解决方案
    solution = result['solution']
    print(f"使用现有解决方案: {solution['error_summary']}")
    print(f"解决方案: {solution['solution']}")
    
elif result['status'] == 'ai_generated_pending':
    # AI生成的解决方案需要人工确认
    print(f"AI生成解决方案，需要人工确认: {result['pending_file']}")
    
elif result['status'] == 'ai_generated_auto_confirmed':
    # AI生成的解决方案已自动确认
    print(f"AI生成解决方案已自动确认: {result['solution_id']}")
```

## 故障排除

### 常见问题

1. **AI生成失败**
   - 检查API密钥是否正确
   - 检查网络连接
   - 查看日志文件 `logs/ai_generator.log`

2. **知识库查询慢**
   - 重建索引：`python scripts/knowledge_db.py --rebuild-index`
   - 优化查询：添加适当的索引

3. **签名提取不准确**
   - 检查错误模式配置
   - 调整正则表达式模式
   - 查看 `scripts/error_signature.py` 中的模式定义

4. **内存不足**
   - 调整 `config/intelligent-analyzer.yaml` 中的资源限制
   - 减少 `max_errors` 参数

### 日志查看

```bash
# 查看AI生成日志
tail -f logs/ai_generator.log

# 查看智能分析器日志
tail -f logs/intelligent_analyzer.log

# 查看数据库操作日志
tail -f logs/knowledge_db.log
```

## 性能优化

### 1. 缓存配置

```yaml
performance:
  cache:
    enabled: true
    max_size: 1000
    ttl: 3600  # 1小时
```

### 2. 并发控制

```yaml
performance:
  concurrency:
    max_workers: 4
    max_ai_requests: 2
    request_timeout: 30
```

### 3. 批量处理

```bash
# 批量分析多个日志文件
for log_file in /var/log/app/*.log; do
  python scripts/intelligent_knowledge.py analyze-file \
    --file "$log_file" \
    --max-errors 20
done
```

## 最佳实践

1. **定期备份知识库**
   ```bash
   # 每天备份
   0 3 * * * python scripts/knowledge_db.py --export --output /backup/knowledge_$(date +\%Y\%m\%d).json
   ```

2. **定期审核待确认的解决方案**
   ```bash
   # 每周一审核
   0 9 * * 1 python scripts/intelligent_knowledge.py list-pending
   ```

3. **监控知识库质量**
   ```bash
   # 检查成功率
   python scripts/intelligent_knowledge.py stats | grep "success_rate"
   
   # 检查未验证的解决方案
   python scripts/knowledge_db.py --search --verified false
   ```

4. **优化错误模式**
   - 定期审查和更新错误模式
   - 添加新的错误类型
   - 调整匹配阈值

## 扩展开发

### 添加新的错误提取器

创建自定义错误提取器：

```python
from scripts.error_signature import ErrorSignatureExtractor

class CustomErrorExtractor(ErrorSignatureExtractor):
    def _extract_error_type(self, error_text: str) -> str:
        # 自定义错误类型提取逻辑
        if "CustomError:" in error_text:
            return "CustomError"
        return super()._extract_error_type(error_text)
```

### 集成其他AI模型

修改 `scripts/ai_solution_generator.py`：

```python
class CustomAIGenerator(AISolutionGenerator):
    def _call_custom_api(self, prompt: str) -> Dict[str, Any]:
        # 调用自定义AI API
        response = requests.post(
            "https://api.custom-ai.com/v1/chat",
            headers={"Authorization": f"Bearer {self.custom_api_key}"},
            json={"prompt": prompt}
        )
        return response.json()
```

### 添加新的知识库后端

创建自定义数据库后端：

```python
from scripts.knowledge_db import KnowledgeDatabase

class PostgreSQLKnowledgeDatabase(KnowledgeDatabase):
    def __init__(self, connection_string: str):
        import psycopg2
        self.conn = psycopg2.connect(connection_string)
        self._init_database()
    
    def _init_database(self):
        # PostgreSQL特定的初始化逻辑
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id SERIAL PRIMARY KEY,
            signature TEXT UNIQUE NOT NULL,
            -- ... 其他字段
        )
        ''')
        self.conn.commit()
```

## 总结

智能知识库系统提供了完整的错误分析工作流：
- **自动化**：自动提取错误签名、匹配知识库、生成解决方案
- **智能化**：AI生成解决方案，不断学习优化
- **可管理**：人工审核流程，确保解决方案质量
- **可扩展**：模块化设计，易于扩展和集成

通过这个系统，您可以：
1. 快速解决重复出现的错误
2. 积累团队知识库
3. 减少人工排查时间
4. 提高问题解决效率

开始使用智能知识库，让错误分析变得更简单、更智能！