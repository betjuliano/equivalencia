"""Infrastructure — structured logger (Spec.md section 9.8)"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_log_dir: Optional[Path] = None


def setup_logger(data_dir: Path) -> None:
    global _log_dir
    _log_dir = Path(data_dir) / "logs"
    _log_dir.mkdir(parents=True, exist_ok=True)


def _write(filename: str, record: dict) -> None:
    if _log_dir is None:
        return
    log_path = _log_dir / filename
    line = json.dumps(record, ensure_ascii=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_app(action: str, user: Optional[str] = None, endpoint: Optional[str] = None,
            resultado: Optional[str] = None, ids: Optional[list] = None) -> None:
    _write("app.log", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usuario": user, "endpoint": endpoint,
        "acao": action, "resultado": resultado, "ids_afetados": ids or [],
    })


def log_audit(action: str, user: Optional[str], ids: Optional[list] = None) -> None:
    _write("audit.log", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usuario": user, "acao": action, "ids_afetados": ids or [],
    })


def log_error(error: str, context: Optional[dict] = None) -> None:
    _write("error.log", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error, "context": context or {},
    })
