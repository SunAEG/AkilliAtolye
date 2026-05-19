"""
Roles CRUD router — /api/v1/roles
"""
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

from app.api.deps import get_db
from app.models.role import RoleRepository

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", summary="Tüm rolleri listele")
async def list_roles(conn: asyncpg.Connection = Depends(get_db)):
    roles = await RoleRepository.get_all(conn)
    return {"data": [r.to_dict() for r in roles], "count": len(roles)}


@router.get("/{role_id}", summary="Rolü ID ile getir")
async def get_role(role_id: int, conn: asyncpg.Connection = Depends(get_db)):
    role = await RoleRepository.get_by_id(conn, role_id)
    if not role:
        raise HTTPException(404, detail="Rol bulunamadı")
    return role.to_dict()


@router.post("/", summary="Yeni rol oluştur", status_code=201)
async def create_role(payload: dict, conn: asyncpg.Connection = Depends(get_db)):
    payload.setdefault("screen_permissions", [])
    role = await RoleRepository.create(conn, payload)
    return role.to_dict()


@router.put("/{role_id}", summary="Rol güncelle")
async def update_role(
    role_id: int, payload: dict, conn: asyncpg.Connection = Depends(get_db)
):
    role = await RoleRepository.update(conn, role_id, payload)
    if not role:
        raise HTTPException(404, detail="Rol bulunamadı")
    return role.to_dict()


@router.delete("/{role_id}", summary="Rol sil", status_code=204)
async def delete_role(role_id: int, conn: asyncpg.Connection = Depends(get_db)):
    deleted = await RoleRepository.delete(conn, role_id)
    if not deleted:
        raise HTTPException(404, detail="Rol bulunamadı")


@router.post("/{role_id}/screens/{screen_id}", summary="Role ekran ata")
async def assign_screen(
    role_id: int,
    screen_id: int,
    payload: dict = {},
    conn: asyncpg.Connection = Depends(get_db),
):
    try:
        role = await RoleRepository.assign_screen(
            conn,
            role_id,
            screen_id,
            can_create=payload.get("can_create", True),
            can_read=payload.get("can_read", True),
            can_update=payload.get("can_update", False),
            can_delete=payload.get("can_delete", False),
            file_types=payload.get("allowed_file_types"),
        )
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    return role.to_dict()


@router.delete("/{role_id}/screens/{screen_id}", summary="Rolden ekran yetkisini kaldır")
async def remove_screen(
    role_id: int, screen_id: int, conn: asyncpg.Connection = Depends(get_db)
):
    role = await RoleRepository.remove_screen(conn, role_id, screen_id)
    if not role:
        raise HTTPException(404, detail="Rol bulunamadı")
    return role.to_dict()
