@echo off
setlocal

echo ======================================================================
echo  Launching FormFlow: Intelligent PDF Form Field Extraction Pipeline
echo ======================================================================

if not exist ".venv\Scripts\streamlit.exe" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting Streamlit application on http://localhost:8501...
echo Press Ctrl+C in this terminal window to stop the application.
echo.

".venv\Scripts\streamlit.exe" run app.py --server.port 8501 --server.headless false

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Application terminated with exit code %ERRORLEVEL%.
    pause
)
