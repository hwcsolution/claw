# log-analyzer-pro

专业日志分析专家技能 - 统一支持SSH远程日志和ELK集中式日志分析。

## 🚀 快速开始

### 1. 安装和初始化

```bash
# 进入技能目录
cd ~/.openclaw/workspace-feishu001/my-skills/log-analyzer-pro

# 运行快速启动向导
./tools/quick-start.sh
```

### 2. 基本使用

#### SSH日志分析
```bash
# 分析远程服务器日志
./log-analyzer-pro ssh analyze --server production-web --log /var/log/syslog --time "1 hour ago"

# 实时监控日志
./log-analyzer-pro ssh monitor --server production-web --log /var/log/nginx/error.log --follow

# 批量分析多个服务器
./log-analyzer-pro ssh batch --servers production-web,production-db --log /var/log/syslog --lines 1000
```

#### ELK日志分析
```bash
# 检查ELK集群健康
./log-analyzer-pro elk health

# 搜索错误日志
./log-analyzer-pro elk errors --time 2h --level ERROR

# 性能分析
./log-analyzer-pro elk performance --time 24h --metrics cpu,memory,disk

# 自定义查询
./log-analyzer-pro elk query --dsl '{"query":{"match":{"level":"ERROR"}}}' --size 100
```

#### 统一分析
```bash
# 智能分析（自动选择数据源）
./log-analyzer-pro analyze --target server01:syslog --time 1h

# 混合分析
./log-analyzer-pro analyze --ssh-host server01 --elk-index logstash-* --time 30m

# 生成报告
./log-analyzer-pro analyze --target server01:nginx --time 6h --output report.html --format html
```

## 📁 项目结构

```
log-analyzer-pro/
├── SKILL.md                    # 技能文档（详细使用说明）
├── log-analyzer-pro           # 统一入口脚本
├── README.md                  # 本文档
├── config/                    # 配置文件目录
│   ├── main-config.yaml      # 主配置文件
│   ├── ssh-config.yaml       # SSH连接配置
│   ├── elk-config.yaml       # ELK连接配置
│   ├── analysis-config.yaml  # 分析规则配置
│   └── alert-config.yaml     # 告警配置
├── scripts/                   # Python脚本
│   ├── config_manager.py     # 配置管理
│   ├── ssh_log_fetcher.py    # SSH日志获取
│   ├── elk_health.py         # ELK健康检查
│   ├── log_analyzer.py       # 日志分析引擎
│   ├── knowledge_manager.py  # 知识库管理
│   ├── report_generator.py   # 报告生成
│   ├── alert_manager.py      # 告警管理
│   └── workflow_manager.py   # 工作流管理
├── tools/                     # 工具脚本
│   ├── setup-cron.sh         # 定时任务设置
│   ├── quick-start.sh        # 快速启动向导
│   ├── daily-report.sh       # 日报生成
│   ├── send-email.py         # 邮件发送
│   └── backup.sh             # 备份工具
├── examples/                  # 示例文件
│   ├── ssh-config-example.yaml
│   └── elk-config-example.yaml
├── logs/                      # 日志目录
├── reports/                   # 报告目录
└── templates/                 # 报告模板
```

## 🔧 配置说明

### 1. 初始化配置
```bash
# 初始化所有配置文件
./log-analyzer-pro config init

# 编辑SSH配置
./log-analyzer-pro config edit ssh

# 编辑ELK配置
./log-analyzer-pro config edit elk

# 验证配置
./log-analyzer-pro config validate
```

### 2. SSH配置 (config/ssh-config.yaml)
```yaml
servers:
  production-web:
    host: "192.168.1.100"
    port: 22
    username: "admin"
    authentication:
      type: "key"  # key, password, agent
      key_path: "~/.ssh/id_rsa"
      password: ""
    logs:
      - path: "/var/log/syslog"
        type: "system"
        parser: "syslog"
      - path: "/var/log/nginx/error.log"
        type: "nginx_error"
        parser: "nginx"
    commands:
      health: "systemctl status nginx"
      disk: "df -h"
      memory: "free -m"
```

### 3. ELK配置 (config/elk-config.yaml)
```yaml
elasticsearch:
  hosts:
    - "http://elk-prod-01:9200"
    - "http://elk-prod-02:9200"
    - "http://elk-prod-03:9200"
  authentication:
    enabled: true
    type: "basic"
    username: "elastic"
    password: "your_password_here"
  indices:
    logs: "logstash-*"
    metrics: "metricbeat-*"
```

## 📊 功能特性

### 1. 双数据源支持
- **SSH远程日志**: 通过SSH连接分析服务器日志
- **ELK集中式日志**: 通过Elasticsearch API分析ELK集群日志
- **智能数据源选择**: 根据目标自动选择最佳数据源
- **混合分析**: 同时分析SSH和ELK日志

### 2. 智能分析引擎
- **错误模式识别**: 基于规则和机器学习的错误识别
- **根因分析**: 多维度错误关联和根因定位
- **知识库匹配**: 自动匹配历史解决方案
- **趋势分析**: 错误频率和趋势分析

