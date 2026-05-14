# 智能知识库功能

## 🎯 功能概述

智能知识库是 `log-analyzer-pro` 的核心增强功能，实现了您描述的完整工作流：

```
1. 提取本次报错的签名
   ↓
2. 在知识库中搜索
   ↓
3. 命中：直接返回历史解决方案
   ↓
4. 未命中：调用AI接口生成解决方案 → 请人工确认 → 存入归档
```

## 📊 数据库结构

智能知识库使用SQLite数据库，结构如下：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| signature | TEXT | 错误签名（唯一标识） |
| error_summary | TEXT | 报错摘要 |
| solution | TEXT | 解决方案 |
| hit_count | INTEGER | 命中次数 |
| success_count | INTEGER | 成功次数 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| category | TEXT | 分类（system/network/database等） |
| severity | TEXT | 严重级别（CRITICAL/ERROR/WARNING/INFO） |
| tags | TEXT | 标签（JSON数组） |
| verified | BOOLEAN | 是否已验证 |
| ai_generated | BOOLEAN | 是否AI生成 |
| verified_by | TEXT | 验证人 |
| verified_at | TIMESTAMP | 验证时间 |

## 🚀 快速开始

### 1. 初始化知识库

```bash
# 初始化数据库
python scripts/knowledge_db.py --init

# 添加示例解决方案
python scripts/knowledge_db.py --add \
  --signature "RedisConnectionException:9000" \
  --summary "连接Redis超时" \
  --solution "检查防火墙配置，重启Redis Sentinel" \
  --category "database" \
  --severity "ERROR" \
  --tags "redis,connection,timeout" \
  --verified \
  --verified-by "admin"

python scripts/knowledge_db.py --add \
  --signature "MySQLIntegrityConstraintViolation" \
  --summary "唯一键冲突" \
  --solution "业务层先查后插或使用 ON DUPLICATE KEY UPDATE" \
  --category "database" \
  --severity "WARNING" \
  --tags "mysql,constraint,duplicate" \
  --verified \
  --verified-by "admin"
```

### 2. 配置AI接口

编辑 `config/ai-config.yaml`：

```yaml
openai:
  api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
  model: "gpt-3.5-turbo"
  max_tokens: 2000
  temperature: 0.7
```

设置环境变量：
```bash
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. 使用智能分析

#### 分析单个错误
```bash
# 使用主脚本
./log-analyzer-pro knowledge analyze-error \
  --error "java.net.ConnectException: Connection refused" \
  --source "production-server"

# 或直接使用Python脚本
python scripts/intelligent_knowledge.py analyze \
  --error "MySQLIntegrityConstraintViolationException: Duplicate entry '12345'" \
  --source "production-db"
```

#### 分析日志文件
```bash
# 分析日志文件中的错误
./log-analyzer-pro knowledge analyze-log \
  --file /var/log/application.log \
  --max-errors 50

# 自动确认高置信度的解决方案
./log-analyzer-pro knowledge analyze-log \
  --file /var/log/application.log \
  --max-errors 50 \
  --auto-confirm
```

#### 管理待确认的解决方案
```bash
# 列出所有待确认的解决方案
./log-analyzer-pro knowledge list-pending

# 确认解决方案
./log-analyzer-pro knowledge confirm-solution \
  --file work/pending_solutions/pending_abc123.json \
  --reviewer "admin" \
  --notes "解决方案正确，已验证"

# 拒绝解决方案
./log-analyzer-pro knowledge reject-solution \
  --file work/pending_solutions/pending_abc123.json \
  --reviewer "admin" \
  --reason "解决方案不完整"
```

#### 查看统计信息
```bash
# 查看知识库统计
./log-analyzer-pro knowledge intelligent-stats

# 输出示例:
# 知识库统计:
#   总解决方案数: 45
#   已验证解决方案: 38
#   AI生成解决方案: 7
#   总命中次数: 123
#   总成功次数: 115
#   成功率: 93.50%
```

## 🔧 工作流示例

### 场景：分析Redis连接错误

```bash
# 1. 错误发生
错误信息: "RedisConnectionException: Connection timeout after 9000ms"

# 2. 提取签名
签名: "7a8b9c0d1e2f" (自动生成)

# 3. 知识库搜索
#   找到匹配项: RedisConnectionException:9000
#   命中次数: 45
#   返回解决方案: "检查防火墙配置，重启Redis Sentinel"

# 4. 如果未找到，AI生成解决方案
#   AI分析错误，生成解决方案
#   置信度: 0.85
#   需要人工确认

# 5. 人工审核
#   审核AI生成的解决方案
#   确认正确性
#   保存到知识库

# 6. 下次遇到相同错误
#   直接返回解决方案
#   命中次数: 46
```

### 场景：批量分析应用日志

```bash
# 1. 分析日志文件
./log-analyzer-pro knowledge analyze-log \
  --file /var/log/app/error.log \
  --max-errors 100

# 2. 查看结果
#   分析完成: 100个错误
#   知识库命中: 65个
#   AI生成: 35个
#   需要人工确认: 10个（置信度<0.7）
#   自动确认: 25个（置信度>=0.7）

# 3. 审核待确认的解决方案
./log-analyzer-pro knowledge list-pending
# 输出: 10个待确认的解决方案

