@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

if not exist "%PYTHON%" (
    echo [错误] 未找到 Python，请先安装 Python 3.12
    pause
    exit /b 1
)

echo 正在启动学生成长记录系统...
echo 浏览器将自动打开 http://localhost:8501
echo 按 Ctrl+C 可停止服务
echo.

"%PYTHON%" -m streamlit run app.py

pause
