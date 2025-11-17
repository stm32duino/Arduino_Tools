@echo off

set SOURCE=%2
set SRC_PARSE=%SOURCE:/=\%
set TARGET=%4
set TARGET=%TARGET:\=%

call :parse %TARGET%
echo %TARGET% not found. Please ensure the device is correctly connected.
exit 7

:parse
set list=%1
set list=%list:"=%

for /f "tokens=1* delims=," %%a in ("%list%") do (
  if not "%%a" == "" call :sub %%a
  if not "%%a" == "" call :nod %%a
  if not "%%b" == "" call :parse "%%b"
)
goto :eof

rem Try with the short name NOD_XXX
:nod
  setlocal enabledelayedexpansion
  echo.%~1|findstr /C:"NODE_" >nul 2>&1
  if not errorlevel 1 (
    set name=%~1
    call :sub !name:E_=_!
  )
goto :eof

:sub
setlocal enabledelayedexpansion
for /F "delims=" %%a in ('powershell -nologo -command ^
  "Get-CimInstance -ClassName 'Win32_LogicalDisk' -Filter 'DriveType = 2' | Where-Object { $_.VolumeName -eq '%~1' } | Select-Object -ExpandProperty DeviceID" 2^>NUL') do if not "%%a" == "" (
    %~dp0busybox.exe cp -f %SRC_PARSE% %%a
    if  !errorlevel! == 0 (echo Upload complete on %1 ^(%%a^))
    exit !errorlevel!)
goto :eof
