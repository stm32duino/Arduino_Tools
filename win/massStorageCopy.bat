@echo off

rem Exit codes for xcopy
rem code | Description
rem  0   | Files were copied without error.
rem  1   | No files were found to copy.
rem  2   | The user pressed CTRL+C to terminate xcopy.
rem  4   | Initialization error occurred. There is not enough memory or disk space, or you entered an invalid drive name or invalid syntax on the command line.
rem  5   | Disk write error occurred.

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
for /F "skip=1 tokens=*" %%a in ('WMIC LOGICALDISK where "volumename like '%~1'" get deviceid 2^>NUL') do if not defined id set id=%%a
  call set "deviceid=%%id: =%%"
  if not "%deviceid%" == "" (
    XCOPY %SRC_PARSE% %deviceid% /Y /Q
    if  !errorlevel! == 0 (echo Upload complete on %1 ^(%deviceid%^))
    exit !errorlevel!)
goto :eof
