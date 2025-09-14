"""
用户仓储层模块
"""
from typing import Dict, List, Optional, Any
from uuid import UUID
from domains.user.entities import UserEntity


class UserRepository:
    """用户仓储接口"""
    
    async def create(self, user: UserEntity) -> UserEntity:
        """创建用户"""
        raise NotImplementedError
    
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """根据ID获取用户"""
        raise NotImplementedError
    
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """根据邮箱获取用户"""
        raise NotImplementedError
    
    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        raise NotImplementedError
    
    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        """根据手机号获取用户"""
        raise NotImplementedError
    
    async def get_by_login_identifier(self, identifier: str) -> Optional[UserEntity]:
        """根据登录标识符（用户名/邮箱/手机号）获取用户"""
        raise NotImplementedError
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """获取所有用户（分页）"""
        raise NotImplementedError
    
    async def get_active_users(self) -> List[UserEntity]:
        """获取所有活跃用户"""
        raise NotImplementedError
    
    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[UserEntity]:
        """更新用户信息"""
        raise NotImplementedError
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """更新最后登录时间"""
        raise NotImplementedError
    
    async def delete(self, user_id: UUID) -> bool:
        """删除用户"""
        raise NotImplementedError
    
    async def soft_delete(self, user_id: UUID) -> bool:
        """软删除用户（设置is_active为False）"""
        raise NotImplementedError
    
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        raise NotImplementedError
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        raise NotImplementedError
    
    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否存在"""
        raise NotImplementedError
    
    async def get_user_stats(self) -> Dict[str, int]:
        """获取用户统计信息"""
        raise NotImplementedError


class MockUserRepository(UserRepository):
    """模拟用户仓储实现"""
    
    def __init__(self):
        self.users: Dict[str, UserEntity] = {}
    
    async def create(self, user: UserEntity) -> UserEntity:
        """创建用户"""
        self.users[str(user.id)] = user
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """根据ID获取用户"""
        return self.users.get(str(user_id))
    
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """根据邮箱获取用户"""
        for user in self.users.values():
            if user.email == email.lower().strip():
                return user
        return None
    
    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        for user in self.users.values():
            if user.username == username.strip():
                return user
        return None
    
    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        """根据手机号获取用户"""
        if not phone:
            return None
        for user in self.users.values():
            if user.phone and user.phone == phone.strip():
                return user
        return None
    
    async def get_by_login_identifier(self, identifier: str) -> Optional[UserEntity]:
        """根据登录标识符获取用户"""
        # 尝试按用户名查找
        user = await self.get_by_username(identifier)
        if user:
            return user
        
        # 尝试按邮箱查找
        user = await self.get_by_email(identifier)
        if user:
            return user
        
        # 尝试按手机号查找
        user = await self.get_by_phone(identifier)
        return user
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """获取所有用户（分页）"""
        users = list(self.users.values())
        return users[skip:skip + limit]
    
    async def get_active_users(self) -> List[UserEntity]:
        """获取所有活跃用户"""
        return [user for user in self.users.values() if user.is_active]
    
    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[UserEntity]:
        """更新用户信息"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # 更新用户属性
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.users[str(user_id)] = user
        return user
    
    async def update_last_login(self, user_id: UUID) -> bool:
        """更新最后登录时间"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.update_last_login()
        self.users[str(user_id)] = user
        return True
    
    async def delete(self, user_id: UUID) -> bool:
        """删除用户"""
        if str(user_id) in self.users:
            del self.users[str(user_id)]
            return True
        return False
    
    async def soft_delete(self, user_id: UUID) -> bool:
        """软删除用户"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.users[str(user_id)] = user
        return True
    
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        return await self.get_by_username(username) is not None
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        return await self.get_by_email(email) is not None
    
    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否存在"""
        return await self.get_by_phone(phone) is not None
    
    async def get_user_stats(self) -> Dict[str, int]:
        """获取用户统计信息"""
        total_users = len(self.users)
        active_users = sum(1 for user in self.users.values() if user.is_active)
        
        # 计算今日新增用户数（简化实现）
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        new_users_today = sum(1 for user in self.users.values() 
                            if user.created_at and user.created_at.date() == today)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_today": new_users_today
        }
