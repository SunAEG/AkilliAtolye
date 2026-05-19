"""
Users CRUD router — /api/v1/endpoints/users
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import asyncpg

from app.api.deps import get_db
from app.models.user import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


class UserMetadataUpdateRequest(BaseModel):
    key: str
    value: str | int | bool | dict | list


@router.get("/", summary="Tüm kullanıcıları listele")
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    group_type: str | None = Query(None, description="supervisor|student|school|business"),
    conn: asyncpg.Connection = Depends(get_db),
):
    users = await UserRepository.get_all(conn, limit, offset, group_type)
    return {"data": [u.to_dict() for u in users], "count": len(users)}


@router.get("/{user_id}", summary="Kullanıcıyı ID ile getir")
async def get_user(user_id: int, conn: asyncpg.Connection = Depends(get_db)):
    user = await UserRepository.get_by_id(conn, user_id)
    if not user:
        raise HTTPException(404, detail="Kullanıcı bulunamadı")
    return user.to_dict()


from app.core.rabbitmq import get_rpc

@router.post("/", summary="Yeni kullanıcı oluştur", status_code=201)
async def create_user(payload: dict, conn: asyncpg.Connection = Depends(get_db)):
    group_type = payload.pop("group_type", "student")
    user = await UserRepository.create(conn, group_type, payload)
    
    # RabbitMQ RPC üzerinden anında loglama işlemi
    try:
        rpc = get_rpc()
        rpc_result = await rpc.call(
            "process_crud_log",
            kwargs={
                "action": "CREATE",
                "table_name": "users",
                "record_id": user.id,
                "details": {"group_type": group_type}
            }
        )
        user_dict = user.to_dict()
        user_dict["rpc_log_status"] = rpc_result
        return user_dict
    except Exception as e:
        # Eğer RPC çalışmazsa işlemi iptal etmeyiz ama hata bilgisini ekleriz
        user_dict = user.to_dict()
        user_dict["rpc_log_status"] = {"status": "error", "message": str(e)}
        return user_dict


@router.put("/{user_id}", summary="Kullanıcı güncelle")
async def update_user(
    user_id: int, payload: dict, conn: asyncpg.Connection = Depends(get_db)
):
    payload.pop("password_hash", None)  # Şifre bu endpoint'ten güncellenmez
    user = await UserRepository.update(conn, user_id, payload)
    if not user:
        raise HTTPException(404, detail="Kullanıcı bulunamadı")
    return user.to_dict()


@router.put("/{user_id}/metadata", summary="Kullanıcı JSONB metadata güncelle")
async def update_user_metadata(
    user_id: int, req: UserMetadataUpdateRequest, conn: asyncpg.Connection = Depends(get_db)
):
    """
    Kullanıcıya ait JSONB veri alanına dinamik değer ekler/günceller.
    Örn: Tercihleri, özel kısıtlamaları veya profil detaylarını saklamak için kullanılır.
    """
    update_payload = {req.key: req.value}
    user = await UserRepository.update(conn, user_id, update_payload)
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {"message": "Kullanıcı metadata güncellendi", "user": user.to_dict()}


@router.delete("/{user_id}", summary="Kullanıcı sil", status_code=204)
async def delete_user(user_id: int, conn: asyncpg.Connection = Depends(get_db)):
    deleted = await UserRepository.delete(conn, user_id)
    if not deleted:
        raise HTTPException(404, detail="Kullanıcı bulunamadı")


@router.get("/{user_id}/screens", summary="Kullanıcının erişebileceği ekranlar")
async def get_user_screens(user_id: int, conn: asyncpg.Connection = Depends(get_db)):
    screens = await UserRepository.get_screens(conn, user_id)
    return {"user_id": user_id, "screens": screens}
