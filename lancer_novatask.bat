@echo off
setlocal
title NovaTask
cd /d "%~dp0"

set PORT=8000
set URL=http://127.0.0.1:%PORT%/

rem --- Edge present ? On ouvre l'appli dans une fenetre sans barre d'adresse
set EDGE=
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe" >nul 2>&1 && set EDGE=1

rem --- Serveur deja lance ? On ouvre simplement la fenetre
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul && goto ouvrir

rem --- Trouver Python
set PY=
where py >nul 2>&1 && set PY=py -3
if not defined PY where python >nul 2>&1 && set PY=python
if not defined PY (
  echo Python est introuvable.
  echo Installez Python 3.12 ou plus depuis python.org et cochez "Add Python to PATH".
  pause
  exit /b 1
)

rem --- Premier lancement : environnement virtuel + dependances
if not exist ".nova\Scripts\python.exe" (
  echo Premier lancement : installation en cours, patientez...
  %PY% -m venv .nova || (pause & exit /b 1)
  ".nova\Scripts\python.exe" -m pip install -r requirements.txt || (pause & exit /b 1)
)

rem --- Base de donnees a jour
".nova\Scripts\python.exe" manage.py migrate --noinput >nul

rem --- Demarrer le serveur dans une fenetre reduite (reste ouverte en cas d'erreur)
start "NovaTask - serveur" /min cmd /k ".nova\Scripts\python.exe manage.py runserver 127.0.0.1:%PORT%"

rem --- Attendre que le serveur reponde (30 s maximum)
set /a n=0
:attente
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul && goto ouvrir
set /a n+=1
if %n% GEQ 30 (
  echo Le serveur ne repond pas. Regardez la fenetre "NovaTask - serveur".
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto attente

:ouvrir
if defined EDGE (start "" msedge --app=%URL%) else (start "" "%URL%")
exit /b 0
