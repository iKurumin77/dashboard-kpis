@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  Dashboard KPIs - Generador de instalador
echo ==========================================

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: No se encontro el entorno virtual .venv
    echo Ejecute primero: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements-dev.txt
    exit /b 1
)

echo.
echo [1/3] Generando el icono de la aplicacion...
.venv\Scripts\python.exe assets\generate_icon.py

echo.
echo [2/3] Generando el ejecutable con PyInstaller...
.venv\Scripts\pyinstaller.exe --clean --onefile --noconfirm --name DashboardKPIs --noconsole ^
    --icon "assets\icono.ico" ^
    --add-data "config;config" ^
    --add-data "locales;locales" ^
    --add-data "data;data" ^
    --add-data "assets;assets" ^
    --add-data "src;src" ^
    --collect-all streamlit ^
    --collect-all streamlit_option_menu ^
    --collect-all plotly ^
    --collect-all fpdf ^
    --hidden-import openpyxl ^
    build\launcher.py

if not exist "dist\DashboardKPIs.exe" (
    echo ERROR: PyInstaller no genero el ejecutable. Revise los mensajes anteriores.
    exit /b 1
)
echo Ejecutable generado en dist\DashboardKPIs.exe

echo.
echo [3/3] Compilando el instalador con Inno Setup...
set "ISCC="
where ISCC.exe >nul 2>&1 && set "ISCC=ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if defined ISCC (
    "%ISCC%" "installer\instalador.iss"
    echo.
    echo Listo. Instalador generado en installer\Output\DashboardKPIsInstaller.exe
) else (
    echo Inno Setup ^(ISCC.exe^) no se encontro en este equipo.
    echo Descargue e instale Inno Setup desde https://jrsoftware.org/isdl.php
    echo Luego abra installer\instalador.iss con Inno Setup y presione "Compile".
)

endlocal
