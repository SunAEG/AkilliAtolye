"""
Logs read-only router — /api/v1/logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpg

from app.api.deps import get_db
from app.models.log import LogRepository

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", summary="Sistem loglarını listele")
async def list_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    action: str | None = Query(None, description="CREATE|UPDATE|DELETE"),
    table_name: str | None = Query(None, description="users|roles|screens"),
    user_id: int | None = Query(None),
    conn: asyncpg.Connection = Depends(get_db),
):
    logs = await LogRepository.get_all(conn, limit, offset, action, table_name, user_id)
    total = await LogRepository.count(conn)
    return {
        "data": [lg.to_dict() for lg in logs],
        "count": len(logs),
        "total": total,
    }


@router.get("/{log_id}", summary="Logu ID ile getir")
async def get_log(log_id: int, conn: asyncpg.Connection = Depends(get_db)):
    log = await LogRepository.get_by_id(conn, log_id)
    if not log:
        raise HTTPException(404, detail="Log bulunamadı")
    return log.to_dict()
