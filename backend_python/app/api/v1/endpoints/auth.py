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
async def login(req: LoginRequest):
    """
    Kullanıcı girişi yapar (Hardcoded Mock).
    """
    if req.email == "admin@akilliatolye.com":
        return {
            "status": "success",
            "message": "Giriş başarılı",
            "token": "mock_admin_token_123",
            "user": {
                "id": 1,
                "email": "admin@akilliatolye.com",
                "role": "supervisor",
                "name": "Admin",
                "surname": "Atölye"
            }
        }
    
    raise HTTPException(status_code=401, detail="Geçersiz email veya şifre")
