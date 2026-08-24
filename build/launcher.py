from __future__ import annotations

import contextlib
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def puerto_libre(inicio: int = 8501, fin: int = 8600) -> int:
    for puerto in range(inicio, fin + 1):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(("127.0.0.1", puerto)) != 0:
                return puerto
    raise RuntimeError("No free port found")


def obtener_ruta_app() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "src" / "app.py"


def esperar_y_abrir_navegador(puerto: int) -> None:
    """Poll the port in a background thread and open the browser once the server answers."""
    url = f"http://127.0.0.1:{puerto}"
    for _ in range(60):
        time.sleep(0.5)
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(("127.0.0.1", puerto)) == 0:
                webbrowser.open(url)
                return
    webbrowser.open(url)


def main() -> None:
    app_path = obtener_ruta_app()
    if not app_path.exists():
        raise FileNotFoundError(f"No se encontró la app en {app_path}")

    # src/app.py uses absolute imports like "from src.componentes_ui import ...",
    # which requires the project root (parent of src/) to be importable.
    proyecto_root = str(app_path.parent.parent)
    if proyecto_root not in sys.path:
        sys.path.insert(0, proyecto_root)

    puerto = puerto_libre()
    threading.Thread(target=esperar_y_abrir_navegador, args=(puerto,), daemon=True).start()

    # Run Streamlit's own CLI in-process (a frozen exe's sys.executable is not a real
    # python.exe, so spawning "python -m streamlit" as a subprocess does not work here).
    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port", str(puerto),
        "--server.headless", "true",
        "--global.developmentMode", "false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
