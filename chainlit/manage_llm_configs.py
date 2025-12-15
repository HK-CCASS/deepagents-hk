#!/usr/bin/env python3
"""
LLM 配置管理脚本

用法:
    # 查看所有配置
    python manage_llm_configs.py list
    
    # 查看指定用户的配置
    python manage_llm_configs.py list --user test
    
    # 删除指定用户的所有配置
    python manage_llm_configs.py delete --user test
    
    # 删除指定名称的配置
    python manage_llm_configs.py delete --user test --name "硅基流动"
    
    # 删除所有用户的所有配置
    python manage_llm_configs.py delete --all
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent / "chainlit_data" / "chat_history.db"

# Docker 环境下的路径
DOCKER_DB_PATH = Path("/app/chainlit_data/chat_history.db")


def get_db_path():
    """获取数据库路径."""
    if DOCKER_DB_PATH.exists():
        return DOCKER_DB_PATH
    elif DB_PATH.exists():
        return DB_PATH
    else:
        print(f"❌ 数据库不存在: {DB_PATH}")
        sys.exit(1)


def list_configs(user_id: str = None):
    """列出 LLM 配置."""
    db = sqlite3.connect(get_db_path())
    cursor = db.cursor()
    
    if user_id:
        cursor.execute(
            "SELECT id, user_id, name, model, protocol FROM llm_configs WHERE user_id = ?",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT id, user_id, name, model, protocol FROM llm_configs ORDER BY user_id"
        )
    
    rows = cursor.fetchall()
    db.close()
    
    if not rows:
        print("📭 没有找到 LLM 配置")
        return
    
    print(f"\n{'='*70}")
    print(f"{'ID':<10} {'用户':<15} {'名称':<20} {'模型':<20} {'协议':<10}")
    print(f"{'='*70}")
    
    for row in rows:
        config_id = row[0][:8] + "..."
        print(f"{config_id:<10} {row[1]:<15} {row[2]:<20} {row[3]:<20} {row[4]:<10}")
    
    print(f"{'='*70}")
    print(f"共 {len(rows)} 条配置\n")


def delete_configs(user_id: str = None, name: str = None, delete_all: bool = False):
    """删除 LLM 配置."""
    db = sqlite3.connect(get_db_path())
    cursor = db.cursor()
    
    # 构建 SQL
    if delete_all:
        sql = "DELETE FROM llm_configs"
        params = ()
        desc = "所有用户的所有配置"
    elif user_id and name:
        sql = "DELETE FROM llm_configs WHERE user_id = ? AND name = ?"
        params = (user_id, name)
        desc = f"用户 {user_id} 的配置 '{name}'"
    elif user_id:
        sql = "DELETE FROM llm_configs WHERE user_id = ?"
        params = (user_id,)
        desc = f"用户 {user_id} 的所有配置"
    else:
        print("❌ 请指定 --user 或 --all")
        db.close()
        return
    
    # 先统计数量
    count_sql = sql.replace("DELETE FROM", "SELECT COUNT(*) FROM")
    cursor.execute(count_sql, params)
    count = cursor.fetchone()[0]
    
    if count == 0:
        print(f"📭 没有找到匹配的配置: {desc}")
        db.close()
        return
    
    # 确认删除
    print(f"\n⚠️  即将删除 {count} 条配置: {desc}")
    confirm = input("确认删除? (y/N): ").strip().lower()
    
    if confirm == 'y':
        cursor.execute(sql, params)
        db.commit()
        print(f"✅ 已删除 {count} 条配置")
    else:
        print("❌ 已取消")
    
    db.close()


def main():
    parser = argparse.ArgumentParser(description="LLM 配置管理工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出配置")
    list_parser.add_argument("--user", "-u", help="指定用户 ID")
    
    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除配置")
    delete_parser.add_argument("--user", "-u", help="指定用户 ID")
    delete_parser.add_argument("--name", "-n", help="指定配置名称")
    delete_parser.add_argument("--all", "-a", action="store_true", help="删除所有配置")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_configs(args.user)
    elif args.command == "delete":
        delete_configs(args.user, args.name, args.all)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
