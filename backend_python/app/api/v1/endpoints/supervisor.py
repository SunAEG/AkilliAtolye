"""
Supervisor endpoint - Role assignment, permission management and dynamic JSONB metadata
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import asyncpg

from app.api.deps import get_db
from app.models.role import RoleRepository

router = APIRouter(prefix="/supervisor", tags=["supervisor"])


class ScreenAssignmentRequest(BaseModel):
    can_create: bool = True
    can_read: bool = True
    can_update: bool = False
    can_delete: bool = False
    allowed_file_types: Optional[List[str]] = None


class GroupDataUpdateRequest(BaseModel):
    key: str
    value: str | int | bool | dict | list


@router.post("/roles/{role_id}/assign-screen/{screen_id}", summary="Gruba ekran ata (Supervisor)")
async def assign_screen_to_group(
    role_id: int,
    screen_id: int,
    req: ScreenAssignmentRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    Belirli bir role (gruba) dinamik olarak ekran atar ve CRUD yetkilerini düzenler.
    """
    try:
        role = await RoleRepository.assign_screen(
            conn,
            role_id,
            screen_id,
            can_create=req.can_create,
            can_read=req.can_read,
            can_update=req.can_update,
            can_delete=req.can_delete,
            file_types=req.allowed_file_types,
        )
        return {"message": "Ekran başarıyla atandı", "role": role.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/roles/{role_id}/remove-screen/{screen_id}", summary="Gruptan ekran kaldır (Supervisor)")
async def remove_screen_from_group(
    role_id: int,
    screen_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    Belirli bir rolden ekran yetkisini tamamen kaldırır.
    """
    role = await RoleRepository.remove_screen(conn, role_id, screen_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol bulunamadı veya işlem başarısız")
    return {"message": "Ekran yetkisi başarıyla kaldırıldı", "role": role.to_dict()}


@router.put("/roles/{role_id}/metadata", summary="Grup metadata güncelle (JSONB)")
async def update_group_metadata(
    role_id: int,
    req: GroupDataUpdateRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    Role ait JSONB alanını manipüle eder. Dinamik veri alanları eklenebilir.
    Örn: Öğrenci limitleri, özel kısıtlamalar vs.
    """
    update_payload = {req.key: req.value}
    role = await RoleRepository.update(conn, role_id, update_payload)
    
    if not role:
        raise HTTPException(status_code=404, detail="Rol bulunamadı")
    return {"message": "Metadata başarıyla güncellendi", "role": role.to_dict()}
