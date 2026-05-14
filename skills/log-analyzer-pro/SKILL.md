---
name: log-analyzer-pro
description: |
  专业日志分析专家技能 - 统一支持SSH远程日志和ELK集中式日志分析。
  
  核心功能：
  1. SSH远程日志分析 - 通过SSH连接服务器分析系统/应用日志
  2. ELK集中式日志分析 - 通过Elasticsearch API分析ELK集群日志
  3. 智能错误识别 - 基于知识库的错误模式匹配
  4. 根因定位 - 多维度错误分析和关联
  5. 解决方案推荐 - 基于知识库的智能推荐
  6. 自动化报告 - 多种格式报告生成
  7. 定时监控 - 定时任务和告警集成
  8. 知识管理 - 解决方案归档和共享
  
  适用于：
  - 生产环境故障排查
  - 性能问题分析
  - 安全事件调查
  - 运维知识积累
  
  NOT for: 实时流处理、日志采集配置、网络包分析。
---

# 专业日志分析专家技能

## 概述

`log-analyzer-pro` 是一个统一的日志分析平台，整合了SSH远程日志分析和ELK集中式日志分析的功能。它提供了完整的日志分析工作流，从日志获取、错误识别、根因分析到解决方案推荐和知识管理。

## 架构设计

### 双数据源支持
```
┌─────────────────────────────────────────────────────────────┐
│                    log-analyzer-pro                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │   SSH日志   │──────▶│  统一分析   │◀─────│   ELK日志   │ │
│  │  获取模块   │      │    引擎     │      │  获取模块   │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│         │                        │                        │ │
│         ▼                        ▼                        ▼ │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  远程服务器 │      │  知识库     │      │ ELK集群     │ │
│  │  (SSH连接)  │      │  匹配引擎   │      │ (API连接)   │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 功能模块
1. **数据获取层**：SSH连接器 + ELK API客户端
2. **分析引擎层**：错误识别 + 根因分析 + 关联分析
3. **知识库层**：解决方案匹配 + 智能推荐 + 自动归档
4. **输出层**：报告生成 + 告警通知 + 可视化

## 快速开始

### 1. 安装和配置

```bash
# 进入技能目录
cd ~/.openclaw/workspace-feishu001/my-skills/log-analyzer-pro

# 初始化配置
./log-analyzer-pro config init

# 编辑配置文件
vi config/ssh-config.yaml      # SSH连接配置
vi config/elk-config.yaml      # ELK连接配置
vi config/analysis-config.yaml # 分析规则配置
```

### 2. 基本使用

#### SSH日志分析
```bash
# 分析远程服务器日志
./log-analyzer-pro ssh --host server01 --log /var/log/syslog --lines 1000

# 分析多个服务器
./log-analyzer-pro ssh --hosts server01,server02,server03 --log /var/log/nginx/error.log

# 实时监控日志
./log-analyzer-pro ssh --host server01 --log /var/log/syslog --follow

# 批量分析
./log-analyzer-pro ssh --host-file servers.txt --log-pattern "*.log"
```

#### ELK日志分析
```bash
# 检查ELK集群健康
./log-analyzer-pro elk health

# 分析ELK错误日志
./log-analyzer-pro elk errors --time 1h --level ERROR

# 搜索特定错误
./log-analyzer-pro elk search --query "OutOfMemoryError" --time 6h

# 性能分析
./log-analyzer-pro elk performance --time 24h --metrics cpu,memory,disk
```

#### 统一分析（自动选择数据源）
```bash
# 智能分析（自动检测数据源）
./log-analyzer-pro analyze --target server01:syslog --time 2h

# 混合分析（同时分析SSH和ELK日志）
./log-analyzer-pro analyze --ssh-host server01 --elk-index logstash-* --time 1h

# 生成详细报告
./log-analyzer-pro analyze --target server01:nginx --time 6h --output report.html --format html
```

### 3. 知识库管理

```bash
# 列出所有解决方案
./log-analyzer-pro knowledge list

# 搜索解决方案
./log-analyzer-pro knowledge search "disk full"

# 查看解决方案详情
./log-analyzer-pro knowledge show elasticsearch/disk-space-full

# 添加新解决方案
./log-analyzer-pro knowledge add --title "新问题标题" --category system

