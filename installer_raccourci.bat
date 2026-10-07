@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=[Environment]::GetFolderPath('Desktop'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut($d+'\NovaTask.lnk'); $s.TargetPath='%~dp0lancer_novatask.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0nova.ico'; $s.WindowStyle=7; $s.Description='Lancer NovaTask'; $s.Save()"
echo.
echo Raccourci NovaTask cree sur le Bureau.
pause
