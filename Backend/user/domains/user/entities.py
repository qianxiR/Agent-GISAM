"""
用户实体模块
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from domains.user.value_objects import (
    Email, Username, PhoneNumber, Password, 
    UserId, UserStatus, Timestamp
)


@dataclass
class UserEntity:
    """用户实体"""
    id: UUID
    email: str
    username: str
    hashed_password: str
    phone: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    @classmethod
    def create_new(
        cls,
        email: str,
        username: str, 
        hashed_password: str,
        phone: Optional[str] = None
    ) -> "UserEntity":
        """创建新用户"""
        return cls(
            id=uuid4(),
            email=email.lower().strip(),
            username=username.strip(),
            hashed_password=hashed_password,
            phone=phone.strip() if phone else None
        )
    
    def update_last_login(self) -> None:
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_profile(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> None:
        """更新用户资料"""
        if username is not None:
            self.username = username.strip()
        if email is not None:
            self.email = email.lower().strip()
        if phone is not None:
            self.phone = phone.strip() if phone else None
        
        self.updated_at = datetime.utcnow()
    
    def validate_username(self, username: str) -> bool:
        """验证用户名"""
        return Username.validate(username)
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        return Email.validate(email)
    
    def validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        return PhoneNumber.validate(phone)
    
    def validate_password(self, password: str) -> bool:
        """验证密码强度"""
        return Password.validate(password)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "phone": self.phone,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def to_profile_dict(self) -> dict:
        """转换为用户资料响应格式"""
        return {
            "id": int(str(self.id).replace('-', '')[:8], 16),  # 转换为整数ID
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "registered_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def can_update_to(self, new_username: Optional[str] = None, new_email: Optional[str] = None) -> bool:
        """检查是否可以更新到新的用户名或邮箱"""
        if new_username and not self.validate_username(new_username):
            return False
        if new_email and not self.validate_email(new_email):
            return False
        return True