# 更新解决方案
./log-analyzer-pro knowledge update system/20240428-new-issue.json --solution "新的解决方案"
```

### 4. 定时任务

```bash
# 设置定时监控
./tools/setup-cron.sh --mode full

# 查看定时任务
./tools/setup-cron.sh --list

# 生成日报
./tools/daily-report.sh --output reports/daily-$(date +%Y%m%d).md

# 发送邮件报告
python tools/send-email.py --config config/email-config.yaml --report reports/daily-20240428.md
```

## 详细功能说明

### SSH日志分析模块

#### 支持的日志类型
- **系统日志**: /var/log/syslog, /var/log/messages, /var/log/auth.log
- **应用日志**: /var/log/nginx/*, /var/log/apache2/*, /var/log/mysql/*
- **服务日志**: journalctl -u service-name
- **内核日志**: dmesg, /var/log/kern.log
- **自定义日志**: 任意文本日志文件

#### SSH连接配置
```yaml
# config/ssh-config.yaml
servers:
  production-web:
    host: 192.168.1.100
    port: 22
    username: admin
    key_path: ~/.ssh/id_rsa
    logs:
      - /var/log/nginx/access.log
      - /var/log/nginx/error.log
      - /var/log/syslog
  
  production-db:
    host: 192.168.1.101
    port: 22
    username: root
    password: "encrypted_password"
    logs:
      - /var/log/mysql/error.log
      - /var/log/syslog
```

#### SSH分析命令
```bash
# 基本日志获取
./log-analyzer-pro ssh get --server production-web --log /var/log/nginx/error.log --lines 500

# 错误分析
./log-analyzer-pro ssh analyze --server production-web --log /var/log/syslog --time "1 hour ago"

# 实时监控
./log-analyzer-pro ssh monitor --server production-web --log /var/log/nginx/access.log --follow --filter "status >= 500"

# 批量操作
./log-analyzer-pro ssh batch --servers production-web,production-db --command "df -h" --output disk-usage.txt
```

### ELK日志分析模块

#### ELK连接配置
```yaml
# config/elk-config.yaml
elasticsearch:
  hosts:
    - "http://elk-prod-01:9200"
    - "http://elk-prod-02:9200"
    - "http://elk-prod-03:9200"
  username: "elastic"
  password: "your_password"
  verify_certs: false
  timeout: 30
  indices:
    - "logstash-*"
    - "application-*"
    - "system-*"

kibana:
  host: "http://kibana-prod:5601"
  username: "kibana_user"
  password: "your_password"

logstash:
  hosts:
    - "logstash-prod:5044"
    - "logstash-prod:5000"
```

#### ELK分析命令
```bash
# 集群健康检查
./log-analyzer-pro elk health --detail

# 节点状态
./log-analyzer-pro elk nodes --format table

# 索引状态
./log-analyzer-pro elk indices --sort size:desc --limit 10

# 错误日志分析
./log-analyzer-pro elk errors --time 2h --level ERROR,WARNING --output errors-report.md

# 性能分析
./log-analyzer-pro elk performance --time 24h --metrics query_latency,index_rate,search_rate

# 自定义查询
./log-analyzer-pro elk query --dsl '{"query":{"match":{"level":"ERROR"}}}' --size 100 --sort "@timestamp:desc"
```

### 统一分析引擎

#### 智能错误识别
```bash
# 自动识别错误模式
./log-analyzer-pro analyze --target server01:syslog --auto-detect

# 模式匹配分析
./log-analyzer-pro analyze --target elk:logstash-* --patterns "OutOfMemory,Connection refused,Timeout"

# 根因分析
./log-analyzer-pro analyze --target server01:nginx --root-cause --depth 3

# 关联分析
./log-analyzer-pro analyze --targets server01:syslog,server02:syslog,elk:logstash-* --correlate
```

#### 报告生成
```bash
# 文本报告
./log-analyzer-pro report --target server01:all --time 24h --output daily-report.txt

# Markdown报告
./log-analyzer-pro report --target elk:all --time 7d --output weekly-report.md --format markdown

# HTML报告（带图表）
./log-analyzer-pro report --targets server01:nginx,server02:mysql,elk:logstash-* --time 1h --output incident-report.html --format html

