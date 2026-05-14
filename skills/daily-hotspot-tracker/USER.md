# USER.md - Daily Hotspot Tracker 用户指南

## 欢迎使用热点捕手！

感谢您选择**热点捕手**——您的科技数码热点智能助手。本指南将帮助您快速上手并充分利用本系统的所有功能。

## 🚀 快速开始

### 第一步：安装与配置
1. **安装依赖**：
   ```bash
   pip install requests
   ```

2. **初始化配置**：
   ```bash
   python daily_hotspot_tracker.py --init-config
   ```

3. **测试系统**：
   ```bash
   python daily_hotspot_tracker.py --test
   ```

### 第二步：个性化设置
1. **编辑配置文件**：
   - 打开 `hotspot_config.json`
   - 调整关键词、平台设置、通知方式等

2. **配置QQ通知**（可选）：
   - 选择通知方式（Server酱、PushPlus等）
   - 获取API密钥
   - 在配置文件中启用通知

### 第三步：启动监控
1. **手动运行**：
   ```bash
   python daily_hotspot_tracker.py --daemon
   ```

2. **设置定时任务**（推荐）：
   ```bash
   bash install_cron.sh
   ```

## 🎯 核心功能详解

### 1. 热点发现
- **监控平台**：微博、知乎、抖音、B站、百度、头条等8个平台
- **检查频率**：每5分钟一次（可配置）
- **关键词匹配**：200+科技数码关键词库

### 2. 智能分析
- **潜力评分**：S/A/B/C四级评分系统
- **评分维度**：
  - 热度分数（0-30分）
  - 排名分数（0-25分）
  - 关键词匹配（每个关键词5分）
  - 时效性分数（0-20分）
- **行动建议**：根据评分提供明确的创作建议

### 3. 内容生成
- **短内容**：适合微博/推特（150字内）
- **长文章**：适合知乎/公众号（2000字左右）
- **视频脚本**：适合抖音/B站（60-90秒）
- **轮播图**：适合小红书/Instagram

### 4. 实时提醒
- **QQ消息推送**：热点发现后立即通知
- **通知内容**：热点详情、潜力评分、行动建议
- **通知频率**：只推送高价值热点（可配置）

### 5. 数据分析
- **趋势报告**：每日热点趋势分析
- **平台统计**：各平台热点数量对比
- **关键词分析**：热门关键词统计
- **综合报告**：日报和趋势预测

## ⚙️ 配置说明

### 基本配置
```json
{
  "tech_keywords": ["苹果", "华为", "AI", "芯片"],
  "min_hot_value": 500000,
  "check_interval": 300,
  "qq_notification": false,
  "generate_draft": true
}
```

### 平台配置
```json
"platforms": {
  "weibo": {
    "enabled": true,
    "name": "微博",
    "check_interval": 1800
  },
  "zhihu": {
    "enabled": true,
    "name": "知乎", 
    "check_interval": 1800
  }
}
```

### 内容配置
```json
"content_categories": {
  "short_post": true,
  "long_article": true,
  "video_script": true,
  "carousel": true
}
```

## 📁 文件结构说明

### 配置文件
- `hotspot_config.json` - 主配置文件
- `hotspot_state.json` - 状态记录文件

### 输出目录
- `hotspot_content/` - 内容草稿
- `trend_reports/` - 趋势报告
- `comprehensive_reports/` - 综合报告
- `logs/` - 运行日志

### 脚本文件
- `daily_hotspot_tracker.py` - 主程序
- `setup_cron.py` - 定时任务设置
- `start_monitor.sh` - 启动脚本
- `stop_monitor.sh` - 停止脚本
- `test_monitor.sh` - 测试脚本

## 🔧 高级功能

### 自定义关键词
1. 编辑 `hotspot_config.json` 中的 `tech_keywords` 数组
2. 添加您关注的关键词
3. 系统会自动匹配包含这些关键词的热点

### 平台管理
1. 启用/禁用特定平台
2. 调整各平台的检查频率
3. 设置平台权重（影响评分）

### 通知定制
1. 选择通知方式（Server酱、PushPlus等）
2. 自定义通知模板
3. 设置通知阈值（只推送S/A级热点）

### 内容模板
1. 修改内容生成模板
2. 添加新的内容形式
3. 调整内容风格和格式

## 📊 数据分析

