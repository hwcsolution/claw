#!/usr/bin/env python3
"""
配置管理脚本
负责管理log-analyzer-pro的配置文件
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or SCRIPT_DIR.parent / "config")
        self.config_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.main_config_path = self.config_dir / "main-config.yaml"
        self.ssh_config_path = self.config_dir / "ssh-config.yaml"
        self.elk_config_path = self.config_dir / "elk-config.yaml"
        self.analysis_config_path = self.config_dir / "analysis-config.yaml"
        self.alert_config_path = self.config_dir / "alert-config.yaml"
        
        # 默认配置模板
        self.default_main_config = {
            "general": {
                "log_level": "INFO",
                "output_format": "text",
                "timezone": "Asia/Shanghai",
                "retention_days": 30
            },
            "ssh": {
                "config_file": "config/ssh-config.yaml",
                "default_user": "admin",
                "default_key": "~/.ssh/id_rsa",
                "connection_timeout": 30,
                "command_timeout": 300
            },
            "elk": {
                "config_file": "config/elk-config.yaml",
                "default_timeout": 30,
                "max_retries": 3,
                "verify_ssl": False
            },
            "analysis": {
                "config_file": "config/analysis-config.yaml",
                "default_time_range": "1h",
                "error_threshold": 10,
                "warning_threshold": 5
            },
            "knowledge": {
                "base_dir": "../knowledge-base",
                "auto_update": True,
                "search_backend": "simple"
            },
            "reporting": {
                "default_format": "markdown",
                "templates_dir": "templates",
                "auto_generate": True
            },
            "alerts": {
                "config_file": "config/alert-config.yaml",
                "enabled": True,
                "check_interval": 300
            },
            "scheduling": {
                "enabled": True,
                "config_file": "config/schedule-config.yaml"
            }
        }
        
        self.default_ssh_config = {
            "servers": {
                "example-server": {
                    "host": "192.168.1.100",
                    "port": 22,
                    "username": "admin",
                    "authentication": {
                        "type": "key",
                        "key_path": "~/.ssh/id_rsa",
                        "password": ""
                    },
                    "logs": [
                        {
                            "path": "/var/log/syslog",
                            "type": "system",
                            "parser": "syslog"
                        },
                        {
                            "path": "/var/log/nginx/error.log",
                            "type": "nginx_error",
                            "parser": "nginx"
                        }
                    ],
                    "commands": {
                        "health": "systemctl status nginx",
                        "disk": "df -h",
                        "memory": "free -m"
                    }
                }
            }
        }
        
        self.default_elk_config = {
            "elasticsearch": {
                "hosts": [
                    "http://localhost:9200",
                    "http://elk-prod-01:9200",
                    "http://elk-prod-02:9200"
                ],
                "authentication": {
                    "enabled": True,
                    "type": "basic",
                    "username": "elastic",
                    "password": "your_password_here"
                },
                "ssl": {
                    "enabled": False,
                    "ca_cert": "/path/to/ca.crt",
                    "client_cert": "/path/to/client.crt",
                    "client_key": "/path/to/client.key"
                },
                "connection": {
                    "timeout": 30,
                    "max_retries": 3,
                    "retry_on_timeout": True,
                    "sniff_on_start": True,
                    "sniff_on_connection_fail": True
                },
                "indices": {
                    "logs": "logstash-*",
                    "metrics": "metricbeat-*",
                    "application": "app-*"
                },
                "query": {
                    "default_size": 1000,
                    "max_size": 10000,
                    "scroll_time": "5m"
                }
            },
            "kibana": {
                "host": "http://kibana-prod:5601",
                "authentication": {
                    "enabled": True,
                    "username": "kibana_user",
                    "password": "your_password_here"
                }
            },
            "logstash": {
                "hosts": [
                    "logstash-prod:5044",
                    "logstash-prod:5000"
                ],
                "monitoring": {
                    "enabled": True,
                    "port": 9600
                }
            }
        }
        
        self.default_analysis_config = {
            "error_patterns": [
                {
                    "name": "out_of_memory",
                    "pattern": "OutOfMemoryError|java.lang.OutOfMemoryError",
                    "category": "system",
                    "severity": "CRITICAL",
                    "solution": "system/out-of-memory.json"
                },
                {
                    "name": "disk_full",
                    "pattern": "No space left on device|disk full",
                    "category": "system",
                    "severity": "CRITICAL",
                    "solution": "system/disk-full.json"
                },
                {
                    "name": "connection_refused",
                    "pattern": "Connection refused|Connection reset by peer",
                    "category": "network",
                    "severity": "ERROR",
                    "solution": "network/connection-refused.json"
                },
                {
                    "name": "timeout",
                    "pattern": "timeout|timed out|read timeout",
                    "category": "network",
                    "severity": "WARNING",
                    "solution": "network/timeout-error.json"
                },
                {
                    "name": "nginx_502",
                    "pattern": "502 Bad Gateway",
                    "category": "application",
                    "severity": "ERROR",
                    "solution": "application/nginx-502.json"
                },
                {
                    "name": "mysql_deadlock",
                    "pattern": "Deadlock found|Lock wait timeout exceeded",
                    "category": "database",
                    "severity": "ERROR",
                    "solution": "database/mysql-deadlock.json"
                }
            ],
            "analysis_rules": {
                "time_windows": [
                    {"name": "last_hour", "value": "1h"},
                    {"name": "last_6_hours", "value": "6h"},
                    {"name": "last_24_hours", "value": "24h"},
                    {"name": "last_7_days", "value": "7d"}
                ],
                "thresholds": {
                    "critical_errors": 10,
                    "warning_errors": 5,
                    "error_increase_rate": 2.0
                },
                "correlation": {
                    "enabled": True,
                    "time_window": "5m",
                    "min_correlation": 0.7
                },
                "root_cause": {
                    "enabled": True,
                    "max_depth": 3,
                    "include_timeline": True
                }
            },
            "reporting": {
                "templates": {
                    "daily": "templates/daily-report.md.j2",
                    "weekly": "templates/weekly-report.html.j2",
                    "incident": "templates/incident-report.md.j2"
                },
                "charts": {
                    "enabled": True,
                    "type": "matplotlib",
                    "theme": "dark",
                    "output_format": "png"
                },
                "notifications": {
                    "email": {
                        "enabled": True,
                        "template": "templates/email-notification.md.j2"
                    },
                    "feishu": {
                        "enabled": False,
                        "webhook": ""
                    },
                    "slack": {
                        "enabled": False,
                        "webhook": ""
                    }
                }
            }
        }
        
        self.default_alert_config = {
            "alerts": {
                "cluster_health": {
                    "enabled": True,
                    "conditions": [
                        {
                            "field": "cluster_health.status",
                            "operator": "!=",
                            "value": "green",
                            "severity": "CRITICAL"
                        }
                    ],
                    "actions": [
                        {
                            "type": "email",
                            "recipients": ["admin@example.com"]
                        },
                        {
                            "type": "feishu",
                            "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
                        }
                    ]
                },
                "error_count": {
                    "enabled": True,
                    "conditions": [
                        {
                            "field": "error_analysis.total_errors",
                            "operator": ">",
                            "value": 10,
                            "severity": "WARNING"
                        },
                        {
                            "field": "error_analysis.total_errors",
                            "operator": ">",
                            "value": 50,
                            "severity": "ERROR"
                        }
                    ],
                    "actions": [
                        {
                            "type": "email",
                            "recipients": ["team@example.com"]
                        }
                    ]
                },
                "performance": {
                    "enabled": True,
                    "conditions": [
                        {
                            "field": "performance.query_latency.p95",
                            "operator": ">",
                            "value": 1000,
                            "severity": "WARNING"
                        },
                        {
                            "field": "performance.cpu_usage.avg",
                            "operator": ">",
                            "value": 80,
                            "severity": "WARNING"
                        }
                    ],
                    "actions": [
                        {
                            "type": "email",
                            "recipients": ["sre@example.com"]
                        }
                    ]
                }
            }
        }
    
    def init_config(self, force: bool = False) -> bool:
        """初始化配置文件"""
        try:
            configs = [
                (self.main_config_path, self.default_main_config, "主配置"),
                (self.ssh_config_path, self.default_ssh_config, "SSH配置"),
                (self.elk_config_path, self.default_elk_config, "ELK配置"),
                (self.analysis_config_path, self.default_analysis_config, "分析配置"),
                (self.alert_config_path, self.default_alert_config, "告警配置")
            ]
            
            for config_path, default_config, config_name in configs:
                if config_path.exists() and not force:
                    print(f"⚠️  {config_name}文件已存在: {config_path}")
                    continue
                
                # 确保目录存在
                config_path.parent.mkdir(exist_ok=True, parents=True)
                
                # 写入配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True, indent=2)
                
                print(f"✅ 已创建{config_name}文件: {config_path}")
            
            # 创建模板目录
            templates_dir = self.config_dir.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            
            # 创建示例模板
            daily_template = templates_dir / "daily-report.md.j2"
            if not daily_template.exists():
                daily_template.write_text("""# 日报 - {{ date }}

