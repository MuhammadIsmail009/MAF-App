from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import files, analysis, alerts, reports
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-Based Memory Forensics Analyzer",
        version="1.0.0",
        description="Backend API for RAM dump analysis, Volatility integration, ML/DL anomaly detection, and reporting.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(files.router, prefix="/api", tags=["files"])
    app.include_router(analysis.router, prefix="/api", tags=["analysis"])
    app.include_router(alerts.router, prefix="/api", tags=["alerts"])
    app.include_router(reports.router, prefix="/api", tags=["reports"])

    return app


app = create_app()


@app.on_event("startup")
async def on_startup() -> None:
    # Initialize database and run any migrations/bootstrap
    await init_db()


