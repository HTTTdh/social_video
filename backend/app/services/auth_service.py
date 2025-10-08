from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
import bcrypt, logging

from app.core.settings import get_settings
from app.repositories import auth_repo
from app.schemas.auth_schemas import LoginIn, LoginOut, RefreshIn, RefreshOut, MeOut

# Setup logging
logger = logging.getLogger(__name__)
settings = get_settings()

def _hash_pwd(password: str) -> str:
    """Hash password với bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _verify_pwd(plain: str, hashed: str) -> bool:
    """Verify password với bcrypt"""
    try:
        result = bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        # Log kết quả (chỉ khi DEBUG)
        if settings.APP_ENV == "dev":
            logger.debug(f"Password verification: {result}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def _create_token(user_id: int, username: str, roles: list[str], token_type: str, expire_minutes: int = None, expire_days: int = None) -> str:
    """Tạo JWT token thống nhất"""
    now = datetime.now(timezone.utc)
    
    if expire_minutes:
        expire = now + timedelta(minutes=expire_minutes)
    elif expire_days:
        expire = now + timedelta(days=expire_days)
    else:
        expire = now + timedelta(hours=1)
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "roles": roles,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }
    
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

class AuthService:
    
    async def login(self, db: Session, payload: LoginIn) -> LoginOut:
        """
        Login đơn giản:
        1. Lấy identifier (username hoặc email)
        2. Tìm user (thử username → email)
        3. Verify password
        4. Tạo tokens
        """
        identifier = payload.identifier.strip()
        password = payload.password
        
        # Tìm user theo username hoặc email
        user = auth_repo.get_by_username_or_email(db, identifier)
        
        if settings.APP_ENV == "dev":
            if user:
                logger.info(f"User found: id={user.id}, username={user.username}, is_active={user.is_active}")
            else:
                logger.info(f"User not found: identifier={identifier}")
        
        
        if not user or not _verify_pwd(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tên đăng nhập hoặc mật khẩu không đúng"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị vô hiệu hóa"
            )
        
        roles = [r.name for r in (user.roles or [])]
        
        now = datetime.now(timezone.utc)
        expires_minutes = getattr(settings, "JWT_EXPIRE_MINUTES", 60)
        expires = now + timedelta(minutes=expires_minutes)
        
        access_payload = {
            "sub": str(user.id),
            "username": user.username,
            "roles": roles,
            "type": "access",
            "exp": int(expires.timestamp()),
            "iat": int(now.timestamp())
        }
        access_token = jwt.encode(
            access_payload, 
            settings.JWT_SECRET, 
            algorithm=settings.JWT_ALG
        )
        
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": int((now + timedelta(days=30)).timestamp()),
            "iat": int(now.timestamp())
        }
        refresh_token = jwt.encode(
            refresh_payload, 
            settings.JWT_SECRET, 
            algorithm=settings.JWT_ALG
        )
        
        return LoginOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_minutes * 60
        )

    async def refresh(self, db: Session, payload: RefreshIn) -> RefreshOut:
        """Refresh access token"""
        try:
            data = jwt.decode(
                payload.refresh_token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALG]
            )
            
            # Validate token type
            if data.get("type") != "refresh":
                raise ValueError("Not a refresh token")
            
            user_id = int(data["sub"])
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn"
            )
        
        # Get user
        user = auth_repo.get_by_id(db, user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại hoặc đã bị vô hiệu hóa"
            )
        
        # Create new access token
        roles = [r.name for r in (user.roles or [])]
        expire_minutes = getattr(settings, "JWT_EXPIRE_MINUTES", 60)
        
        access_token = _create_token(
            user_id=user.id,
            username=user.username,
            roles=roles,
            token_type="access",
            expire_minutes=expire_minutes
        )
        
        return RefreshOut(
            access_token=access_token,
            token_type="bearer",
            expires_in=expire_minutes * 60
        )

    async def me(self, db: Session, user_id: int) -> MeOut:
        """Get current user info"""
        user = auth_repo.get_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Người dùng không tồn tại"
            )
        
        roles = [r.name for r in (user.roles or [])]
        
        return MeOut(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            roles=roles,
            role=roles[0] if roles else None,
            is_active=user.is_active,
            created_at=user.created_at
        )

    async def logout(self, db: Session, token: str):
        """Logout - implement token blacklist nếu cần"""
        return {"message": "Đăng xuất thành công"}