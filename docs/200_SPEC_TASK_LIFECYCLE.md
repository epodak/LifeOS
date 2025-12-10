# 任务生命周期自动化流程设计

## 场景：`life add 优化lifeOS` 后的完整流程

### 阶段 1：任务创建（已完成）
```
用户: life add 优化lifeOS
  ↓
CLI: 发布 task.created 事件
  ↓
后台 serve: 处理事件 → 创建 Task(id=1, title="优化lifeOS", status="pending")
```

### 阶段 2：任务分析（待实现）
```
后台 serve: 检测到新任务 → 发布 task.analyze 事件
  ↓
分析引擎 (Engines): 
  - 提取关键词: ["优化", "lifeOS", "系统"]
  - 分类: "开发/维护"
  - 优先级: "medium" (基于历史数据)
  - 相似任务检测: 发现任务 #5 "重构lifeOS架构" (相似度 0.75)
  ↓
发布 task.analyze.completed 事件（携带分析结果）
```

### 阶段 3：任务增强（待实现）
```
任务增强服务 (Services):
  - 更新任务元数据: tags=["优化", "开发"], category="开发/维护", priority="medium"
  - 关联相似任务: related_tasks=[5]
  - 建议截止日期: 基于历史完成时间预测
  ↓
发布 task.enhanced 事件
```

### 阶段 4：持续监控（待实现）
```
定时任务 (每 1 小时检查一次):
  - 检查 pending 任务
  - 如果任务创建超过 7 天未更新 → 发布 task.remind 事件
  - 如果任务创建超过 30 天未更新 → 发布 task.auto_archive 事件
  ↓
提醒服务: 处理 task.remind → 发送提醒（控制台/通知）
归档服务: 处理 task.auto_archive → 状态改为 "archived"
```

### 阶段 5：状态流转记录（待实现）
```
每次状态变更:
  - 记录 TaskTransition: from_status → to_status, timestamp, reason
  - 确保任务有明确的"结局"（done/dropped/archived）
```

## 事件类型清单

| 事件类型 | 来源 | 处理者 | 说明 |
|---------|------|--------|------|
| `task.created` | CLI/Collector | TaskService | 创建任务记录 |
| `task.analyze` | TaskService | AnalysisEngine | 分析任务内容 |
| `task.analyze.completed` | AnalysisEngine | TaskEnhancementService | 增强任务元数据 |
| `task.enhanced` | TaskEnhancementService | - | 任务增强完成 |
| `task.remind` | Scheduler | ReminderService | 提醒用户 |
| `task.auto_archive` | Scheduler | TaskService | 自动归档 |
| `task.status.changed` | TaskService | TransitionService | 记录状态流转 |

## 架构整合点

1. **Engines 层** (`life_system/engines/`):
   - `task_analyzer.py`: 任务分析引擎（关键词提取、分类、优先级）
   - `similarity_engine.py`: 相似度计算引擎

2. **Services 层** (`life_system/services/`):
   - `task_enhancement_service.py`: 任务增强服务
   - `reminder_service.py`: 提醒服务
   - `transition_service.py`: 状态流转记录服务

3. **Scheduler** (`life_system/services/scheduler.py`):
   - 添加定时检查 pending 任务
   - 触发提醒和归档逻辑

4. **Models** (`life_system/core/models.py`):
   - 扩展 Task 模型：添加 tags, priority, category, last_remind_at 等字段
   - 新增 TaskTransition 模型：记录状态流转历史