## 概览
- 分析时间: {{ analysis_time }}
- 数据源: {{ data_source }}
- 总日志数: {{ total_logs }}
- 错误数量: {{ error_count }}
- 警告数量: {{ warning_count }}

## 集群健康状态
{% if cluster_health %}
### Elasticsearch集群
- 状态: {{ cluster_health.status }}
- 节点数: {{ cluster_health.nodes }}
- 分片数: {{ cluster_health.shards }}
- 未分配分片: {{ cluster_health.unassigned_shards }}

### 节点状态
{% for node in nodes %}
- {{ node.name }}: CPU {{ node.cpu }}%, 内存 {{ node.ram }}%, 堆内存 {{ node.heap }}%
{% endfor %}
{% endif %}

## 错误分析
{% if errors %}
### 关键错误 ({{ errors.critical|length }})
{% for error in errors.critical %}
- **{{ error.timestamp }}** - {{ error.message }}
  - 服务器: {{ error.host }}
  - 服务: {{ error.service }}
  - 建议: {{ error.suggestion }}
{% endfor %}

### 一般错误 ({{ errors.normal|length }})
{% for error in errors.normal %}
- {{ error.timestamp }} - {{ error.message }} ({{ error.host }})
{% endfor %}
{% else %}
未发现错误
{% endif %}

