"""
Log model + repository. Loglar immutable — yalnızca INSERT ve SELECT.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import asyncpg

from app.models.base import BaseRecord


@dataclass
class LogRecord(BaseRecord):

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> "LogRecord":
        return cls(
            id=row["id"],
            created_at=row["created_at"],
            value=cls._parse_value(row["value"]),
        )


class LogRepository:

    @staticmethod
    async def get_all(
        conn: asyncpg.Connection,
        limit: int = 100,
        offset: int = 0,
        action: str | None = None,
        table_name: str | None = None,
        user_id: int | None = None,
    ) -> list[LogRecord]:
        conditions = ["1=1"]
        params: list[Any] = []

        if action:
            params.append(action.upper())
            conditions.append(f"value->>'action' = ${len(params)}")
        if table_name:
            params.append(table_name)
            conditions.append(f"value->>'table_name' = ${len(params)}")
        if user_id is not None:
            params.append(str(user_id))
            conditions.append(f"value->>'user_id' = ${len(params)}")

        params += [limit, offset]
        where = " AND ".join(conditions)
        sql = f"""
            SELECT * FROM logs
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ${len(params) - 1} OFFSET ${len(params)}
        """
        rows = await conn.fetch(sql, *params)
        return [LogRecord.from_row(r) for r in rows]

    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, log_id: int) -> LogRecord | None:
        row = await conn.fetchrow("SELECT * FROM logs WHERE id = $1", log_id)
        return LogRecord.from_row(row) if row else None

    @staticmethod
    async def count(conn: asyncpg.Connection) -> int:
        return await conn.fetchval("SELECT COUNT(*) FROM logs")
