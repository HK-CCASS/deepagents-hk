#!/usr/bin/env python
"""
初始化 Chainlit SQLite 数据库。

运行: python init_db.py
"""

import sqlite3
from pathlib import Path

# 数据库路径
project_root = Path(__file__).parent.parent.resolve()
DB_PATH = project_root / "chainlit_data" / "chat_history.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQL Schema for Chainlit (adapted for SQLite)
SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT NOT NULL UNIQUE,
    "metadata" TEXT NOT NULL,
    "createdAt" TEXT
);

-- Threads table (conversations)
CREATE TABLE IF NOT EXISTS threads (
    "id" TEXT PRIMARY KEY,
    "createdAt" TEXT,
    "name" TEXT,
    "userId" TEXT,
    "userIdentifier" TEXT,
    "tags" TEXT,
    "metadata" TEXT,
    FOREIGN KEY ("userId") REFERENCES users("id") ON DELETE CASCADE
);

-- Steps table (messages and actions)
CREATE TABLE IF NOT EXISTS steps (
    "id" TEXT PRIMARY KEY,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "threadId" TEXT NOT NULL,
    "parentId" TEXT,
    "streaming" INTEGER NOT NULL,
    "waitForAnswer" INTEGER,
    "isError" INTEGER,
    "metadata" TEXT,
    "tags" TEXT,
    "input" TEXT,
    "output" TEXT,
    "createdAt" TEXT,
    "command" TEXT,
    "start" TEXT,
    "end" TEXT,
    "generation" TEXT,
    "showInput" TEXT,
    "language" TEXT,
    "indent" INTEGER,
    "defaultOpen" INTEGER,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

-- Elements table (files, images, etc.)
CREATE TABLE IF NOT EXISTS elements (
    "id" TEXT PRIMARY KEY,
    "threadId" TEXT,
    "type" TEXT,
    "url" TEXT,
    "chainlitKey" TEXT,
    "name" TEXT NOT NULL,
    "display" TEXT,
    "objectKey" TEXT,
    "size" TEXT,
    "page" INTEGER,
    "language" TEXT,
    "forId" TEXT,
    "mime" TEXT,
    "props" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

-- Feedbacks table
CREATE TABLE IF NOT EXISTS feedbacks (
    "id" TEXT PRIMARY KEY,
    "forId" TEXT NOT NULL,
    "threadId" TEXT NOT NULL,
    "value" INTEGER NOT NULL,
    "comment" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

-- User configs table (用户配置)
CREATE TABLE IF NOT EXISTS user_configs (
    "user_id" TEXT PRIMARY KEY,
    "config_json" TEXT NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_threads_userId ON threads("userId");
CREATE INDEX IF NOT EXISTS idx_threads_userIdentifier ON threads("userIdentifier");
CREATE INDEX IF NOT EXISTS idx_steps_threadId ON steps("threadId");
CREATE INDEX IF NOT EXISTS idx_elements_threadId ON elements("threadId");
CREATE INDEX IF NOT EXISTS idx_feedbacks_threadId ON feedbacks("threadId");
"""

# 配置表更新时间触发器 SQL
CONFIG_TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS update_user_config_timestamp
AFTER UPDATE ON user_configs
BEGIN
    UPDATE user_configs SET updated_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id;
END;
"""

def init_database():
    """创建数据库和表。"""
    print(f"📦 初始化数据库: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 执行 schema
    cursor.executescript(SCHEMA)
    
    # 创建配置表触发器（需要单独执行）
    try:
        cursor.execute(CONFIG_TRIGGER_SQL)
    except sqlite3.OperationalError:
        # 触发器已存在，忽略错误
        pass
    
    conn.commit()
    
    # 验证表创建
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"✅ 已创建表: {[t[0] for t in tables]}")
    
    # 显示触发器
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
    triggers = cursor.fetchall()
    if triggers:
        print(f"✅ 已创建触发器: {[t[0] for t in triggers]}")
    
    conn.close()
    print("✅ 数据库初始化完成！")


if __name__ == "__main__":
    init_database()

