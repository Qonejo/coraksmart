@echo off
echo ================================
echo  CorakSmart Server - Gevent Mode
echo ================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que existe requirements.txt
if not exist requirements.txt (
    echo ❌ No se encontró requirements.txt
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo 📦 Verificando dependencias...
python -c "import gevent" >nul 2>&1
if errorlevel 1 (
    echo 🔄 Instalando dependencias...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error al instalar dependencias
        pause
        exit /b 1
    )
)

echo ✅ Dependencias verificadas
echo.

REM Iniciar el servidor
echo 🚀 Iniciando servidor...
echo.
python start_server.py

pause
