from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.file import MemoryFile
from app.models.analysis import AnalysisResult
from app.models.alert import Alert
from app.reports.pdf import build_pdf_report
from app.utils.chain_of_custody import log_event

router = APIRouter()


@router.get("/report/{file_id}")
async def get_report(
    file_id: int,
    analyst_name: str = Query(default=""),
    session: AsyncSession = Depends(get_session),
):
    file_obj = await session.get(MemoryFile, file_id)
    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found.",
        )

    stmt = (
        select(AnalysisResult)
        .where(AnalysisResult.file_id == file_id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis results found for this file.",
        )

    stmt_alerts = select(Alert).where(Alert.file_id == file_id).order_by(Alert.created_at.asc())
    alerts_res = await session.execute(stmt_alerts)
    alerts = alerts_res.scalars().all()

    metadata = {
        "filename": file_obj.filename,
        "sha256": file_obj.sha256,
        "size_bytes": file_obj.size_bytes,
        "case_id": file_obj.case_id,
        "timestamp": file_obj.created_at.isoformat(),
    }

    pdf_bytes = build_pdf_report(
        metadata=metadata,
        volatility_output=analysis.volatility_output,
        ml_output=analysis.ml_output,
        dl_output=analysis.dl_output,
        alerts=[
            {
                "process_name": a.process_name,
                "pid": a.pid,
                "anomaly_score": a.anomaly_score,
                "ml_confidence": a.ml_confidence,
                "label": a.label,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ],
        analyst_name=analyst_name,
    )

    await log_event(
        session,
        event_type="report",
        description="PDF forensic report generated.",
        file_id=file_obj.id,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{file_id}.pdf"'},
    )



