"""
用户服务层模块
"""
from typing import Dict, List, Optional
from uuid import UUID
from domains.user.entities import UserEntity
from domains.user.repositories import UserRepository


class UserService:
    """用户服务"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(
        self,
        email: str,
        username: str,
        hashed_password: str,
        phone: Optional[str] = None
    ) -> UserEntity:
        """创建新用户"""
        # 验证邮箱是否已存在
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("邮箱已存在")
        
        # 验证用户名是否已存在
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 验证手机号是否已存在
        if phone:
            existing_user = await self.user_repository.get_by_phone(phone)
            if existing_user:
                raise ValueError("手机号已存在")
        
        # 创建用户实体
        user = UserEntity.create_new(
            email=email,
            username=username,
            hashed_password=hashed_password,
            phone=phone
        )
        
        # 保存到仓储
        return await self.user_repository.create(user)
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        """根据ID获取用户"""
        return await self.user_repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        """根据邮箱获取用户"""
        return await self.user_repository.get_by_email(email)
    
    async def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        """根据用户名获取用户"""
        return await self.user_repository.get_by_username(username)
    
    async def get_user_by_phone(self, phone: str) -> Optional[UserEntity]:
        """根据手机号获取用户"""
        return await self.user_repository.get_by_phone(phone)

    async def get_user_by_login_identifier(self, identifier: str) -> Optional[UserEntity]:
        """根据登录标识符获取用户（用户名/邮箱/手机号）。"""
        return await self.user_repository.get_by_login_identifier(identifier)
    
    async def update_user_profile(
        self,
        user_id: UUID,
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> UserEntity:
        """更新用户资料"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 验证新用户名是否与其他用户冲突
        if username and username != user.username:
            existing_user = await self.user_repository.get_by_username(username)
            if existing_user:
                raise ValueError("用户名已存在")
        
        # 验证新邮箱是否与其他用户冲突
        if email and email != user.email:
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError("邮箱已存在")
        
        # 验证新手机号是否与其他用户冲突
        if phone and phone != user.phone:
            existing_user = await self.user_repository.get_by_phone(phone)
            if existing_user:
                raise ValueError("手机号已存在")
        
        # 更新用户资料
        user.update_profile(username=username, email=email, phone=phone)
        
        # 保存到仓储
        update_data = {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "updated_at": user.updated_at,
            "last_login": user.last_login
        }
        result = await self.user_repository.update(user_id, update_data)
        if not result:
            raise ValueError("用户更新失败")
        return result
    
    async def search_users(self, query: str) -> List[UserEntity]:
        """搜索用户"""
        # 使用get_all然后过滤，因为search_users方法已移除
        all_users = await self.user_repository.get_all()
        return [user for user in all_users if query.lower() in user.username.lower() or query.lower() in user.email.lower()]
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """获取用户列表"""
        return await self.user_repository.get_all(skip=skip, limit=limit)
    
    async def get_user_stats(self) -> Dict:
        """获取用户统计信息"""
        return await self.user_repository.get_user_stats()

    async def update_last_login(self, user_id: UUID) -> bool:
        """更新最后登录时间。"""
        return await self.user_repository.update_last_login(user_id)
    
    async def deactivate_user(self, user_id: UUID) -> UserEntity:
        """停用用户"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        result = await self.user_repository.update(user_id, {"is_active": False})
        if not result:
            raise ValueError("用户停用失败")
        return result
    
    async def activate_user(self, user_id: UUID) -> UserEntity:
        """激活用户"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        result = await self.user_repository.update(user_id, {"is_active": True})
        if not result:
            raise ValueError("用户激活失败")
        return result

    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在。"""
        return await self.user_repository.exists_by_username(username)

    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在。"""
        return await self.user_repository.exists_by_email(email)

    async def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否存在。"""
        return await self.user_repository.exists_by_phone(phone)

    async def change_password_hashed(self, user_id: UUID, hashed_new_password: str) -> UserEntity:
        """直接以哈希后的新密码更新用户密码。"""
        # 检查仓储是否有change_password_hashed方法
        if hasattr(self.user_repository, 'change_password_hashed'):
            updated = await self.user_repository.change_password_hashed(user_id, hashed_new_password)
        else:
            # 降级使用update方法
            updated = await self.user_repository.update(user_id, {"hashed_password": hashed_new_password})
        
        if not updated:
            raise ValueError("密码修改失败")
        return updated
