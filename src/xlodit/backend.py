from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class BackendError(RuntimeError):
    pass


def libreoffice_available() -> bool:
    return shutil.which("soffice") is not None


def resolve_backend(requested: str) -> str:
    if requested == "none":
        return "none"
    if requested == "libreoffice":
        if not libreoffice_available():
            raise BackendError("LibreOffice backend is unavailable")
        return "libreoffice"
    if requested == "auto":
        return "libreoffice" if libreoffice_available() else "none"
    raise BackendError(f"Unknown backend: {requested}")


def recalculate_with_libreoffice(path: Path) -> Path:
    outdir = Path(tempfile.mkdtemp(prefix="xlodit-recalc-"))
    cmd = [
        "soffice",
        "--headless",
        "--convert-to",
        "xlsx",
        "--outdir",
        str(outdir),
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        msg = (
            proc.stderr.strip() or proc.stdout.strip() or "Unknown LibreOffice failure"
        )
        raise BackendError(msg)
    converted = outdir / path.name
    if not converted.exists():
        raise BackendError("LibreOffice did not produce an output workbook")
    return converted
