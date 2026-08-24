@echo off
setlocal enableextensions enabledelayedexpansion

title Dashboard KPIs

echo.
echo ==========================================
echo   Dashboard KPIs - Iniciando aplicacion
echo ==========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: No se encontro Python en su equipo.
    echo Instale Python 3.11 o superior desde https://www.python.org/downloads/
    echo Importante: durante la instalacion marque la casilla "Add Python to PATH".
    echo Luego vuelva a hacer doble clic en este archivo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [2/4] Preparando el entorno ^(solo la primera vez, puede tardar unos minutos^)...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Entorno ya preparado.
)

call .\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

echo [3/4] Verificando dependencias...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias. Revise su conexion a internet.
    pause
    exit /b 1
)

echo [4/4] Abriendo la aplicacion en su navegador...
start "" cmd /c "timeout /t 4 /nobreak >nul & start http://localhost:8501"

echo.
echo La aplicacion esta corriendo. NO CIERRE ESTA VENTANA mientras la use.
echo Para detener la aplicacion, cierre esta ventana.
echo.
python -m streamlit run src\app.py --server.port 8501 --server.headless true

endlocal
