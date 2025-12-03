"""
配置持久化层 - SQLite 存储用户配置

扩展现有 SQLite 数据库，实现用户配置的存储和加载。
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import aiosqlite

from config_models import UserConfig, get_default_config


class ConfigStorage:
    """用户配置存储管理器.
    
    使用 SQLite 存储用户配置，支持异步操作。
    """
    
    def __init__(self, db_path: Path):
        """初始化配置存储.
        
        Args:
            db_path: SQLite 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_dir()
    
    def _ensure_db_dir(self) -> None:
        """确保数据库目录存在."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def init_table(self) -> None:
        """初始化配置表.
        
        创建 user_configs 表（如果不存在）。
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_configs (
                    user_id TEXT PRIMARY KEY,
                    config_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建更新时间触发器
            await db.execute("""
                CREATE TRIGGER IF NOT EXISTS update_user_config_timestamp
                AFTER UPDATE ON user_configs
                BEGIN
                    UPDATE user_configs SET updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = NEW.user_id;
                END
            """)
            await db.commit()
    
    def init_table_sync(self) -> None:
        """同步初始化配置表.
        
        用于启动时确保表存在。
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_configs (
                    user_id TEXT PRIMARY KEY,
                    config_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建更新时间触发器（SQLite 不支持 IF NOT EXISTS for triggers）
            try:
                cursor.execute("""
                    CREATE TRIGGER update_user_config_timestamp
                    AFTER UPDATE ON user_configs
                    BEGIN
                        UPDATE user_configs SET updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = NEW.user_id;
                    END
                """)
            except sqlite3.OperationalError:
                # 触发器已存在
                pass
            conn.commit()
        finally:
            conn.close()
    
    async def save_config(self, user_id: str, config: UserConfig) -> bool:
        """保存用户配置.
        
        Args:
            user_id: 用户标识
            config: 用户配置对象
            
        Returns:
            是否保存成功
        """
        try:
            config_json = config.to_json()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO user_configs (user_id, config_json)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        config_json = excluded.config_json,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, config_json))
                await db.commit()
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    async def load_config(self, user_id: str) -> Optional[UserConfig]:
        """加载用户配置.
        
        Args:
            user_id: 用户标识
            
        Returns:
            用户配置对象，不存在则返回 None
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT config_json FROM user_configs WHERE user_id = ?",
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return UserConfig.from_json(row["config_json"])
            return None
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None
    
    async def load_or_default(self, user_id: str) -> UserConfig:
        """加载用户配置，不存在则返回默认配置.
        
        Args:
            user_id: 用户标识
            
        Returns:
            用户配置对象
        """
        config = await self.load_config(user_id)
        if config is None:
            config = get_default_config()
        return config
    
    async def delete_config(self, user_id: str) -> bool:
        """删除用户配置.
        
        Args:
            user_id: 用户标识
            
        Returns:
            是否删除成功
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM user_configs WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
            return True
        except Exception as e:
            print(f"删除配置失败: {e}")
            return False
    
    async def reset_to_default(self, user_id: str) -> UserConfig:
        """重置用户配置为默认值.
        
        Args:
            user_id: 用户标识
            
        Returns:
            默认配置对象
        """
        default_config = get_default_config()
        await self.save_config(user_id, default_config)
        return default_config
    
    async def get_all_users(self) -> list[str]:
        """获取所有有配置的用户列表.
        
        Returns:
            用户 ID 列表
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT user_id FROM user_configs"
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    async def get_config_stats(self) -> Dict[str, Any]:
        """获取配置统计信息.
        
        Returns:
            统计信息字典
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 总用户数
                async with db.execute(
                    "SELECT COUNT(*) FROM user_configs"
                ) as cursor:
                    row = await cursor.fetchone()
                    total_users = row[0] if row else 0
                
                # 最近更新时间
                async with db.execute(
                    "SELECT MAX(updated_at) FROM user_configs"
                ) as cursor:
                    row = await cursor.fetchone()
                    last_updated = row[0] if row else None
                
                return {
                    "total_users": total_users,
                    "last_updated": last_updated,
                }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {"total_users": 0, "last_updated": None}


# 全局配置存储实例（延迟初始化）
_config_storage: Optional[ConfigStorage] = None


def get_config_storage(db_path: Path) -> ConfigStorage:
    """获取配置存储实例（单例模式）.
    
    Args:
        db_path: 数据库路径
        
    Returns:
        ConfigStorage 实例
    """
    global _config_storage
    if _config_storage is None:
        _config_storage = ConfigStorage(db_path)
        _config_storage.init_table_sync()
    return _config_storage


async def init_config_storage(db_path: Path) -> ConfigStorage:
    """异步初始化配置存储.
    
    Args:
        db_path: 数据库路径
        
    Returns:
        ConfigStorage 实例
    """
    storage = get_config_storage(db_path)
    await storage.init_table()
    return storage