### 3. 知识库系统
- **解决方案库**: 按分类存储运维解决方案
- **智能搜索**: 自然语言搜索和模式匹配
- **自动归档**: 将验证有效的方案自动归档
- **使用统计**: 记录解决方案使用次数和成功率

### 4. 报告和可视化
- **多种格式**: 支持文本、Markdown、HTML、JSON输出
- **图表生成**: 自动生成统计图表
- **定时报告**: 自动生成日报、周报、月报
- **自定义模板**: 支持自定义报告模板

### 5. 定时监控
- **健康检查**: 定时检查集群和服务健康状态
- **错误监控**: 实时监控错误日志
- **性能监控**: 监控性能指标和趋势
- **告警通知**: 支持邮件、飞书、Slack告警

### 6. 工作流自动化
- **分析工作流**: 定义和执行分析工作流
- **定时调度**: 自动调度分析任务
- **团队协作**: 共享分析结果和解决方案
- **API集成**: 提供REST API接口

## 🛠️ 常用命令

### 配置管理
```bash
# 显示所有配置
./log-analyzer-pro config show

# 编辑特定配置
./log-analyzer-pro config edit ssh
./log-analyzer-pro config edit elk

# 验证配置
./log-analyzer-pro config validate

# 备份配置
./log-analyzer-pro config backup

# 恢复配置
./log-analyzer-pro config restore <备份文件>
```

### SSH日志分析
```bash
# 获取日志
./log-analyzer-pro ssh get --server server01 --log /var/log/syslog --lines 1000

# 分析日志
./log-analyzer-pro ssh analyze --server server01 --log /var/log/nginx/error.log --time "2 hours ago"

# 实时监控
./log-analyzer-pro ssh monitor --server server01 --log /var/log/syslog --follow --filter "ERROR"

# 批量操作
./log-analyzer-pro ssh batch --servers server01,server02 --command "df -h" --output disk-usage.txt

# 连接测试
./log-analyzer-pro ssh test --server server01
```

### ELK日志分析
```bash
# 集群健康
./log-analyzer-pro elk health --detail

# 节点状态
./log-analyzer-pro elk nodes --format table

# 索引状态
./log-analyzer-pro elk indices --sort size:desc --limit 10

# 错误分析
./log-analyzer-pro elk errors --time 6h --level ERROR,WARNING --output errors-report.md

# 性能分析
./log-analyzer-pro elk performance --time 24h --metrics query_latency,index_rate,search_rate

# 自定义查询
./log-analyzer-pro elk query --dsl '{"query":{"range":{"@timestamp":{"gte":"now-1h"}}}}' --size 500
```

### 知识库管理
```bash
# 列出所有解决方案
./log-analyzer-pro knowledge list

# 搜索解决方案
./log-analyzer-pro knowledge search "磁盘空间不足"
./log-analyzer-pro knowledge search --category elasticsearch
./log-analyzer-pro knowledge search --severity CRITICAL

# 查看解决方案详情
./log-analyzer-pro knowledge show elasticsearch/disk-space-full

# 添加新解决方案
./log-analyzer-pro knowledge add --title "新问题标题" --category system --severity ERROR

# 更新解决方案
./log-analyzer-pro knowledge update system/20240428-new-issue.json --solution "新的解决方案"

# 查看统计信息
./log-analyzer-pro knowledge stats
```

### 报告生成
```bash
# 健康报告
./log-analyzer-pro report health --time 24h --output health-report.md

# 错误报告
./log-analyzer-pro report errors --time 7d --output errors-report.html --format html

# 性能报告
./log-analyzer-pro report performance --time 30d --output performance-report.json --format json

# 综合报告
./log-analyzer-pro report comprehensive --time 1d --output daily-comprehensive.md --sections health,errors,performance,knowledge

# 比较报告
./log-analyzer-pro report compare --time1 "2024-04-01" --time2 "2024-04-28" --output comparison-report.md
```

### 告警管理
```bash
# 测试告警配置
./log-analyzer-pro alert test --config config/alert-config.yaml

# 查看告警状态
./log-analyzer-pro alert status

# 检查告警
./log-analyzer-pro alert check --now

# 查看告警历史
./log-analyzer-pro alert history --days 7

# 管理告警配置
./log-analyzer-pro alert config --show
```

### 工作流管理
```bash
# 定义工作流
./log-analyzer-pro workflow define --name "daily-monitoring" --steps "health-check,error-analysis,performance-review"

# 运行工作流
./log-analyzer-pro workflow run --name "daily-monitoring" --time 24h

# 列出工作流
./log-analyzer-pro workflow list

# 调度工作流
./log-analyzer-pro workflow schedule --name "daily-monitoring" --cron "0 8 * * *"

# 查看工作流状态
./log-analyzer-pro workflow status --name "daily-monitoring"
```

