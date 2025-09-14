"""
Redis 缓存管理
"""
import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from core.config import settings


class CacheService:
    """缓存服务"""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """连接到 Redis"""
        self._redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
    
    async def disconnect(self) -> None:
        """断开 Redis 连接"""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self._redis:
            return None
        
        value = await self._redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        if not self._redis:
            return False
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        result = await self._redis.set(key, value, ex=expire)
        return bool(result)
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self._redis:
            return False
        
        return bool(await self._redis.delete(key))
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            return False
        
        return bool(await self._redis.exists(key))
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if not self._redis:
            return False
        
        return await self._redis.expire(key, seconds)


# 全局缓存实例
cache = CacheService()