# JSON报告（用于自动化处理）
./log-analyzer-pro report --target server01:syslog --time 2h --output analysis.json --format json
```

### 知识库系统

#### 知识库结构
```
knowledge-base/
├── elasticsearch/          # Elasticsearch相关问题
│   ├── disk-space-full.json
│   ├── cluster-red-status.json
│   └── index-read-only.json
├── logstash/              # Logstash相关问题
│   ├── pipeline-failed.json
│   ├── connection-error.json
│   └── performance-issue.json
├── kibana/                # Kibana相关问题
│   ├── slow-query.json
│   ├── connection-failed.json
│   └── memory-issue.json
├── system/                # 系统级问题
│   ├── disk-full.json
│   ├── memory-leak.json
│   └── service-crash.json
├── network/               # 网络问题
│   ├── connection-refused.json
│   ├── timeout-error.json
│   └── dns-failure.json
├── database/              # 数据库问题
│   ├── mysql-deadlock.json
│   ├── redis-oom.json
│   └── mongodb-slow-query.json
├── application/           # 应用级问题
│   ├── nginx-502.json
│   ├── java-oom.json
│   └── python-exception.json
└── monitoring/            # 监控告警问题
    ├── prometheus-down.json
    ├── grafana-dashboard-error.json
    └── alertmanager-failure.json
```

#### 知识条目格式
```json
{
  "id": "elasticsearch-disk-space-full-20240428",
  "title": "Elasticsearch磁盘空间不足导致索引只读",
  "category": "elasticsearch",
  "severity": "CRITICAL",
  "description": "Elasticsearch集群因磁盘空间超过水位线，自动将索引设置为只读模式",
  "error_patterns": [
    "index read-only",
    "FORBIDDEN/12/index read-only",
    "flood stage disk watermark"
  ],
  "symptoms": [
    "无法写入新数据",
    "索引状态显示为只读",
    "集群健康状态可能为YELLOW或RED",
    "磁盘使用率超过95%"
  ],
  "root_cause": "磁盘使用率超过Elasticsearch配置的水位线（默认low: 85%, high: 90%, flood: 95%）",
  "evidence": [
    "日志信息：blocked by: [FORBIDDEN/12/index read-only / allow delete (api)]",
    "命令输出：curl -X GET \"localhost:9200/_cluster/settings?pretty\" 显示磁盘水位线配置",
    "系统命令：df -h 显示磁盘使用率超过95%"
  ],
  "solution": {
    "immediate_action": [
      "清理磁盘空间：删除旧索引或临时文件",
      "临时调整水位线",
      "解除索引只读"
    ],
    "permanent_fix": [
      "扩容磁盘空间或增加数据节点",
      "设置索引生命周期策略，自动删除旧索引",
      "调整数据保留策略"
    ],
    "validation": [
      "检查集群健康状态",
      "验证索引可写",
      "监控磁盘使用率"
    ]
  },
  "prevention": [
    "设置磁盘使用率监控告警（阈值：80%警告，85%紧急）",
    "定期清理旧索引，设置保留策略",
    "使用ILM（索引生命周期管理）自动管理索引",
    "容量规划：预留20%以上的磁盘空间"
  ],
  "tags": ["disk", "read-only", "cluster", "emergency"],
  "created_at": "2024-04-28T10:30:00Z",
  "last_updated": "2024-04-28T10:30:00Z",
  "usage_count": 5,
  "success_rate": 0.95,
  "references": [
    "https://www.elastic.co/guide/en/elasticsearch/reference/current/disk-allocator.html"
  ],
  "notes": "此问题为生产环境常见问题，建议定期检查磁盘使用率"
}
```

#### 知识库管理
```bash
# 智能搜索（支持自然语言）
./log-analyzer-pro knowledge search "磁盘满了怎么办"

# 按分类浏览
./log-analyzer-pro knowledge browse --category elasticsearch

# 按严重级别过滤
./log-analyzer-pro knowledge browse --severity CRITICAL

# 查看统计信息
./log-analyzer-pro knowledge stats

# 导出知识库
./log-analyzer-pro knowledge export --format json --output knowledge-base-export.json