# 4. 批量确认
for file in work/pending_solutions/*.json; do
  ./log-analyzer-pro knowledge confirm-solution \
    --file "$file" \
    --reviewer "batch-review" \
    --notes "批量审核通过"
done
```

## ⚙️ 配置说明

### 主要配置文件

1. **config/intelligent-analyzer.yaml** - 智能分析器配置
2. **config/ai-config.yaml** - AI接口配置
3. **knowledge.db** - SQLite知识库数据库

### 关键配置项

```yaml
# AI生成配置
ai:
  generation:
    min_confidence: 0.7      # 最小置信度阈值（0.0-1.0）
    auto_confirm: false      # 是否自动确认AI生成的解决方案
    max_retries: 3           # 最大重试次数

# 工作流配置
workflow:
  analysis:
    extract_signature: true   # 是否提取错误签名
    search_knowledge_base: true  # 是否搜索知识库
    generate_if_not_found: true  # 是否生成AI解决方案
    require_human_review: true   # 是否需要人工审核
```

## 📈 监控和维护

### 定期检查
```bash
# 查看知识库统计
./log-analyzer-pro knowledge intelligent-stats

# 检查未验证的解决方案
python scripts/knowledge_db.py --search --verified false

# 查看最常用的解决方案
python scripts/knowledge_db.py --search --limit 10 --sort-by hit_count
```

### 备份和恢复
```bash
# 备份知识库
python scripts/knowledge_db.py --export --output knowledge_backup_$(date +%Y%m%d).json

# 恢复知识库
python scripts/knowledge_db.py --import --file knowledge_backup_20240428.json
```

### 性能优化
```bash
# 重建索引
python scripts/knowledge_db.py --rebuild-index

# 清理旧数据
# 删除30天前的未验证解决方案
```

## 🧪 测试

### 运行测试套件
```bash
# 运行完整测试
chmod +x test_intelligent_knowledge.sh
./test_intelligent_knowledge.sh
```

### 手动测试
```bash
# 测试错误签名提取
python scripts/error_signature.py --input "java.lang.OutOfMemoryError: Java heap space"

# 测试知识库操作
python scripts/knowledge_db.py --stats

# 测试AI生成（模拟模式）
python scripts/intelligent_knowledge.py analyze \
  --error "测试错误信息" \
  --source "test"
```

## 🔍 故障排除

### 常见问题

1. **AI生成失败**
   ```bash
   # 检查API密钥
   echo $OPENAI_API_KEY
   
   # 检查网络连接
   curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
   
   # 查看日志
   tail -f logs/ai_generator.log
   ```

2. **知识库查询慢**
   ```bash
   # 重建索引
   python scripts/knowledge_db.py --rebuild-index
   
   # 优化查询
   python scripts/knowledge_db.py --search --query "错误关键词" --limit 10
   ```

3. **签名提取不准确**
   ```bash
   # 查看提取的签名
   python scripts/error_signature.py --input "你的错误信息"
   
   # 调整错误模式
   # 编辑 scripts/error_signature.py 中的 ERROR_PATTERNS
   ```

### 日志查看
```bash
# AI生成日志
tail -f logs/ai_generator.log

# 智能分析器日志
tail -f logs/intelligent_analyzer.log

# 数据库操作日志
tail -f logs/knowledge_db.log
```

## 📚 相关文件

### 核心脚本
- `scripts/intelligent_knowledge.py` - 智能知识库管理器
- `scripts/knowledge_db.py` - 知识库数据库管理
- `scripts/error_signature.py` - 错误签名提取器
- `scripts/ai_solution_generator.py` - AI解决方案生成器
- `scripts/intelligent_analyzer.py` - 智能分析器

### 配置文件
- `config/intelligent-analyzer.yaml` - 智能分析器配置
- `config/ai-config.yaml` - AI接口配置

### 文档
- `docs/intelligent-knowledge-guide.md` - 完整使用指南
- `test_intelligent_knowledge.sh` - 测试脚本

## 🎉 开始使用

### 第一步：初始化
```bash
# 1. 设置API密钥
export OPENAI_API_KEY="your-api-key"

# 2. 运行测试
./test_intelligent_knowledge.sh

# 3. 分析第一个错误
./log-analyzer-pro knowledge analyze-error \
  --error "你的错误信息" \
  --source "你的系统"
```

### 第二步：集成到现有流程
```bash
# 1. 分析生产日志
./log-analyzer-pro knowledge analyze-log \
  --file /path/to/production.log \
  --max-errors 100

# 2. 审核AI生成的解决方案
./log-analyzer-pro knowledge list-pending

# 3. 确认有效的解决方案
./log-analyzer-pro knowledge confirm-solution \
  --file work/pending_solutions/pending_xxx.json \
  --reviewer "你的用户名"
```

### 第三步：定期维护
```bash
# 1. 每天分析新错误
0 2 * * * /path/to/log-analyzer-pro knowledge analyze-log --file /var/log/app/error.log --max-errors 50

# 2. 每周审核待确认的解决方案
0 9 * * 1 /path/to/log-analyzer-pro knowledge list-pending

# 3. 每月备份知识库
0 3 1 * * /path/to/log-analyzer-pro knowledge export --output /backup/knowledge_$(date +\%Y\%m\%d).json
```

## 🤝 贡献

欢迎贡献错误模式、解决方案和改进建议！

1. 提交Issue报告问题
2. 提交Pull Request贡献代码
3. 分享您的使用案例

## 📞 支持

如有问题，请：
1. 查看日志文件
2. 运行测试脚本
3. 检查配置文件
4. 提交Issue

---

**智能知识库系统** - 让错误分析变得更智能、更高效！