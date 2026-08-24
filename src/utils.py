import json
import sys
from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path.home() / ".dashboard_kpis"
USER_SETTINGS = DATA_DIR / "user_settings.json"


def get_app_root() -> Path:
    if getattr(sys, "frozen", False):
        # Prefer the installed exe's own folder (where the installer places editable
        # config/locales/data) over PyInstaller's temp extraction dir, so users can
        # actually edit config.yaml after installing.
        carpeta_exe = Path(sys.executable).resolve().parent
        if (carpeta_exe / "config" / "config.yaml").exists():
            return carpeta_exe
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return carpeta_exe
    return BASE_DIR


def get_data_dir() -> Path:
    """Writable, persistent per-user folder for logs/uploads (safe even when installed under Program Files)."""
    crear_carpeta_si_no_existe(DATA_DIR)
    return DATA_DIR


def cargar_config(ruta: str | None = None) -> dict[str, Any]:
    ruta = Path(ruta or get_app_root() / "config" / "config.yaml")
    with open(ruta, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ruta_datos_local(ruta_relativa: str) -> Path:
    return get_app_root() / ruta_relativa


def obtener_ruta_fuente(config: dict[str, Any]) -> str:
    fuente = config.get("fuente_datos", {})
    tipo = fuente.get("tipo", "excel")
    if tipo in ("excel", "csv"):
        return fuente.get("ruta", "data/ejemplo")
    if tipo == "sqlite":
        return fuente.get("sqlite", "data/ejemplo/datos.db")
    return ""


def crear_carpeta_si_no_existe(ruta: str | Path) -> None:
    path = Path(ruta)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def cargar_usuario_config(ruta: str | None = None) -> dict[str, Any]:
    ruta = Path(ruta or USER_SETTINGS)
    if not ruta.exists():
        return {}
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_usuario_config(datos: dict[str, Any], ruta: str | None = None) -> None:
    ruta = Path(ruta or USER_SETTINGS)
    crear_carpeta_si_no_existe(ruta.parent)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
