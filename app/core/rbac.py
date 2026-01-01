"""Role-Based Access Control (RBAC) for Base10."""
from functools import wraps
from fastapi import HTTPException, status
from typing import List, Callable
from app.models.user import User
from app.models.enums import UserRole


def require_role(allowed_roles: List[UserRole]):
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @require_role([UserRole.TEACHER])
        async def teacher_only_endpoint(user: User = Depends(get_current_user)):
            ...
    
        @require_role([UserRole.ADMIN, UserRole.TEACHER])
        async def admin_or_teacher_endpoint(user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by Depends(get_current_user))
            user = kwargs.get('user') or kwargs.get('current_user')
            
            if not user:
                # Try to find in args (positional arguments)
                for arg in args:
                    if isinstance(arg, User):
                        user = arg
                        break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_role(user: User, allowed_roles: List[str]) -> bool:
    """
    Check if user has one of the allowed roles.
    
    Usage:
        if not check_role(current_user, [UserRole.TEACHER, UserRole.ADMIN]):
            raise HTTPException(403, "Access denied")
    """
    return user.role in allowed_roles


def is_teacher(user: User) -> bool:
    """Check if user is a teacher."""
    return user.role == UserRole.TEACHER


def is_student(user: User) -> bool:
    """Check if user is a student."""
    return user.role == UserRole.STUDENT


def is_admin(user: User) -> bool:
    """Check if user is an admin."""
    return user.role == UserRole.ADMIN


def can_access_classroom_as_teacher(user: User, teacher_id: int) -> bool:
    """Check if user can access classroom as teacher."""
    # Admin can access any classroom
    if is_admin(user):
        return True
    
    # Teacher can only access their own classrooms
    return is_teacher(user) and user.id == teacher_id


def can_modify_user(current_user: User, target_user: User) -> bool:
    """Check if current user can modify target user."""
    # Admin can modify anyone
    if is_admin(current_user):
        return True
    
    # Users can only modify themselves
    return current_user.id == target_user.id
