@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

if not exist "%PYTHON%" (
    echo [错误] 未找到 Python，请先安装 Python 3.12
    pause
    exit /b 1
)

echo 正在安装项目依赖...
"%PYTHON%" -m pip install -r requirements.txt

echo.
echo 安装完成！双击「启动.bat」即可运行项目。
pause
