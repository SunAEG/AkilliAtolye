"""
Authentication endpoint - Mock/Basic Login
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import asyncpg

from app.api.deps import get_db
from app.models.user import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login", summary="Kullanıcı Girişi (Mock)")
async def login(req: LoginRequest, conn: asyncpg.Connection = Depends(get_db)):
    """
    Kullanıcı girişi yapar. Gerçekte şifre doğrulaması veya JWT üretimi yapılmalıdır.
    Bu aşamada sadece JSONB içinden emaili doğrular.
    """
    user = await UserRepository.get_by_email(conn, req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz email veya şifre")

    # TODO: Gerçek şifre kontrolü burada yapılmalıdır
    
    return {
        "status": "success",
        "message": "Giriş başarılı",
        "token": f"mock_token_for_{user.id}",
        "user": {
            "id": user.id,
            "email": user.value.get("email"),
            "role": user.group_type,
            "name": user.value.get("name", ""),
            "surname": user.value.get("surname", "")
        }
    }
