"""
用户认证用例
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from domains.user.entities import UserEntity
from domains.user.services import UserService
from application.dto.user_dto import (
    UserRegisterDTO, UserLoginDTO, UserProfileDTO, 
    UserUpdateDTO, PasswordChangeDTO
)
from core.config import settings

# 密码加密上下文（使用内置的 pbkdf2_sha256，避免外部二进制依赖问题）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthUseCase:
    """用户认证用例"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    async def register_user(self, user_data: UserRegisterDTO) -> Dict[str, Any]:
        """用户注册"""
        # 验证密码确认
        if user_data.password != user_data.confirm_password:
            raise ValueError("密码和确认密码不匹配")
        
        # 创建用户（内部包含唯一性检查）
        hashed_password = self._get_password_hash(user_data.password)
        created_user = await self.user_service.create_user(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            phone=user_data.phone,
        )
        
        return {
            "success": True,
            "message": "用户注册成功",
            "data": {
                "username": created_user.username
            }
        }
    
    async def login_user(self, login_data: UserLoginDTO) -> Dict[str, Any]:
        """用户登录"""
        # 根据登录标识符获取用户
        user = await self.user_service.get_user_by_login_identifier(login_data.login_identifier)
        
        if not user:
            raise ValueError("用户名、邮箱或手机号不存在")
        
        if not user.is_active:
            raise ValueError("用户账户已被禁用")
        
        # 验证密码
        if not self._verify_password(login_data.password, user.hashed_password):
            raise ValueError("密码错误")
        
        # 更新最后登录时间
        await self.user_service.update_last_login(user.id)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self._create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "message": "登录成功",
            "token": access_token,
            "data": {
                "username": user.username
            }
        }
    
    async def get_user_profile(self, user_id: UUID) -> Dict[str, Any]:
        """获取用户资料"""
        user = await self.user_service.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("用户不存在")
        
        return {
            "success": True,
            "message": "用户资料获取成功",
            "data": user.to_profile_dict()
        }
    
    async def update_user_profile(self, user_id: UUID, update_data: UserUpdateDTO) -> Dict[str, Any]:
        """更新用户资料"""
        user = await self.user_service.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("用户不存在")
        
        # 构建更新数据
        update_dict = {}
        old_info = {}
        new_info = {}
        
        # 计算差异并更新
        new_username = update_data.new_username if update_data.new_username and update_data.new_username != update_data.old_username else None
        new_email = update_data.new_email if update_data.new_email and update_data.new_email != update_data.old_email else None
        new_phone = update_data.new_phone if update_data.new_phone and update_data.new_phone != update_data.old_phone else None

        if new_username or new_email or new_phone:
            updated_user = await self.user_service.update_user_profile(
                user_id,
                username=new_username,
                email=new_email,
                phone=new_phone,
            )
            if new_username:
                old_info["username"] = update_data.old_username
                new_info["username"] = new_username
            if new_email:
                old_info["email"] = update_data.old_email
                new_info["email"] = new_email
            if new_phone:
                old_info["phone"] = update_data.old_phone
                new_info["phone"] = new_phone

            return {
                "success": True,
                "message": "用户信息修改成功",
                "data": {
                    "old_info": old_info,
                    "new_info": new_info
                }
            }
        return {
            "success": True,
            "message": "用户信息未发生变化",
            "data": {}
        }
    
    async def change_password(self, user_id: UUID, password_data: PasswordChangeDTO) -> Dict[str, Any]:
        """修改密码"""
        user = await self.user_service.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("用户不存在")
        
        # 验证当前密码
        if not self._verify_password(password_data.current_password, user.hashed_password):
            raise ValueError("当前密码错误")
        
        # 验证新密码确认
        if password_data.new_password != password_data.confirm_new_password:
            raise ValueError("新密码和确认密码不匹配")
        
        # 检查新密码是否与当前密码相同
        if self._verify_password(password_data.new_password, user.hashed_password):
            raise ValueError("新密码不能与当前密码相同")
        
        # 更新密码
        hashed_new_password = self._get_password_hash(password_data.new_password)
        updated_user = await self.user_service.change_password_hashed(user_id, hashed_new_password)
        
        return {
            "success": True,
            "message": "密码修改成功",
            "data": {
                "username": updated_user.username,
                "message": "密码已更新，请使用新密码登录"
            }
        }
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        stats = await self.user_service.get_user_stats()
        
        return {
            "success": True,
            "message": "统计信息获取成功",
            "data": stats
        }
    
    async def logout_user(self) -> Dict[str, Any]:
        """用户登出"""
        # 在实际应用中，这里可能需要将令牌加入黑名单
        return {
            "success": True,
            "message": "登出成功，已清除用户会话"
        }