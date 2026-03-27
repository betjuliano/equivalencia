"""API — Upload endpoints (Spec.md section 10.3)"""
from __future__ import annotations
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from src.api.auth import get_current_user, get_current_user_optional, require_role, TokenData
from src.domain.enums import UserRole
from src.config import settings

router = APIRouter()


def get_upload_dir() -> Path:
    from src.main import UPLOAD_DIR
    return UPLOAD_DIR


@router.post("/uploads/pdf", status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
    upload_dir: Path = Depends(get_upload_dir),
):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Somente arquivos PDF são aceitos")

    content = await file.read()
    max_bytes = settings.max_pdf_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Arquivo excede o limite de {settings.max_pdf_size_mb}MB")

    upload_id = str(uuid.uuid4())
    save_path = upload_dir / f"{upload_id}.pdf"
    save_path.write_bytes(content)

    return {
        "upload_id": upload_id,
        "path": f"data/uploads/pdf/{upload_id}.pdf",
        "filename": file.filename,
    }
