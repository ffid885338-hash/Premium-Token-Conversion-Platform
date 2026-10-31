from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets
from app.database import get_db
from app.models import User
from app.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class OAuthCallbackRequest(BaseModel):
    provider: str # google, facebook, vk, apple, x
    code: str
    telegram_username: str = None

class AuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    is_admin: bool

@router.post("/oauth/exchange", response_model=AuthResponse)
def handle_oauth_exchange(payload: OAuthCallbackRequest, db: Session = Depends(get_db)):
    """
    Standardized OAuth callback router. 
    Processes authorized exchange without exposing end-user passwords or intercepting raw browser credentials.
    """
    if payload.provider not in ["google", "facebook", "vk", "apple", "x"]:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

    # In production, this verifies authorization code against provider /token endpoint
    mock_provider_user_id = f"{payload.provider}_{hash(payload.code) % 1000000}"
    mock_display_name = f"{payload.provider.upper()}_User_{secrets.token_hex(2)}"

    user = db.query(User).filter(User.oauth_id == mock_provider_user_id).first()
    if not user:
        user = User(
            oauth_provider=payload.provider,
            oauth_id=mock_provider_user_id,
            username=mock_display_name,
            telegram_username=payload.telegram_username,
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token(data={"sub": user.id, "provider": user.oauth_provider})
    
    return AuthResponse(
        token=jwt_token,
        user_id=user.id,
        username=user.username,
        is_admin=user.is_admin
    )