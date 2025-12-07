from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertRead

router = APIRouter()


@router.post("/alerts/create", response_model=AlertRead)
async def create_alert(payload: AlertCreate, session: AsyncSession = Depends(get_session)):
    alert = Alert(
        file_id=payload.file_id,
        process_name=payload.process_name,
        pid=payload.pid,
        anomaly_score=payload.anomaly_score,
        ml_confidence=payload.ml_confidence,
        label=payload.label,
        message=payload.message,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return AlertRead.model_validate(alert)


@router.get("/alerts/list", response_model=List[AlertRead])
async def list_alerts(session: AsyncSession = Depends(get_session)):
    stmt = select(Alert).order_by(Alert.created_at.desc())
    result = await session.execute(stmt)
    alerts = result.scalars().all()
    return [AlertRead.model_validate(a) for a in alerts]


@router.get("/alerts/by_file/{file_id}", response_model=List[AlertRead])
async def alerts_by_file(file_id: int, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Alert)
        .where(Alert.file_id == file_id)
        .order_by(Alert.created_at.desc())
    )
    result = await session.execute(stmt)
    alerts = result.scalars().all()
    return [AlertRead.model_validate(a) for a in alerts]



