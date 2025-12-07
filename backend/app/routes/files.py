from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.file import MemoryFile
from app.schemas.file import MemoryFileRead
from app.utils.hashing import sha256_file
from app.utils.chain_of_custody import log_event

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


@router.post("/upload", response_model=MemoryFileRead)
async def upload_memory_dump(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    if not (file.filename.endswith(".raw") or file.filename.endswith(".vmem")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .raw and .vmem memory dump files are allowed.",
        )

    contents = await file.read()
    size_bytes = len(contents)
    if size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file is not allowed.",
        )

    target_path = UPLOAD_DIR / file.filename
    with target_path.open("wb") as f:
        f.write(contents)

    sha256 = sha256_file(target_path)

    mem_file = MemoryFile(
        case_id=case_id,
        filename=file.filename,
        stored_path=str(target_path),
        size_bytes=size_bytes,
        sha256=sha256,
    )
    session.add(mem_file)
    await session.commit()
    await session.refresh(mem_file)

    await log_event(
        session,
        event_type="upload",
        description=f"File uploaded: {mem_file.filename} (SHA-256={sha256})",
        file_id=mem_file.id,
    )

    return MemoryFileRead(
        id=mem_file.id,
        case_id=mem_file.case_id,
        filename=mem_file.filename,
        size_bytes=mem_file.size_bytes,
        sha256=mem_file.sha256,
        stored_path=mem_file.stored_path,
        created_at=mem_file.created_at,
    )


@router.get("/files", response_model=List[MemoryFileRead])
async def list_files(session: AsyncSession = Depends(get_session)):
    stmt = select(MemoryFile).order_by(MemoryFile.created_at.desc())
    result = await session.execute(stmt)
    files = result.scalars().all()
    return [
        MemoryFileRead(
            id=f.id,
            case_id=f.case_id,
            filename=f.filename,
            size_bytes=f.size_bytes,
            sha256=f.sha256,
            stored_path=f.stored_path,
            created_at=f.created_at,
        )
        for f in files
    ]



