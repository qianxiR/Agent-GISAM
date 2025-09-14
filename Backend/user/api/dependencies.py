"""
FastAPI 依赖注入模块
提供用户认证和权限控制的依赖函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from core.security import verify_token

# HTTP Bearer Token 实例
security = HTTPBearer()


# 临时用户实体类（简化版本）
class UserEntity:
    """临时用户实体类"""
    
    def __init__(self, user_id: str, username: str, email: str, is_active: bool = True, is_superuser: bool = False):
        self.id = user_id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.is_superuser = is_superuser


# 临时用户数据（模拟数据库）
mock_users = {
    "1": UserEntity("1", "qianxi", "qianxi111@126.com", True, False),
    "2": UserEntity("2", "admin", "admin@example.com", True, True),
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserEntity:
    """获取当前用户
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        UserEntity: 当前用户实体
        
    Raises:
        HTTPException: 当用户不存在或令牌无效时
    """
    
    try:
        # 从token获取用户ID
        user_id = verify_token(credentials.credentials)
        
        # 从模拟数据获取用户对象
        current_user = mock_users.get(user_id)
        
        # 处理None情况
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或令牌无效"
            )
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败"
        )


async def get_current_active_user(
    current_user: UserEntity = Depends(get_current_user)
) -> UserEntity:
    """获取当前活跃用户
    
    Args:
        current_user: 当前用户实体
        
    Returns:
        UserEntity: 活跃用户实体
        
    Raises:
        HTTPException: 当用户账户被禁用时
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户账户已禁用"
        )
    return current_user


async def get_current_superuser(
    current_user: UserEntity = Depends(get_current_user)
) -> UserEntity:
    """获取当前超级用户
    
    Args:
        current_user: 当前用户实体
        
    Returns:
        UserEntity: 超级用户实体
        
    Raises:
        HTTPException: 当用户权限不足时
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级用户权限"
        )
    return current_user
