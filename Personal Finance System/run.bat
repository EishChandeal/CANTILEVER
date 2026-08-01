@echo off
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt -q
python src/main.py
pause
