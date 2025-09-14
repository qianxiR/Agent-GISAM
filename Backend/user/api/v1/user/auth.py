"""
用户认证API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from application.dto.user_dto import (
    UserRegisterDTO, UserLoginDTO, UserUpdateDTO, 
    PasswordChangeDTO, AuthResponseDTO
)
from application.use_cases.user.auth_use_case import AuthUseCase
from core.database import get_db
from core.security import get_current_user_id
from core.container import build_auth_use_case

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=AuthResponseDTO)
async def register_user(
    user_data: UserRegisterDTO,
    session = Depends(get_db)
) -> Dict[str, Any]:
    """用户注册"""
    try:
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.register_user(user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=AuthResponseDTO)
async def login_user(
    login_data: UserLoginDTO,
    session = Depends(get_db)
) -> Dict[str, Any]:
    """用户登录"""
    try:
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.login_user(login_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.get("/profile")
async def get_user_profile(
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取用户资料"""
    try:
        from uuid import UUID
        user_id = UUID(current_user_id)
        
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.get_user_profile(user_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败"
        )


@router.get("/me")
async def get_current_user(
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取当前用户信息"""
    try:
        from uuid import UUID
        user_id = UUID(current_user_id)
        
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.get_user_profile(user_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.get("/stats")
async def get_user_stats(
    session = Depends(get_db)
) -> Dict[str, Any]:
    """获取用户统计信息"""
    try:
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.get_user_stats()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )


@router.post("/logout")
async def logout_user() -> Dict[str, Any]:
    """用户登出"""
    try:
        # 这里可以添加令牌黑名单逻辑
        return {
            "success": True,
            "message": "登出成功，已清除用户会话"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )


@router.post("/update-profile")
async def update_user_profile(
    update_data: UserUpdateDTO,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """修改用户信息"""
    try:
        from uuid import UUID
        user_id = UUID(current_user_id)
        
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.update_user_profile(user_id, update_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改用户信息失败"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeDTO,
    current_user_id: str = Depends(get_current_user_id),
    session = Depends(get_db)
) -> Dict[str, Any]:
    """修改密码"""
    try:
        from uuid import UUID
        user_id = UUID(current_user_id)
        
        auth_use_case = build_auth_use_case(session)
        
        result = await auth_use_case.change_password(user_id, password_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )