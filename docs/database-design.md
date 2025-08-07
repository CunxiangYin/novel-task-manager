# 数据库设计文档 - 小说处理任务管理系统

## 1. 概述

本文档定义了小说处理任务管理系统的数据库结构设计，用于持久化存储任务信息、处理状态和结果数据。

## 2. 数据库选择

推荐使用 **PostgreSQL** 作为主数据库，原因如下：
- 支持 JSON 数据类型，便于存储灵活的元数据
- 优秀的并发处理能力
- 支持事务和数据完整性
- 便于横向扩展

## 3. 表结构设计

### 3.1 任务表 (tasks)

存储所有任务的基本信息和处理状态。

```sql
CREATE TABLE tasks (
    -- 主键
    id VARCHAR(50) PRIMARY KEY,                    -- 任务唯一标识符 (如: task-1234567890-abc123)
    
    -- 文件信息
    file_name VARCHAR(255) NOT NULL,               -- 文件名
    file_size BIGINT NOT NULL,                     -- 文件大小（字节）
    file_type VARCHAR(50) DEFAULT 'text/plain',    -- 文件MIME类型
    file_hash VARCHAR(64),                         -- 文件SHA256哈希值（用于去重）
    
    -- 任务状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 状态: pending, processing, completed, failed
    progress INTEGER DEFAULT 0,                    -- 进度百分比 (0-100)
    priority INTEGER DEFAULT 0,                    -- 优先级（数值越大优先级越高）
    
    -- 时间戳
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 上传时间
    started_at TIMESTAMP,                          -- 开始处理时间
    completed_at TIMESTAMP,                        -- 完成时间
    
    -- 结果信息
    result_url TEXT,                               -- 结果文件URL
    error_message TEXT,                            -- 错误信息
    
    -- 用户信息
    user_id VARCHAR(50),                           -- 用户ID（预留字段）
    session_id VARCHAR(100),                       -- 会话ID（用于临时用户）
    
    -- 元数据
    metadata JSONB,                                -- 额外的元数据（JSON格式）
    
    -- 索引优化
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CONSTRAINT chk_status CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    CONSTRAINT chk_progress CHECK (progress >= 0 AND progress <= 100)
);

-- 创建索引
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_session_id ON tasks(session_id);
CREATE INDEX idx_tasks_uploaded_at ON tasks(uploaded_at DESC);
CREATE INDEX idx_tasks_file_hash ON tasks(file_hash);
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC) WHERE status = 'pending';
```

### 3.2 任务日志表 (task_logs)

记录任务处理过程中的详细日志。

```sql
CREATE TABLE task_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    log_level VARCHAR(20) NOT NULL,                -- 日志级别: info, warning, error, debug
    message TEXT NOT NULL,                         -- 日志消息
    details JSONB,                                 -- 详细信息（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_task_logs_task_id ON task_logs(task_id);
CREATE INDEX idx_task_logs_created_at ON task_logs(created_at DESC);
```

### 3.3 处理结果表 (task_results)

存储任务处理的详细结果。

```sql
CREATE TABLE task_results (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL UNIQUE,
    
    -- 结果文件信息
    result_file_path TEXT,                         -- 结果文件路径
    result_file_size BIGINT,                       -- 结果文件大小
    result_file_type VARCHAR(50),                  -- 结果文件类型
    
    -- 处理统计
    processing_time_ms INTEGER,                    -- 处理耗时（毫秒）
    tokens_processed INTEGER,                      -- 处理的token数量
    
    -- 结果数据
    summary TEXT,                                  -- 处理结果摘要
    full_content TEXT,                             -- 完整处理内容
    
    -- 质量指标
    quality_score DECIMAL(3,2),                    -- 质量评分 (0.00-1.00)
    confidence_score DECIMAL(3,2),                 -- 置信度评分 (0.00-1.00)
    
    -- 元数据
    metadata JSONB,                                -- 额外的结果元数据
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_task_results_task_id ON task_results(task_id);
```

### 3.4 任务队列表 (task_queue)

用于管理任务处理队列，支持分布式处理。