### 工具脚本
```bash
# 设置定时任务
./tools/setup-cron.sh --mode basic
./tools/setup-cron.sh --mode full
./tools/setup-cron.sh --mode custom

# 查看定时任务
./tools/setup-cron.sh --list
./tools/setup-cron.sh --status

# 移除定时任务
./tools/setup-cron.sh --remove

# 生成日报
./tools/daily-report.sh --output reports/daily-$(date +%Y%m%d).md

# 发送邮件报告
python tools/send-email.py --config config/email-config.yaml --report reports/daily-20240428.md

# 快速启动
./tools/quick-start.sh
```

## ⚙️ 定时任务配置

### 基础监控模式
```bash
# 每5分钟检查集群健康
*/5 * * * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro elk health --quiet >> logs/health-$(date +\%Y\%m\%d).log 2>&1

# 每15分钟检查错误日志
*/15 * * * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro elk errors --time 15m --quiet >> logs/errors-$(date +\%Y\%m\%d).log 2>&1

# 每小时运行完整分析
0 * * * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro analyze --time 1h --output reports/hourly-$(date +\%Y\%m\%d_\%H).md >> logs/analyze-$(date +\%Y\%m\%d).log 2>&1

# 每天8点生成日报
0 8 * * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro report daily --time 24h --output reports/daily-$(date +\%Y\%m\%d).md >> logs/report-$(date +\%Y\%m\%d).log 2>&1
```

### 完整监控模式
```bash
# 包含基础监控所有任务
# 每30分钟性能分析
*/30 * * * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro elk performance --time 30m --quiet >> logs/performance-$(date +\%Y\%m\%d).log 2>&1

# 每6小时更新知识库
0 */6 * * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro knowledge update --auto >> logs/knowledge-$(date +\%Y\%m\%d).log 2>&1

# 每周一9点生成周报
0 9 * * 1 cd /path/to/log-analyzer-pro && ./log-analyzer-pro report weekly --time 7d --output reports/weekly-$(date +\%Y\%m\%d).md >> logs/report-$(date +\%Y\%m\%d).log 2>&1

# 每月1号10点生成月报
0 10 1 * * cd /path/to/log-analyzer-pro && ./log-analyzer-pro report monthly --time 30d --output reports/monthly-$(date +\%Y\%m).md >> logs/report-$(date +\%Y\%m).log 2>&1
```

## 🐛 故障排除

### 1. SSH连接失败
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

### 2. ELK连接失败
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

### 3. 分析结果不准确
```bash
# 检查错误模式配置
./log-analyzer-pro config show --section error_patterns

# 测试模式匹配
./log-analyzer-pro test pattern --log sample.log --pattern "OutOfMemory"

# 调整分析参数
./log-analyzer-pro analyze --target server01:syslog --time 2h --threshold 5
```

### 4. 知识库搜索无结果
```bash
# 重建知识库索引
./log-analyzer-pro knowledge rebuild-index

# 检查知识库文件
./log-analyzer-pro knowledge list --verbose

# 添加测试条目
./log-analyzer-pro knowledge add --title "测试问题" --category test --pattern "test pattern"
```

### 5. 调试模式
```bash
# 启用调试日志
LOG_LEVEL=DEBUG ./log-analyzer-pro analyze --target server01:syslog

# 保存调试信息
./log-analyzer-pro analyze --target server01:syslog --debug --debug-file debug.log

# 性能分析
./log-analyzer-pro analyze --target server01:syslog --profile --profile-file profile.json
```

## 📈 最佳实践

### 1. 监控策略
- **高频监控（5分钟）**: 关键服务健康状态
- **中频监控（15分钟）**: 错误日志检查
- **低频监控（1小时）**: 性能指标分析
- **定期报告（每天）**: 综合报告生成

### 2. 告警策略
- **立即告警**: 服务不可用、数据丢失
- **快速告警（5分钟）**: 性能下降、错误增加
- **日常告警（1小时）**: 趋势异常、容量预警
- **定期检查（每天）**: 配置变更、安全扫描

### 3. 知识管理
- 每个解决方案独立文档
- 包含问题描述、根因、解决方案、验证步骤
- 定期回顾和更新
- 建立分类索引和搜索

### 4. 团队协作
- 共享分析报告和解决方案
- 建立评审流程
- 定期知识分享
- 建立on-call轮值

## 🔄 更新日志

### v1.0.0 (2026-04-28)
- 初始版本发布
- 统一SSH和ELK日志分析
- 智能错误识别和根因分析
- 知识库驱动的解决方案推荐
- 多种报告格式支持
- 定时任务和告警集成

## 🤝 贡献指南

### 报告问题
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

## 📞 支持

### 文档
- 详细文档: `SKILL.md`
- 配置指南: `config/` 目录
- 示例文件: `examples/` 目录

### 社区
- 问题反馈: GitHub Issues
- 功能建议: GitHub Discussions
- 代码贡献: GitHub Pull Requests

### 联系方式
- 维护者: 运维助手 🔧
- 创建时间: 2026-04-28
- 版本: v1.0.0

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

---

**开始使用**: `./tools/quick-start.sh`

**查看帮助**: `./log-analyzer-pro --help`

**查看文档**: `cat SKILL.md | less`

**报告问题**: 创建GitHub Issue

**贡献代码**: 提交Pull Request