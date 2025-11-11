# 对话历史查看功能使用指南

## 新增功能概览

✅ **已实现**：
1. `/history` - 查看当前会话的对话历史
2. `/sessions` - 列出所有会话
3. 自动持久化 - 对话自动保存
4. 自动恢复 - 重启后无缝继续

## 功能详细说明

### 1. `/history` - 查看对话历史

**功能**：显示当前会话的对话记录

**使用方法**：
```
> /history
```

**显示内容**：
- 当前 thread_id
- 总 checkpoint 数量
- 最近 10 个 checkpoint
- 每个 checkpoint 的最后 3 条消息
- 消息角色着色（用户=蓝色，助手=绿色）
- 长消息自动截断（>100 字符）

**输出示例**：
```
📝 Conversation History

Found 15 checkpoints in current thread
Thread ID: main

Checkpoint 1 (ID: 1f4e7a8b...)
  👤 User: 你好，我叫张三
  🤖 Assistant: 你好张三！很高兴认识你。有什么我可以帮助你的吗？
  👤 User: 查询00700的最新公告

Checkpoint 2 (ID: 2a5f8c9d...)
  🤖 Assistant: 正在为您查询腾讯控股（00700）的最新公告...
  ...

... and 5 more checkpoints
Showing most recent 10 checkpoints

💡 Tip: Use /clear to start a new conversation thread
```

### 2. `/sessions` - 列出所有会话

**功能**：显示所有保存的对话会话

**使用方法**：
```
> /sessions
```

**显示内容**：
- 会话总数
- 每个会话的 thread_id
- 每个会话的 checkpoint 数量
- 当前活动会话标记（→）

**输出示例**：
```
📚 All Conversation Sessions

Found 3 session(s)

→ main
   12 checkpoints
   (current session)

  main-1731350400
   8 checkpoints

  main-1731336000
   5 checkpoints

💡 Tip: Use /clear to create a new session
💡 Use /history to view current session's messages
```

### 3. `/clear` - 开始新会话

**功能**：清屏并创建新的对话会话

**使用方法**：
```
> /clear
```

**效果**：
- 清空屏幕
- 创建新 thread_id（格式：`main-{timestamp}`）
- 历史对话保留在数据库中
- 可通过 `/sessions` 查看所有会话

### 4. 自动持久化和恢复

**持久化**：
- 每次对话自动保存到 SQLite 数据库
- 位置：`~/.hkex-agent/default/checkpoints.db`
- 无需手动操作

**自动恢复**：
- 重启程序后自动恢复上次对话
- 直接继续之前的会话
- 无缝体验

## 使用场景示例

### 场景 1：长期项目跟踪

```bash
# Day 1
> 分析00700的财务状况
[深入对话...]

# 退出
> /quit

# Day 2（重启后）
> 继续昨天的分析，生成报告
[Agent 记得昨天的内容，直接继续]

# 查看历史
> /history
[看到所有对话记录]
```

### 场景 2：多任务管理

```bash
# 任务 1：分析腾讯
> 分析00700
[对话...]

# 切换任务
> /clear

# 任务 2：分析阿里
> 分析09988
[对话...]

# 查看所有任务
> /sessions
[显示两个会话]

# 查看当前任务历史
> /history
[只显示 09988 的对话]
```

### 场景 3：回顾和总结

```bash
# 经过多天的研究...
> /sessions
[看到所有研究会话]

> /history
[查看当前会话的所有讨论]

> 基于我们之前的所有讨论，生成一份总结报告
[Agent 基于历史生成报告]
```

## 技术细节

### 数据存储

**位置**：
```
~/.hkex-agent/
└── default/
    └── checkpoints.db  # SQLite 数据库
```

**数据库结构**：
- `thread_id`: 会话标识符
- `checkpoint_id`: 每个检查点的唯一 ID
- `messages`: 对话消息（序列化）
- 其他状态数据

### Thread ID 管理

**默认 Thread**：`main`

**新 Thread 格式**：`main-{timestamp}`
- 使用 Unix 时间戳确保唯一性
- 例如：`main-1731350400`

**当前 Thread 跟踪**：
- 存储在环境变量：`HKEX_CURRENT_THREAD_ID`
- `/clear` 命令更新此变量

### 性能考虑

**显示限制**：
- 最多显示 10 个 checkpoint（避免输出过长）
- 每个 checkpoint 最多显示 3 条消息
- 消息截断至 100 字符

