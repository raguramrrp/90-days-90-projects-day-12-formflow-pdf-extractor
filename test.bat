@echo off
setlocal

echo ======================================================================
echo  Running FormFlow Automated Test Suite (pytest)
echo ======================================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pytest tests -v
set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
if %TEST_EXIT_CODE% equ 0 (
    echo [PASS] All automated tests passed successfully!
) else (
    echo [FAIL] Test suite failed with exit code %TEST_EXIT_CODE%.
)

exit /b %TEST_EXIT_CODE%