### 查看报告
```bash
# 查看最新趋势报告
ls -la trend_reports/

# 查看内容草稿
ls -la hotspot_content/

# 查看综合报告
ls -la comprehensive_reports/
```

### 分析日志
```bash
# 查看运行日志
tail -f logs/hotspot_monitor.log

# 查看匹配的热点
grep "发现匹配热点" logs/hotspot_monitor.log

# 查看错误信息
grep ERROR logs/hotspot_monitor.log
```

### 性能监控
```bash
# 查看系统状态
cat hotspot_state.json | python -m json.tool

# 查看统计信息
grep "统计" logs/hotspot_monitor.log
```

## 🐛 故障排除

### 常见问题

#### 1. 没有发现热点
- 检查关键词配置是否合适
- 调整 `min_hot_value` 降低热度阈值
- 确认平台是否启用
- 查看日志确认数据获取情况

#### 2. QQ通知未发送
- 确认 `qq_notification` 设置为 `true`
- 检查通知配置是否正确
- 查看网络连接是否正常
- 检查API密钥是否有效

#### 3. 系统运行缓慢
- 减少监控平台数量
- 增加检查间隔时间
- 清理旧的日志和报告文件
- 检查系统资源使用情况

#### 4. 内容生成不理想
- 调整关键词库
- 修改内容模板
- 调整评分阈值
- 增加个性化配置

### 日志分析
```bash
# 查看完整日志
cat logs/hotspot_monitor.log

# 查看特定平台的日志
grep "微博" logs/hotspot_monitor.log

# 查看错误详情
grep -A 5 -B 5 ERROR logs/hotspot_monitor.log
```

## 🔄 维护与更新

### 日常维护
1. **日志清理**：
   ```bash
   # 清理7天前的日志
   find logs/ -name "*.log" -mtime +7 -delete
   ```

2. **数据备份**：
   ```bash
   # 备份配置文件
   cp hotspot_config.json hotspot_config.json.backup
   cp hotspot_state.json hotspot_state.json.backup
   ```

3. **状态检查**：
   ```bash
   # 检查系统状态
   ps aux | grep daily_hotspot_tracker
   ```

### 系统更新
1. **备份当前配置**
2. **下载新版本**
3. **合并配置文件**
4. **测试新功能**
5. **正式上线**

### 性能优化
1. **调整检查频率**：根据需求调整 `check_interval`
2. **优化关键词**：定期更新关键词库
3. **清理历史数据**：定期清理旧的热点记录
4. **监控资源使用**：确保系统稳定运行

## 📈 最佳实践

### 内容创作流程
1. **接收提醒**：QQ消息推送热点信息
2. **查看详情**：点击链接查看热点详情
3. **选择角度**：根据内容建议选择创作角度
4. **快速创作**：使用生成的草稿快速创作
5. **发布优化**：根据平台特点优化内容
6. **效果跟踪**：监控内容传播效果

### 热点跟进策略
- **S级热点**：立即创作，抢占先机
- **A级热点**：尽快创作，争取流量
- **B级热点**：选择性创作，差异化角度
- **C级热点**：保持关注，等待时机

### 时间管理建议
- **黄金时间**：热点出现后2-4小时内
- **二次传播**：24小时后总结性内容
- **深度解读**：48小时后行业分析
- **长期跟踪**：持续关注热点发展

## 🤝 支持与反馈

### 获取帮助
1. **查看文档**：仔细阅读本指南
2. **检查日志**：查看错误信息和运行状态
3. **社区支持**：加入用户社区交流
4. **联系开发者**：提交Issue或邮件联系

### 反馈建议
1. **功能建议**：希望添加哪些新功能
2. **问题反馈**：遇到的bug和问题
3. **使用体验**：系统的易用性和稳定性
4. **改进意见**：如何让系统更好用

### 贡献代码
1. **Fork项目**
2. **创建分支**
3. **提交代码**
4. **发起PR**

## 📄 许可证与版权

### 许可证
MIT License - 详见 LICENSE 文件

### 版权声明
Copyright (c) 2026 Daily Hotspot Tracker Team

### 使用条款
1. 本系统仅供个人学习和研究使用
2. 请遵守各平台的使用条款
3. 尊重知识产权和版权
4. 不用于非法用途

---

**感谢使用热点捕手！**  
**愿您抢占每一个热点，创造更多价值！**