# 导入知识库
./log-analyzer-pro knowledge import --file new-knowledge.json
```

### 定时监控和告警

#### 定时任务配置
```bash
# 查看可用的定时任务模板
./tools/setup-cron.sh --list-templates

# 设置基础监控（每5分钟检查健康，每15分钟检查错误，每小时生成报告）
./tools/setup-cron.sh --mode basic

# 设置完整监控（包括性能分析和知识库更新）
./tools/setup-cron.sh --mode full

# 自定义定时任务
./tools/setup-cron.sh --custom "*/10 * * * * /path/to/log-analyzer-pro elk health --quiet"

# 删除定时任务
./tools/setup-cron.sh --remove
```

#### 告警配置
```yaml
# config/alert-config.yaml
alerts:
  # 集群健康告警
  cluster_health:
    enabled: true
    conditions:
      - field: "cluster_health.status"
        operator: "!="
        value: "green"
        severity: "CRITICAL"
    actions:
      - type: "email"
        recipients: ["admin@example.com"]
      - type: "feishu"
        webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
  
  # 错误数量告警
  error_count:
    enabled: true
    conditions:
      - field: "error_analysis.total_errors"
        operator: ">"
        value: 10
        severity: "WARNING"
      - field: "error_analysis.total_errors"
        operator: ">"
        value: 50
        severity: "ERROR"
    actions:
      - type: "email"
        recipients: ["team@example.com"]
  
  # 性能告警
  performance:
    enabled: true
    conditions:
      - field: "performance.query_latency.p95"
        operator: ">"
        value: 1000  # 1秒
        severity: "WARNING"
      - field: "performance.cpu_usage.avg"
        operator: ">"
        value: 80    # 80%
        severity: "WARNING"
```

#### 告警命令
```bash
# 测试告警配置
./log-analyzer-pro alert test --config config/alert-config.yaml

# 查看当前告警状态
./log-analyzer-pro alert status

# 手动触发告警检查
./log-analyzer-pro alert check --now

# 查看告警历史
./log-analyzer-pro alert history --days 7
```

### 报告和可视化

#### 报告类型
```bash
# 健康报告
./log-analyzer-pro report health --time 24h --output health-report.md

# 错误报告
./log-analyzer-pro report errors --time 7d --output errors-report.md --format html

# 性能报告
./log-analyzer-pro report performance --time 30d --output performance-report.html --format html

# 综合报告
./log-analyzer-pro report comprehensive --time 1d --output daily-comprehensive.md --sections health,errors,performance,knowledge

# 比较报告
./log-analyzer-pro report compare --time1 "2024-04-01" --time2 "2024-04-28" --output comparison-report.md
```

#### 可视化选项
```bash
# 生成图表（需要matplotlib）
./log-analyzer-pro visualize --type line --data errors.json --output errors-chart.png

# 生成仪表板
./log-analyzer-pro visualize --type dashboard --data report.json --output dashboard.html

# 导出到Grafana
./log-analyzer-pro visualize --export-grafana --data metrics.json --output grafana-dashboard.json
```

## 高级功能

### 1. 机器学习分析（实验性）
```bash
# 异常检测
./log-analyzer-pro ml anomaly --data logs.json --model isolation-forest --output anomalies.json

# 模式发现
./log-analyzer-pro ml patterns --data logs.json --min-support 0.1 --output patterns.json

# 预测分析
./log-analyzer-pro ml predict --data historical.json --horizon 24h --output predictions.json
```

### 2. 工作流自动化
```bash
# 定义分析工作流
./log-analyzer-pro workflow define --name "daily-monitoring" --steps "health-check,error-analysis,performance-review"

# 执行工作流
./log-analyzer-pro workflow run --name "daily-monitoring" --time 24h

# 调度工作流
./log-analyzer-pro workflow schedule --name "daily-monitoring" --cron "0 8 * * *"
```

### 3. 团队协作
```bash
# 共享分析结果
./log-analyzer-pro share --report report.md --teams "devops,platform,sre"

# 添加评论
./log-analyzer-pro comment --report report.md --comment "已确认问题根因，建议扩容磁盘"

# 分配任务
./log-analyzer-pro assign --issue "disk-full-20240428" --assignee "alice@example.com" --priority high
```

### 4. API集成
```bash
# 启动API服务器
./log-analyzer-pro api start --port 8080 --host 0.0.0.0

