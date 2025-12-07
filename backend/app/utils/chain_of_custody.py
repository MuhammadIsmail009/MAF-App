from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.log import ChainOfCustodyLog


async def log_event(
    session: AsyncSession, event_type: str, description: str, file_id: Optional[int] = None
) -> ChainOfCustodyLog:
    log = ChainOfCustodyLog(file_id=file_id, event_type=event_type, description=description)
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def list_logs_for_file(session: AsyncSession, file_id: int):
    stmt = select(ChainOfCustodyLog).where(ChainOfCustodyLog.file_id == file_id).order_by(
        ChainOfCustodyLog.created_at.asc()
    )
    result = await session.execute(stmt)
    return result.scalars().all()



