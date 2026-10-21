@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 --version >nul 2>nul
  if not errorlevel 1 (py -3.12 one_click.py & goto done)
  py -3 one_click.py
  goto done
)
python one_click.py
:done
echo.
echo Process finished. Read messages above.
pause