# 使用curl调用API
curl -X GET "http://localhost:8080/api/v1/health"
curl -X POST "http://localhost:8080/api/v1/analyze" -H "Content-Type: application/json" -d '{"target": "server01:syslog", "time": "1h"}'

# 生成API客户端
./log-analyzer-pro api client --language python --output client.py
```

## 配置说明

### 主配置文件
```yaml
# config/main-config.yaml
general:
  log_level: "INFO"
  output_format: "text"  # text, json, yaml, html
  timezone: "Asia/Shanghai"
  retention_days: 30

ssh:
  config_file: "config/ssh-config.yaml"
  default_user: "admin"
  default_key: "~/.ssh/id_rsa"
  connection_timeout: 30
  command_timeout: 300

elk:
  config_file: "config/elk-config.yaml"
  default_timeout: 30
  max_retries: 3
  verify_ssl: false

analysis:
  config_file: "config/analysis-config.yaml"
  default_time_range: "1h"
  error_threshold: 10
  warning_threshold: 5

knowledge:
  base_dir: "knowledge-base"
  auto_update: true
  search_backend: "simple"  # simple, elasticsearch

reporting:
  default_format: "markdown"
  templates_dir: "templates"
  auto_generate: true

alerts:
  config_file: "config/alert-config.yaml"
  enabled: true
  check_interval: 300  # 5分钟

scheduling:
  enabled: true
  config_file: "config/schedule-config.yaml"
```

### SSH连接配置
```yaml
# config/ssh-config.yaml
servers:
  web-prod-01:
    host: "192.168.1.100"
    port: 22
    username: "admin"
    authentication:
      type: "key"  # key, password, agent
      key_path: "~/.ssh/id_rsa"
      password: ""  # 留空使用key认证
    logs:
      - path: "/var/log/nginx/access.log"
        type: "nginx_access"
        parser: "nginx"
      - path: "/var/log/nginx/error.log"
        type: "nginx_error"
        parser: "nginx"
      - path: "/var/log/syslog"
        type: "system"
        parser: "syslog"
    commands:
      health: "systemctl status nginx"
      disk: "df -h"
      memory: "free -m"
  
  db-prod-01:
    host: "192.168.1.101"
    port: 22
    username: "root"
    authentication:
      type: "password"
      password: "encrypted_password_here"
    logs:
      - path: "/var/log/mysql/error.log"
        type: "mysql_error"
        parser: "mysql"
    commands:
      health: "systemctl status mysql"
      connections: "mysqladmin status"
```

### ELK连接配置
```yaml
# config/elk-config.yaml
elasticsearch:
  # 集群配置
  hosts:
    - "http://elk-prod-01:9200"
    - "http://elk-prod-02:9200"
    - "http://elk-prod-03:9200"
  
  # 认证配置
  authentication:
    enabled: true
    type: "basic"  # basic, api_key, ssl
    username: "elastic"
    password: "your_password_here"
  
  # SSL配置
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
  
  # 查询配置
  query:
    default_size: 1000
    max_size: 10000
    scroll_time: "5m"

kibana:
  host: "http://kibana-prod:5601"
  authentication:
    enabled: true
    username: "kibana_user"
    password: "your_password_here"

logstash:
  hosts:
    - "logstash-prod:5044"
    - "logstash-prod:5000"
  monitoring:
    enabled: true
    port: 9600
```

### 分析规则配置
```yaml
# config/analysis-config.yaml
error_patterns:
  # 系统错误
  - name: "out_of_memory"
    pattern: "OutOfMemoryError|java.lang.OutOfMemoryError"
    category: "system"
    severity: "CRITICAL"
    solution: "system/out-of-memory.json"
  
  - name: "disk_full"
    pattern: "No space left on device|disk full"
    category: "system"
    severity: "CRITICAL"
    solution: "system/disk-full.json"
  
  # 网络错误
  - name: "connection_refused"
    pattern: "Connection refused|Connection reset by peer"
    category: "network"
    severity: "ERROR"
    solution: "network/connection-refused.json"
  
  - name: "timeout"
    pattern: "timeout|timed out|read timeout"
    category: "network"
    severity: "WARNING"
    solution: "network/timeout-error.json"
  
  # 应用错误
  - name: "nginx_502"
    pattern: "502 Bad Gateway"
    category: "application"
    severity: "ERROR"
    solution: "application/nginx-502.json"
  
  - name: "mysql_deadlock"
    pattern: "Deadlock found|Lock wait timeout exceeded"
    category: "database"
    severity: "ERROR"
    solution: "database/mysql-deadlock.json"

