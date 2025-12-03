"""
本地文件存储客户端 - 用于 Chainlit SQLAlchemyDataLayer。

将上传的文件存储到本地目录。
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Union


class LocalStorageClient:
    """本地文件存储客户端，实现 Chainlit BaseStorageClient 接口。"""
    
    def __init__(self, storage_dir: str | Path):
        """
        初始化本地存储客户端。
        
        Args:
            storage_dir: 存储文件的本地目录路径
        """
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        object_key: str,
        data: Union[bytes, str],
        mime: str = "application/octet-stream",
        overwrite: bool = True,
        content_disposition: str | None = None,
    ) -> Dict[str, Any]:
        """上传文件到本地存储。"""
        file_path = self.storage_dir / object_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not overwrite and file_path.exists():
            raise FileExistsError(f"File already exists: {file_path}")
        
        if isinstance(data, str):
            file_path.write_text(data)
        else:
            file_path.write_bytes(data)
        
        return {
            "object_key": object_key,
            "url": f"file://{file_path}",
        }
    
    async def delete_file(self, object_key: str) -> bool:
        """删除本地文件。"""
        file_path = self.storage_dir / object_key
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    async def get_read_url(self, object_key: str) -> str:
        """获取文件读取 URL（本地路径）。"""
        file_path = self.storage_dir / object_key
        # 返回相对于 chainlit 服务器的 URL
        return f"/files/{object_key}"
    
    async def close(self) -> None:
        """关闭存储客户端（本地存储无需特殊关闭）。"""
        pass

