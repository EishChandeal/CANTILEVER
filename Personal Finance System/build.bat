@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM  build.bat — Build Personal Finance System into a standalone Windows .exe
REM  Usage: Double-click or run from project root.
REM  Output: dist\PersonalFinanceSystem\PersonalFinanceSystem.exe
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
if not exist .venv (
    echo Virtual environment not found. Creating...
    python -m venv .venv
)
call .venv\Scripts\activate

echo [2/3] Installing / verifying dependencies...
pip install -r requirements.txt -q

echo [3/3] Running PyInstaller...
pyinstaller --noconfirm --clean personal_finance.spec

echo.
if exist dist\PersonalFinanceSystem\PersonalFinanceSystem.exe (
    echo  BUILD SUCCESSFUL!
    echo  Executable: dist\PersonalFinanceSystem\PersonalFinanceSystem.exe
) else (
    echo  BUILD FAILED. Check the output above for errors.
)
echo.
pause