analysis_rules:
  # 时间窗口分析
  time_windows:
    - name: "last_hour"
      value: "1h"
    - name: "last_6_hours"
      value: "6h"
    - name: "last_24_hours"
      value: "24h"
    - name: "last_7_days"
      value: "7d"
  
  # 错误阈值
  thresholds:
    critical_errors: 10
    warning_errors: 5
    error_increase_rate: 2.0  # 错误增长率阈值
  
  # 关联分析
  correlation:
    enabled: true
    time_window: "5m"
    min_correlation: 0.7
  
  # 根因分析
  root_cause:
    enabled: true
    max_depth: 3
    include_timeline: true

reporting:
  # 报告模板
  templates:
    daily: "templates/daily-report.md.j2"
    weekly: "templates/weekly-report.html.j2"
    incident: "templates/incident-report.md.j2"
  
  # 图表配置
  charts:
    enabled: true
    type: "matplotlib"  # matplotlib, plotly, none
    theme: "dark"
    output_format: "png"
  
  # 通知配置
  notifications:
    email:
      enabled: true
      template: "templates/email-notification.md.j2"
    feishu:
      enabled: false
      webhook: ""
    slack:
      enabled: false
      webhook: ""
```

## 故障排除

### 常见问题

#### 1. SSH连接失败
```bash
# 测试SSH连接
ssh -v user@host

# 检查SSH配置
cat ~/.ssh/config

# 检查密钥权限
chmod 600 ~/.ssh/id_rsa

# 使用详细模式
./log-analyzer-pro ssh get --server server01 --log /var/log/syslog --verbose
```

#### 2. ELK连接失败
```bash
# 测试Elasticsearch连接
curl -X GET "http://localhost:9200/"

# 检查集群健康
curl -X GET "http://localhost:9200/_cluster/health?pretty"

# 使用详细模式
./log-analyzer-pro elk health --verbose

# 检查配置文件
./log-analyzer-pro config validate --type elk
```

#### 3. 分析结果不准确
```bash
# 检查错误模式配置
./log-analyzer-pro config show --section error_patterns

# 测试模式匹配
./log-analyzer-pro test pattern --log sample.log --pattern "OutOfMemory"

# 调整分析参数
./log-analyzer-pro analyze --target server01:syslog --time 2h --threshold 5
```

#### 4. 知识库搜索无结果
```bash
# 重建知识库索引
./log-analyzer-pro knowledge rebuild-index

# 检查知识库文件
./log-analyzer-pro knowledge list --verbose

# 添加测试条目
./log-analyzer-pro knowledge add --title "测试问题" --category test --pattern "test pattern"
```

### 调试模式
```bash
# 启用调试日志
LOG_LEVEL=DEBUG ./log-analyzer-pro analyze --target server01:syslog

# 保存调试信息
./log-analyzer-pro analyze --target server01:syslog --debug --debug-file debug.log

# 性能分析
./log-analyzer-pro analyze --target server01:syslog --profile --profile-file profile.json
```

## 最佳实践

### 1. 配置管理
- 使用版本控制管理配置文件
- 为不同环境创建配置模板
- 定期备份配置文件
- 使用环境变量覆盖敏感配置

### 2. 监控策略
- 高频监控（5分钟）：关键服务健康状态
- 中频监控（15分钟）：错误日志检查
- 低频监控（1小时）：性能指标分析
- 定期报告（每天）：综合报告生成

### 3. 告警策略
- 立即告警：服务不可用、数据丢失
- 快速告警（5分钟）：性能下降、错误增加
- 日常告警（1小时）：趋势异常、容量预警
- 定期检查（每天）：配置变更、安全扫描

### 4. 知识管理
- 每个解决方案独立文档
- 包含问题描述、根因、解决方案、验证步骤
- 定期回顾和更新
- 建立分类索引和搜索

### 5. 团队协作
- 共享分析报告和解决方案
- 建立评审流程
- 定期知识分享
- 建立on-call轮值

## 性能优化

### 1. 查询优化
```bash
# 限制查询时间范围
./log-analyzer-pro analyze --time 1h --limit 1000