## 性能指标
{% if performance %}
### 查询性能
- 平均响应时间: {{ performance.query_latency.avg }}ms
- P95响应时间: {{ performance.query_latency.p95 }}ms
- P99响应时间: {{ performance.query_latency.p99 }}ms

### 资源使用
- CPU使用率: {{ performance.cpu_usage.avg }}%
- 内存使用率: {{ performance.memory_usage.avg }}%
- 磁盘使用率: {{ performance.disk_usage.avg }}%
{% endif %}

## 知识库匹配
{% if knowledge_matches %}
### 匹配的解决方案 ({{ knowledge_matches|length }})
{% for match in knowledge_matches %}
- **{{ match.title }}** ({{ match.category }})
  - 匹配度: {{ match.score }}%
  - 解决方案: {{ match.solution }}
{% endfor %}
{% endif %}

## 建议
{% if suggestions %}
{% for suggestion in suggestions %}
- {{ suggestion }}
{% endfor %}
{% else %}
无特殊建议
{% endif %}

---
*报告生成时间: {{ generated_at }}*
*分析工具: log-analyzer-pro*
""")
                print(f"✅ 已创建日报模板: {daily_template}")
            
            print("\n🎉 配置初始化完成！")
            print("请编辑以下配置文件以适配您的环境：")
            print(f"  1. {self.ssh_config_path} - SSH服务器配置")
            print(f"  2. {self.elk_config_path} - ELK集群配置")
            print(f"  3. {self.alert_config_path} - 告警配置")
            
            return True
            
        except Exception as e:
            print(f"❌ 配置初始化失败: {e}")
            return False
    
    def show_config(self, config_type: str = "all") -> bool:
        """显示配置"""
        try:
            config_files = {
                "main": self.main_config_path,
                "ssh": self.ssh_config_path,
                "elk": self.elk_config_path,
                "analysis": self.analysis_config_path,
                "alert": self.alert_config_path
            }
            
            if config_type == "all":
                files_to_show = config_files.values()
            elif config_type in config_files:
                files_to_show = [config_files[config_type]]
            else:
                print(f"❌ 未知的配置类型: {config_type}")
                print(f"可用类型: {', '.join(config_files.keys())}")
                return False
            
            for config_file in files_to_show:
                if not config_file.exists():
                    print(f"⚠️  配置文件不存在: {config_file}")
                    continue
                
                print(f"\n{'='*60}")
                print(f"配置文件: {config_file}")
                print(f"{'='*60}")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
            
            return True
            
        except Exception as e:
            print(f"❌ 显示配置失败: {e}")
            return False
    
    def edit_config(self, config_type: str) -> bool:
        """编辑配置"""
        try:
            config_files = {
                "main": self.main_config_path,
                "ssh": self.ssh_config_path,
                "elk": self.elk_config_path,
                "analysis": self.analysis_config_path,
                "alert": self.alert_config_path
            }
            
            if config_type not in config_files:
                print(f"❌ 未知的配置类型: {config_type}")
                print(f"可用类型: {', '.join(config_files.keys())}")
                return False
            
            config_file = config_files[config_type]
            
            if not config_file.exists():
                print(f"⚠️  配置文件不存在: {config_file}")
                response = input("是否创建该配置文件？(y/n): ")
                if response.lower() == 'y':
                    return self.init_config(force=True)
                else:
                    return False
            
            # 获取编辑器
            editor = os.environ.get('EDITOR', 'vi')
            
            # 编辑文件
            os.system(f"{editor} {config_file}")
            
            print(f"✅ 已编辑配置文件: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 编辑配置失败: {e}")
            return False
    
    def validate_config(self, config_type: str = "all") -> bool:
        """验证配置"""
        try:
            config_files = {
                "main": (self.main_config_path, self.default_main_config),
                "ssh": (self.ssh_config_path, self.default_ssh_config),
                "elk": (self.elk_config_path, self.default_elk_config),
                "analysis": (self.analysis_config_path, self.default_analysis_config),
                "alert": (self.alert_config_path, self.default_alert_config)
            }
            
            if config_type == "all":
                files_to_validate = config_files.items()
            elif config_type in config_files:
                files_to_validate = [(config_type, config_files[config_type])]
            else:
                print(f"❌ 未知的配置类型: {config_type}")
                print(f"可用类型: {', '.join(config_files.keys())}")
                return False
            
            all_valid = True
            
            for name, (config_file, default_config) in files_to_validate:
                if not config_file.exists():
                    print(f"❌ 配置文件不存在: {config_file}")
                    all_valid = False
                    continue
                
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    
                    # 基本验证
                    if not config:
                        print(f"❌ 配置文件为空: {config_file}")
                        all_valid = False
                        continue
                    
                    # 检查必需字段
                    required_fields = self._get_required_fields(name)
                    missing_fields = []
                    
                    for field in required_fields:
                        if not self._check_field_exists(config, field):
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print(f"❌ 配置文件 {name} 缺少必需字段: {', '.join(missing_fields)}")
                        all_valid = False
                    else:
                        print(f"✅ 配置文件 {name} 验证通过")
                        
                        # 显示配置摘要
                        self._show_config_summary(name, config)
                
                except yaml.YAMLError as e:
                    print(f"❌ 配置文件 {name} YAML格式错误: {e}")
                    all_valid = False
                except Exception as e:
                    print(f"❌ 验证配置文件 {name} 失败: {e}")
                    all_valid = False
            
            return all_valid
            
        except Exception as e:
            print(f"❌ 验证配置失败: {e}")
            return False
    
    def backup_config(self, backup_dir: str = None) -> bool:
        """备份配置"""
        try:
            backup_dir = Path(backup_dir or self.config_dir.parent / "backups" / "config")
            backup_dir.mkdir(exist_ok=True, parents=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"config_backup_{timestamp}.tar.gz"
            
            import tarfile
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for config_file in self.config_dir.glob("*.yaml"):
                    tar.add(config_file, arcname=config_file.name)
            
            print(f"✅ 配置已备份到: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ 备份配置失败: {e}")
            return False
    
    def restore_config(self, backup_file: str) -> bool:
        """恢复配置"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                print(f"❌ 备份文件不存在: {backup_file}")
                return False
            
            import tarfile
            import shutil
            
            # 备份当前配置
            self.backup_config()
            
            # 恢复配置
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(self.config_dir)
            
            print(f"✅ 配置已从 {backup_file} 恢复")
            return True
            
        except Exception as e:
            print(f"❌ 恢复配置失败: {e}")
            return False
    
    def _get_required_fields(self, config_type: str) -> list:
        """获取必需字段"""
        required_fields = {
            "main": ["general", "ssh", "elk", "analysis", "knowledge"],
            "ssh": ["servers"],
            "elk": ["elasticsearch"],
            "analysis": ["error_patterns", "analysis_rules"],
            "alert": ["alerts"]
        }
        
        return required_fields.get(config_type, [])
    
    def _check_field_exists(self, config: dict, field_path: str) -> bool:
        """检查字段是否存在"""
        try:
            parts = field_path.split('.')
            current = config
            
            for part in parts:
                if part not in current:
                    return False
                current = current[part]
            
            return True
        except:
            return False
    
    def _show_config_summary(self, config_type: str, config: dict):
        """显示配置摘要"""
        if config_type == "ssh":
            servers = config.get("servers", {})
            print(f"   配置了 {len(servers)} 个服务器")
            for server_name in servers:
                print(f"   - {server_name}")
        
        elif config_type == "elk":
            hosts = config.get("elasticsearch", {}).get("hosts", [])
            print(f"   配置了 {len(hosts)} 个Elasticsearch节点")
            for host in hosts[:3]:  # 只显示前3个
                print(f"   - {host}")
            if len(hosts) > 3:
                print(f"   - ... 和 {len(hosts) - 3} 个更多节点")
        
        elif config_type == "analysis":
            patterns = config.get("error_patterns", [])
            print(f"   配置了 {len(patterns)} 个错误模式")
        
        elif config_type == "alert":
            alerts = config.get("alerts", {})
            print(f"   配置了 {len(alerts)} 个告警规则")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="log-analyzer-pro 配置管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化配置")
    init_parser.add_argument("--force", action="store_true", help="强制覆盖现有配置")
    
    # show 命令
    show_parser = subparsers.add_parser("show", help="显示配置")
    show_parser.add_argument("type", nargs="?", default="all", 
                           choices=["all", "main", "ssh", "elk", "analysis", "alert"],
                           help="配置类型")
    
    # edit 命令
    edit_parser = subparsers.add_parser("edit", help="编辑配置")
    edit_parser.add_argument("type", 
                           choices=["main", "ssh", "elk", "analysis", "alert"],
                           help="配置类型")
    
    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证配置")
    validate_parser.add_argument("type", nargs="?", default="all",
                               choices=["all", "main", "ssh", "elk", "analysis", "alert"],
                               help="配置类型")
    
    # backup 命令
    backup_parser = subparsers.add_parser("backup", help="备份配置")
    backup_parser.add_argument("--dir", help="备份目录")
    
    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复配置")
    restore_parser.add_argument("file", help="备份文件路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config_manager = ConfigManager()
    
    if args.command == "init":
        success = config_manager.init_config(force=args.force)
        sys.exit(0 if success else 1)
    
    elif args.command == "show":
        success = config_manager.show_config(args.type)
        sys.exit(0 if success else 1)
    
    elif args.command == "edit":
        success = config_manager.edit_config(args.type)
        sys.exit(0 if success else 1)
    
    elif args.command == "validate":
        success = config_manager.validate_config(args.type)
        sys.exit(0 if success else 1)
    
    elif args.command == "backup":
        success = config_manager.backup_config(args.dir)
        sys.exit(0 if success else 1)
    
    elif args.command == "restore":
        success = config_manager.restore_config(args.file)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    from datetime import datetime
    main()