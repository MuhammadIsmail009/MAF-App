from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.analysis import AnalysisResult
from app.models.file import MemoryFile
from app.models.alert import Alert
from app.schemas.analysis import AnalysisResultRead, ProcessPrediction
from app.utils.chain_of_custody import log_event
from app.volatility.service import run_volatility_plugins
from app.ml.pipeline import run_ml_pipeline
from app.dl.text_model import analyze_strings

router = APIRouter()


@router.post("/analyze/{file_id}", response_model=AnalysisResultRead)
async def analyze_file(file_id: int, session: AsyncSession = Depends(get_session)):
    file_obj = await session.get(MemoryFile, file_id)
    if not file_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found.",
        )

    dump_path = Path(file_obj.stored_path)
    if not dump_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stored dump path does not exist on server.",
        )

    try:
        volatility_output = run_volatility_plugins(dump_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Volatility analysis failed: {exc}",
        ) from exc

    # ML pipeline
    ml_output = run_ml_pipeline(volatility_output)

    # DL text model on cmdline strings
    cmd_strings = [c.get("cmdline", "") for c in volatility_output.get("cmdline", []) if c]
    dl_output = analyze_strings(cmd_strings)

    max_anomaly_score = float(ml_output.get("max_anomaly_score", 0.0))

    analysis = AnalysisResult(
        file_id=file_obj.id,
        status="completed",
        summary="Automated analysis completed.",
        volatility_output=volatility_output,
        ml_output=ml_output,
        dl_output=dl_output,
        max_anomaly_score=max_anomaly_score,
    )
    session.add(analysis)
    await session.commit()
    await session.refresh(analysis)

    await log_event(
        session,
        event_type="analysis",
        description="Automated analysis executed.",
        file_id=file_obj.id,
    )

    # ALERT LOGIC: anomaly_score > 0.7 OR prediction_label == 'malicious'
    proc_preds: List[dict] = ml_output.get("processes") or []
    alerts: List[Alert] = []
    for p in proc_preds:
        if p["anomaly_score"] > 0.7 or p["label"] == "malicious":
            alert = Alert(
                file_id=file_obj.id,
                process_name=p["name"],
                pid=p["pid"],
                anomaly_score=p["anomaly_score"],
                ml_confidence=p["confidence"],
                label=p["label"],
                message=f"Malicious or anomalous process detected: {p['name']} (PID {p['pid']})",
            )
            session.add(alert)
            alerts.append(alert)

    if alerts:
        await session.commit()
        for a in alerts:
            await log_event(
                session,
                event_type="alert",
                description=(
                    f"Alert triggered for process {a.process_name} "
                    f"(PID {a.pid}) anomaly={a.anomaly_score:.2f}"
                ),
                file_id=file_obj.id,
            )

    processes = [
        ProcessPrediction(
            pid=p["pid"],
            ppid=p["ppid"],
            name=p["name"],
            anomaly_score=p["anomaly_score"],
            confidence=p["confidence"],
            label=p["label"],
            features=p["features"],
        )
        for p in proc_preds
    ]

    return AnalysisResultRead(
        id=analysis.id,
        file_id=analysis.file_id,
        status=analysis.status,
        summary=analysis.summary,
        volatility_output=analysis.volatility_output,
        ml_output=analysis.ml_output,
        dl_output=analysis.dl_output,
        max_anomaly_score=analysis.max_anomaly_score,
        created_at=analysis.created_at,
        processes=processes,
    )


@router.get("/results/{file_id}", response_model=AnalysisResultRead)
async def get_results(file_id: int, session: AsyncSession = Depends(get_session)):
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

    ml_output = analysis.ml_output or {}
    proc_preds: List[dict] = ml_output.get("processes") or []
    processes = [
        ProcessPrediction(
            pid=p["pid"],
            ppid=p["ppid"],
            name=p["name"],
            anomaly_score=p["anomaly_score"],
            confidence=p["confidence"],
            label=p["label"],
            features=p["features"],
        )
        for p in proc_preds
    ]

    return AnalysisResultRead(
        id=analysis.id,
        file_id=analysis.file_id,
        status=analysis.status,
        summary=analysis.summary,
        volatility_output=analysis.volatility_output,
        ml_output=analysis.ml_output,
        dl_output=analysis.dl_output,
        max_anomaly_score=analysis.max_anomaly_score,
        created_at=analysis.created_at,
        processes=processes,
    )