# 使用过滤条件
./log-analyzer-pro analyze --filter "level:ERROR AND host:web-*"

# 分批处理大数据集
./log-analyzer-pro analyze --batch-size 1000 --parallel 4
```

### 2. 缓存优化
```bash
# 启用查询缓存
./log-analyzer-pro analyze --cache --cache-ttl 300

# 使用结果缓存
./log-analyzer-pro analyze --cache-results --cache-dir /tmp/log-cache

# 清理缓存
./log-analyzer-pro cache clear --older-than 7d
```

### 3. 并行处理
```bash
# 并行分析多个服务器
./log-analyzer-pro ssh analyze --servers server01,server02,server03 --parallel 3

# 并行查询多个索引
./log-analyzer-pro elk query --indices logstash-*,metricbeat-* --parallel 2

# 控制并发数
./log-analyzer-pro analyze --max-workers 4 --max-connections 10
```

## 安全考虑

### 1. 认证安全
- 使用SSH密钥认证而非密码
- 定期轮换密钥和密码
- 使用密钥管理服务
- 启用多因素认证

### 2. 数据安全
- 加密存储敏感配置
- 限制日志访问权限
- 定期清理敏感数据
- 审计日志访问记录

### 3. 网络安全
- 使用VPN或专用网络
- 限制IP访问范围
- 启用TLS/SSL加密
- 定期安全扫描

### 4. 合规性
- 遵守数据保留政策
- 记录所有分析操作
- 定期安全审计
- 员工安全培训

## 扩展和集成

### 1. 插件系统
```bash
# 列出可用插件
./log-analyzer-pro plugins list

# 安装插件
./log-analyzer-pro plugins install prometheus-exporter

# 启用插件
./log-analyzer-pro plugins enable prometheus-exporter

# 配置插件
./log-analyzer-pro plugins config prometheus-exporter --port 9090
```

### 2. Web界面
```bash
# 启动Web界面
./log-analyzer-pro web start --port 8080

# 访问Web界面
open http://localhost:8080

# 配置Web界面
./log-analyzer-pro web config --theme dark --language zh-CN
```

### 3. API集成
```bash
# 生成OpenAPI规范
./log-analyzer-pro api docs --output openapi.yaml

# 生成客户端库
./log-analyzer-pro api client --language python --output client.py
./log-analyzer-pro api client --language go --output client.go
./log-analyzer-pro api client --language javascript --output client.js
```

### 4. 数据导出
```bash
# 导出到Prometheus
./log-analyzer-pro export prometheus --output metrics.prom

# 导出到Grafana
./log-analyzer-pro export grafana --output dashboard.json

# 导出到Elasticsearch
./log-analyzer-pro export elasticsearch --index log-analysis-results

# 导出到CSV
./log-analyzer-pro export csv --output analysis.csv
```

## 版本历史

### v1.0.0 (2026-04-28)
- 初始版本发布
- 统一SSH和ELK日志分析
- 智能错误识别和根因分析
- 知识库驱动的解决方案推荐
- 多种报告格式支持
- 定时任务和告警集成

### 计划功能
- 机器学习异常检测
- 实时流处理支持
- 更多数据源集成（AWS CloudWatch, GCP Logging等）
- 高级可视化仪表板
- 团队协作功能
- 移动端应用

## 支持和贡献

### 问题反馈
1. 检查配置文件和日志
2. 使用 `--verbose` 参数获取详细输出
3. 提交issue到项目仓库

### 功能建议
欢迎提交功能建议和改进意见：
1. 新的数据源支持
2. 额外的分析规则
3. 集成其他监控系统
4. 性能优化建议

### 贡献代码
1. Fork项目仓库
2. 创建功能分支
3. 提交Pull Request
4. 更新文档和测试

### 社区支持
- 文档：https://docs.log-analyzer-pro.example.com
- 论坛：https://community.log-analyzer-pro.example.com