**数据库查询**：
- 直接 SQL 查询（高效）
- 按时间排序（最新在前）
- 连接即用即关（无资源泄漏）

## 已知限制

### 当前版本限制

1. **无法切换会话**
   - 只能查看，不能切换到历史会话
   - 需要手动重启并设置 thread_id（高级用法）

2. **无法搜索历史**
   - 不支持关键词搜索
   - 需要手动浏览

3. **无法导出**
   - 不能导出对话为文件
   - 需要直接查询数据库

4. **显示限制**
   - 固定显示最近 10 个 checkpoint
   - 不支持动态分页或查看更多

### 后续计划（未来版本）

- [ ] `/session <id>` - 切换到指定会话
- [ ] `/search <keyword>` - 搜索历史对话
- [ ] `/export [format]` - 导出对话（txt/md/json）
- [ ] 分页浏览（`/history --page 2`）
- [ ] 删除会话（`/delete <session_id>`）
- [ ] 会话重命名
- [ ] 会话标签和分类

## 故障排查

### 问题 1：/history 显示"No conversation history"

**原因**：尚未开始对话或 checkpointer 未配置

**解决**：
1. 进行至少一轮对话
2. 检查数据库文件是否存在：`ls -lh ~/.hkex-agent/default/checkpoints.db`

### 问题 2：/sessions 显示空列表

**原因**：数据库为空或未创建

**解决**：
1. 进行对话创建第一个 checkpoint
2. 等待程序自动保存

### 问题 3：重启后没有自动恢复

**原因**：thread_id 变更或数据库损坏

**解决**：
1. 检查环境变量：`echo $HKEX_CURRENT_THREAD_ID`
2. 查看 `/sessions` 确认会话存在
3. 检查数据库文件完整性

### 问题 4：历史消息显示不完整

**原因**：超过显示限制（10 个 checkpoint）

**说明**：
- 这是设计行为，防止输出过长
- 所有数据仍保存在数据库中
- 可以直接查询数据库获取完整历史

## 高级用法

### 直接查询数据库

如果需要查看完整历史或进行复杂查询：

```bash
# 进入数据库
sqlite3 ~/.hkex-agent/default/checkpoints.db

# 查看所有表
.tables

# 查看 checkpoint 数量
SELECT COUNT(*) FROM checkpoints;

# 查看所有 thread
SELECT DISTINCT thread_id FROM checkpoints;

# 查看特定 thread 的 checkpoint
SELECT checkpoint_id, thread_id FROM checkpoints 
WHERE thread_id = 'main' 
ORDER BY checkpoint_id DESC;

# 退出
.exit
```

### 手动切换 Thread

```bash
# 导出特定 thread_id
export HKEX_CURRENT_THREAD_ID="main-1731350400"

# 启动程序
hkex

# 现在使用指定的 thread
```

## 最佳实践

### 1. 定期查看历史

```bash
# 每天工作结束前
> /history
[回顾今天的讨论]

> /sessions
[确认所有任务都有记录]
```

### 2. 任务隔离

```bash
# 重要任务使用独立会话
> /clear  # 开始新任务

# 完成后标记
> 这个任务已完成，记录为：腾讯分析 2025-01-11
```

### 3. 定期清理

```bash
# 查看所有会话
> /sessions

# 对于不再需要的会话，可以手动删除数据库记录
# （未来版本将支持 /delete 命令）
```

## 数据管理

### 备份

```bash
# 备份数据库
cp ~/.hkex-agent/default/checkpoints.db ~/backup/checkpoints-$(date +%Y%m%d).db
```

### 恢复

```bash
# 从备份恢复
cp ~/backup/checkpoints-20250111.db ~/.hkex-agent/default/checkpoints.db
```

### 清理

```bash
# 完全重置（删除所有历史）
rm ~/.hkex-agent/default/checkpoints.db

# 程序会自动创建新数据库
```

## 总结

✅ **完整功能**：
- 自动持久化和恢复
- 查看对话历史（`/history`）
- 列出所有会话（`/sessions`）
- 创建新会话（`/clear`）

✅ **用户体验**：
- 零学习成本（自动工作）
- 直观的命令
- 清晰的输出格式
- 有用的提示信息

✅ **技术实现**：
- SQLite 数据库
- AsyncSqliteSaver
- 自动 checkpoint 管理
- 高效的查询

---

**版本**：v0.3.0  
**更新日期**：2025-01-11  
**文档状态**：✅ 完成

