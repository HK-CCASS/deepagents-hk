#!/usr/bin/env python3
"""
配置迁移脚本 - 解决部署时的配置冲突

在新服务器部署时运行，自动修复依赖旧环境变量的用户配置。

用法:
    python migrate_configs.py [--dry-run] [--reset-all]
    
选项:
    --dry-run    只检查，不修改
    --reset-all  删除所有用户配置（让用户重新配置）
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent / "chainlit_data" / "chat_history.db"
DOCKER_DB_PATH = Path("/app/chainlit_data/chat_history.db")


def get_db_path():
    """获取数据库路径."""
    if DOCKER_DB_PATH.exists():
        return DOCKER_DB_PATH
    elif DB_PATH.exists():
        return DB_PATH
    else:
        print(f"❌ 数据库不存在")
        return None


def get_default_config():
    """获取当前默认配置."""
    return {
        "api_key": os.getenv("CUSTOM_API_KEY"),
        "api_url": os.getenv("CUSTOM_API_URL"),
        "model": os.getenv("CUSTOM_API_MODEL", "deepseek-chat"),
        "api_protocol": os.getenv("CUSTOM_API_PROTOCOL", "openai"),
    }


def check_conflicts(db_path):
    """检查配置冲突."""
    conflicts = []
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("SELECT user_id, config_json FROM user_configs")
    rows = cursor.fetchall()
    
    for user_id, config_json in rows:
        try:
            config = json.loads(config_json)
            api_key = config.get("api_key") or config.get("api_key_override")
            provider = config.get("provider", "")
            
            # 检查是否依赖环境变量
            if not api_key:
                env_var_needed = None
                if provider == "siliconflow":
                    env_var_needed = "SILICONFLOW_API_KEY"
                elif provider == "openai":
                    env_var_needed = "OPENAI_API_KEY"
                elif provider == "anthropic":
                    env_var_needed = "ANTHROPIC_API_KEY"
                
                if env_var_needed and not os.getenv(env_var_needed):
                    conflicts.append({
                        "user_id": user_id,
                        "provider": provider,
                        "missing_env": env_var_needed,
                        "config": config,
                    })
        except json.JSONDecodeError:
            conflicts.append({
                "user_id": user_id,
                "error": "JSON 解析失败",
            })
    
    db.close()
    return conflicts


def fix_conflicts(db_path, dry_run=False):
    """修复配置冲突."""
    conflicts = check_conflicts(db_path)
    
    if not conflicts:
        print("✅ 没有发现配置冲突")
        return
    
    print(f"⚠️  发现 {len(conflicts)} 个配置冲突:\n")
    
    for c in conflicts:
        print(f"  用户: {c['user_id']}")
        if "error" in c:
            print(f"    错误: {c['error']}")
        else:
            print(f"    Provider: {c['provider']}")
            print(f"    缺失环境变量: {c['missing_env']}")
        print()
    
    if dry_run:
        print("📋 Dry run 模式，不做修改")
        return
    
    # 获取默认配置
    default_config = get_default_config()
    
    if not default_config["api_key"]:
        print("❌ 无法修复：CUSTOM_API_KEY 环境变量未设置")
        return
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    for c in conflicts:
        user_id = c["user_id"]
        
        if "error" in c:
            # 配置损坏，删除
            cursor.execute("DELETE FROM user_configs WHERE user_id = ?", (user_id,))
            print(f"🗑️  已删除损坏配置: {user_id}")
        else:
            # 更新为默认配置
            old_config = c["config"]
            old_config["api_key"] = default_config["api_key"]
            old_config["api_url"] = default_config["api_url"]
            old_config["model"] = default_config["model"]
            old_config["api_protocol"] = default_config["api_protocol"]
            old_config["provider"] = "siliconflow"  # 重置 provider
            
            new_config_json = json.dumps(old_config, ensure_ascii=False)
            cursor.execute(
                "UPDATE user_configs SET config_json = ? WHERE user_id = ?",
                (new_config_json, user_id)
            )
            print(f"✅ 已更新配置: {user_id} -> {default_config['model']}")
    
    db.commit()
    db.close()
    print(f"\n🎉 已修复 {len(conflicts)} 个配置")


def reset_all_configs(db_path, dry_run=False):
    """删除所有用户配置."""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM user_configs")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📭 没有用户配置")
        db.close()
        return
    
    print(f"⚠️  即将删除 {count} 个用户配置")
    
    if dry_run:
        print("📋 Dry run 模式，不做修改")
        db.close()
        return
    
    confirm = input("确认删除? (y/N): ").strip().lower()
    if confirm == "y":
        cursor.execute("DELETE FROM user_configs")
        db.commit()
        print(f"✅ 已删除 {count} 个用户配置")
    else:
        print("❌ 已取消")
    
    db.close()


def main():
    parser = argparse.ArgumentParser(description="配置迁移工具")
    parser.add_argument("--dry-run", action="store_true", help="只检查，不修改")
    parser.add_argument("--reset-all", action="store_true", help="删除所有用户配置")
    parser.add_argument("--check", action="store_true", help="只检查冲突")
    
    args = parser.parse_args()
    
    db_path = get_db_path()
    if not db_path:
        return
    
    print(f"📦 数据库: {db_path}\n")
    
    if args.check:
        conflicts = check_conflicts(db_path)
        if conflicts:
            print(f"⚠️  发现 {len(conflicts)} 个配置冲突")
            for c in conflicts:
                print(f"  - {c['user_id']}: {c.get('missing_env', c.get('error'))}")
        else:
            print("✅ 没有配置冲突")
    elif args.reset_all:
        reset_all_configs(db_path, args.dry_run)
    else:
        fix_conflicts(db_path, args.dry_run)


if __name__ == "__main__":
    main()
