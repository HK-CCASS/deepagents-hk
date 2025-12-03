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
-- Users table (扩展用户认证字段)
CREATE TABLE IF NOT EXISTS users (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT NOT NULL UNIQUE,
    "metadata" TEXT NOT NULL,
    "createdAt" TEXT,
    "password_hash" TEXT,
    "email" TEXT,
    "display_name" TEXT,
    "is_active" INTEGER DEFAULT 1
);

-- Email 唯一索引（允许 NULL）
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users("email") WHERE "email" IS NOT NULL;

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

# 用户表迁移 SQL（为现有数据库添加新列）
# 注意：SQLite 不支持在 ALTER TABLE 中添加 UNIQUE 列，所以 email 列不带 UNIQUE
USER_TABLE_MIGRATIONS = [
    ('password_hash', 'ALTER TABLE users ADD COLUMN "password_hash" TEXT'),
    ('email', 'ALTER TABLE users ADD COLUMN "email" TEXT'),
    ('display_name', 'ALTER TABLE users ADD COLUMN "display_name" TEXT'),
    ('is_active', 'ALTER TABLE users ADD COLUMN "is_active" INTEGER DEFAULT 1'),
]

# 用户表索引（用于 email 唯一性检查）
USER_TABLE_INDEXES = [
    ('idx_users_email', 'CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users("email") WHERE "email" IS NOT NULL'),
]


def migrate_users_table(cursor: sqlite3.Cursor) -> None:
    """为现有 users 表添加新的认证字段。"""
    # 获取现有列
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # 添加缺失的列
    for column_name, alter_sql in USER_TABLE_MIGRATIONS:
        if column_name not in existing_columns:
            try:
                cursor.execute(alter_sql)
                print(f"  ✓ 添加列: {column_name}")
            except sqlite3.OperationalError as e:
                # 列已存在，忽略
                if "duplicate column" not in str(e).lower():
                    print(f"  ⚠ 添加列 {column_name} 失败: {e}")
    
    # 创建索引（用于邮箱唯一性检查）
    for index_name, index_sql in USER_TABLE_INDEXES:
        try:
            cursor.execute(index_sql)
            print(f"  ✓ 创建索引: {index_name}")
        except sqlite3.OperationalError:
            # 索引已存在，忽略
            pass


def init_database():
    """创建数据库和表。"""
    print(f"📦 初始化数据库: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 执行 schema
    cursor.executescript(SCHEMA)
    
    # 迁移 users 表（添加新的认证字段）
    print("🔄 检查用户表迁移...")
    migrate_users_table(cursor)
    
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
    
    # 显示 users 表结构
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"✅ users 表字段: {[col[1] for col in columns]}")
    
    # 显示触发器
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
    triggers = cursor.fetchall()
    if triggers:
        print(f"✅ 已创建触发器: {[t[0] for t in triggers]}")
    
    conn.close()
    print("✅ 数据库初始化完成！")


if __name__ == "__main__":
    init_database()