```sql
CREATE TABLE task_queue (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL UNIQUE,
    
    -- 队列管理
    queue_position INTEGER NOT NULL,               -- 队列位置
    assigned_worker VARCHAR(100),                  -- 分配的处理器ID
    assigned_at TIMESTAMP,                         -- 分配时间
    
    -- 重试机制
    retry_count INTEGER DEFAULT 0,                 -- 重试次数
    max_retries INTEGER DEFAULT 3,                 -- 最大重试次数
    next_retry_at TIMESTAMP,                       -- 下次重试时间
    
    -- 超时控制
    timeout_seconds INTEGER DEFAULT 300,           -- 超时时间（秒）
    expires_at TIMESTAMP,                          -- 过期时间
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_task_queue_position ON task_queue(queue_position);
CREATE INDEX idx_task_queue_assigned_worker ON task_queue(assigned_worker);
CREATE INDEX idx_task_queue_task_id ON task_queue(task_id);
```

### 3.5 文件存储表 (file_storage)

管理上传文件的存储信息。

```sql
CREATE TABLE file_storage (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    
    -- 存储位置
    storage_type VARCHAR(20) NOT NULL,             -- 存储类型: local, s3, oss
    storage_path TEXT NOT NULL,                    -- 存储路径
    storage_url TEXT,                               -- 访问URL
    
    -- 文件信息
    original_name VARCHAR(255) NOT NULL,           -- 原始文件名
    stored_name VARCHAR(255) NOT NULL,             -- 存储文件名
    content_type VARCHAR(100),                     -- 内容类型
    file_size BIGINT NOT NULL,                     -- 文件大小
    checksum VARCHAR(64),                          -- 文件校验和
    
    -- 状态
    is_deleted BOOLEAN DEFAULT FALSE,              -- 是否已删除
    deleted_at TIMESTAMP,                          -- 删除时间
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,                          -- 过期时间（用于临时文件）
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_file_storage_task_id ON file_storage(task_id);
CREATE INDEX idx_file_storage_is_deleted ON file_storage(is_deleted);
CREATE INDEX idx_file_storage_expires_at ON file_storage(expires_at);
```

## 4. 视图设计

### 4.1 任务概览视图

```sql
CREATE VIEW v_task_overview AS
SELECT 
    t.id,
    t.file_name,
    t.file_size,
    t.status,
    t.progress,
    t.uploaded_at,
    t.started_at,
    t.completed_at,
    t.result_url,
    t.error_message,
    CASE 
        WHEN t.status = 'completed' THEN 
            EXTRACT(EPOCH FROM (t.completed_at - t.started_at)) * 1000
        ELSE NULL 
    END AS processing_time_ms,
    tr.quality_score,
    tr.confidence_score
FROM tasks t
LEFT JOIN task_results tr ON t.id = tr.task_id
ORDER BY t.uploaded_at DESC;
```

### 4.2 队列状态视图

```sql
CREATE VIEW v_queue_status AS
SELECT 
    COUNT(*) FILTER (WHERE t.status = 'pending') AS pending_count,
    COUNT(*) FILTER (WHERE t.status = 'processing') AS processing_count,
    COUNT(*) FILTER (WHERE t.status = 'completed') AS completed_count,
    COUNT(*) FILTER (WHERE t.status = 'failed') AS failed_count,
    COUNT(*) AS total_count,
    AVG(t.progress) FILTER (WHERE t.status = 'processing') AS avg_progress
FROM tasks t;
```

## 5. 存储过程和函数

### 5.1 更新任务进度

```sql
CREATE OR REPLACE FUNCTION update_task_progress(
    p_task_id VARCHAR(50),
    p_progress INTEGER
)
RETURNS VOID AS $$
BEGIN
    UPDATE tasks 
    SET 
        progress = p_progress,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_task_id;
    
    -- 记录日志
    INSERT INTO task_logs (task_id, log_level, message, details)
    VALUES (
        p_task_id, 
        'info', 
        'Progress updated',
        jsonb_build_object('progress', p_progress)
    );
END;
$$ LANGUAGE plpgsql;
```

### 5.2 获取下一个待处理任务

