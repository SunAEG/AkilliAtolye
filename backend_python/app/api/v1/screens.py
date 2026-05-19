"""
Screens CRUD router — /api/v1/screens
"""
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpg

from app.api.deps import get_db
from app.models.screen import ScreenRepository

router = APIRouter(prefix="/screens", tags=["screens"])


@router.get("/", summary="Tüm ekranları listele")
async def list_screens(
    active_only: bool = Query(False),
    conn: asyncpg.Connection = Depends(get_db),
):
    screens = await ScreenRepository.get_all(conn, active_only)
    return {"data": [s.to_dict() for s in screens], "count": len(screens)}


@router.get("/{screen_id}", summary="Ekranı ID ile getir")
async def get_screen(screen_id: int, conn: asyncpg.Connection = Depends(get_db)):
    screen = await ScreenRepository.get_by_id(conn, screen_id)
    if not screen:
        raise HTTPException(404, detail="Ekran bulunamadı")
    return screen.to_dict()


@router.post("/", summary="Yeni ekran oluştur", status_code=201)
async def create_screen(payload: dict, conn: asyncpg.Connection = Depends(get_db)):
    payload.setdefault("is_active", True)
    screen = await ScreenRepository.create(conn, payload)
    return screen.to_dict()


@router.put("/{screen_id}", summary="Ekran güncelle")
async def update_screen(
    screen_id: int, payload: dict, conn: asyncpg.Connection = Depends(get_db)
):
    screen = await ScreenRepository.update(conn, screen_id, payload)
    if not screen:
        raise HTTPException(404, detail="Ekran bulunamadı")
    return screen.to_dict()


@router.delete("/{screen_id}", summary="Ekran sil", status_code=204)
async def delete_screen(screen_id: int, conn: asyncpg.Connection = Depends(get_db)):
    deleted = await ScreenRepository.delete(conn, screen_id)
    if not deleted:
        raise HTTPException(404, detail="Ekran bulunamadı")
