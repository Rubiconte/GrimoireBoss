@echo off
rem Construit l'appli puis l'installateur : dist\GrimoireBoss-Setup.exe (necessite Inno Setup 6)
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3.12 -m venv .venv || goto :err
.venv\Scripts\python -m pip install -q PySide6-Essentials PySide6-Addons PySide6-WebEngine pyinstaller || goto :err
.venv\Scripts\python -m PyInstaller --noconfirm --clean --onedir --windowed --name GrimoireBoss --icon "%~dp0icon.ico" ^
  --distpath build --workpath build\tmp --specpath build\tmp ^
  --add-data "%~dp0icon.ico;." --exclude-module tkinter --exclude-module PyQt6 --exclude-module PyQt5 ^
  "%~dp0grimoire_boss.py" || goto :err
set ISCC=
for %%p in ("%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe") do (
  if exist %%p set ISCC=%%~p
)
if not defined ISCC (
  echo Inno Setup 6 est introuvable. Installe-le : winget install JRSoftware.InnoSetup
  goto :err
)
"%ISCC%" /Q installer.iss || goto :err
echo.
echo Fini : dist\GrimoireBoss-Setup.exe
if /i not "%1"=="nopause" pause
exit /b 0
:err
echo La construction a echoue.
if /i not "%1"=="nopause" pause
exit /b 1