```sql
CREATE OR REPLACE FUNCTION get_next_pending_task(
    p_worker_id VARCHAR(100)
)
RETURNS TABLE(task_id VARCHAR(50)) AS $$
BEGIN
    RETURN QUERY
    WITH next_task AS (
        SELECT t.id
        FROM tasks t
        LEFT JOIN task_queue tq ON t.id = tq.task_id
        WHERE t.status = 'pending'
        AND (tq.assigned_worker IS NULL OR tq.expires_at < CURRENT_TIMESTAMP)
        ORDER BY t.priority DESC, t.uploaded_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    UPDATE tasks t
    SET 
        status = 'processing',
        started_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    FROM next_task nt
    WHERE t.id = nt.id
    RETURNING t.id;
    
    -- 更新队列信息
    UPDATE task_queue
    SET 
        assigned_worker = p_worker_id,
        assigned_at = CURRENT_TIMESTAMP,
        expires_at = CURRENT_TIMESTAMP + INTERVAL '5 minutes'
    WHERE task_id IN (SELECT task_id FROM next_task);
END;
$$ LANGUAGE plpgsql;
```

## 6. 数据库迁移策略

### 6.1 初始化脚本

```sql
-- 创建数据库
CREATE DATABASE novel_task_manager
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    CONNECTION LIMIT = -1;

-- 创建schema
CREATE SCHEMA IF NOT EXISTS task_manager;

-- 设置默认schema
SET search_path TO task_manager, public;
```

### 6.2 版本控制

使用数据库迁移工具（如 Flyway 或 Liquibase）管理数据库版本：

```sql
CREATE TABLE schema_version (
    version VARCHAR(20) PRIMARY KEY,
    description VARCHAR(255),
    installed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version, description) 
VALUES ('1.0.0', 'Initial schema creation');
```

## 7. 性能优化建议

### 7.1 分区策略

对于大量数据，可以按时间对 tasks 表进行分区：

```sql
-- 按月分区
CREATE TABLE tasks_2024_01 PARTITION OF tasks
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 7.2 定期维护

```sql
-- 定期清理已完成的旧任务
DELETE FROM tasks 
WHERE status = 'completed' 
AND completed_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

-- 定期分析和重建索引
ANALYZE tasks;
REINDEX TABLE tasks;
```

### 7.3 连接池配置

- 最小连接数：5
- 最大连接数：20
- 连接超时：30秒
- 空闲超时：10分钟

## 8. 备份策略

### 8.1 备份计划

- **全量备份**：每天凌晨 2:00
- **增量备份**：每 6 小时
- **事务日志备份**：每 15 分钟

### 8.2 备份脚本

```bash
#!/bin/bash
# 全量备份
pg_dump -h localhost -U postgres -d novel_task_manager \
    -f /backup/novel_task_manager_$(date +%Y%m%d_%H%M%S).sql

# 保留最近30天的备份
find /backup -name "novel_task_manager_*.sql" -mtime +30 -delete
```

## 9. 监控指标

### 9.1 关键性能指标 (KPI)

- 平均任务处理时间
- 任务成功率
- 队列长度
- 并发处理数

### 9.2 监控查询

```sql
-- 过去1小时的任务统计
SELECT 
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_tasks,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_processing_seconds
FROM tasks
WHERE uploaded_at > CURRENT_TIMESTAMP - INTERVAL '1 hour';
```

## 10. 安全考虑

### 10.1 权限管理

```sql
-- 创建应用用户
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 授予必要权限
GRANT CONNECT ON DATABASE novel_task_manager TO app_user;
GRANT USAGE ON SCHEMA task_manager TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA task_manager TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA task_manager TO app_user;
```

### 10.2 数据加密

- 使用 SSL/TLS 加密数据库连接
- 敏感数据字段使用应用层加密
- 定期轮换数据库密码

## 11. 扩展性设计

### 11.1 水平扩展

- 使用读写分离架构
- 配置主从复制
- 使用连接池和负载均衡

### 11.2 垂直扩展

- 根据负载调整数据库实例规格
- 优化查询和索引
- 使用缓存层（Redis）减少数据库压力

---

*文档版本：1.0.0*  
*最后更新：2024年*  
*作者：系统架构团队*