@ECHO off

REM Exit codes for xcopy
REM code | Description
REM  0   | Files were copied without error.
REM  1   | No files were found to copy.
REM  2   | The user pressed CTRL+C to terminate xcopy.
REM  4   | Initialization error occurred. There is not enough memory or disk space, or you entered an invalid drive name or invalid syntax on the command line.
REM  5   | Disk write error occurred.

SET SOURCE=%2
SET SRC_PARSE=%SOURCE:/=\%
SET TARGET=%4
SET TARGET=%TARGET:\=%

call :parse %TARGET%
echo %TARGET% not found. Please ensure the device is correctly connected.
exit 7

:parse
set list=%1
set list=%list:"=%

for /f "tokens=1* delims=," %%a in ("%list%") DO (
  if not "%%a" == "" call :sub %%a
  if not "%%b" == "" call :parse "%%b"
)
goto :eof


:sub
setlocal enabledelayedexpansion
for /F "skip=1 tokens=*" %%a in ('WMIC LOGICALDISK where "volumename like '%~1'" get deviceid 2^>NUL') do if not defined id set id=%%a
  call Set "deviceid=%%id: =%%"
  if not "%deviceid%" == "" (
    XCOPY %SRC_PARSE% %deviceid% /Y /Q
    if  !errorlevel! == 0 (echo Upload complete on %1 ^(%deviceid%^))   
    exit !errorlevel!)
goto :eof
