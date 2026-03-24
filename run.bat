@echo off
cd /d "%~dp0"
call pip install -r requirements.txt
python main.py
pause

