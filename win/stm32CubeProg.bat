@echo off

set ERROR=0
set STM32CP_CLI=STM32_Programmer_CLI.exe
set ADDRESS=0x8000000

:: Check tool
where /Q %STM32CP_CLI%
if %errorlevel%==0 goto :param
::Check with default path
set STM32CP=%ProgramW6432%\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin
set STM32CP86=%ProgramFiles(X86)%\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin
set PATH=%PATH%;%STM32CP%;%STM32CP86%
where /Q %STM32CP_CLI%
if %errorlevel%==0 goto :param
echo %STM32CP_CLI% not found.
echo Please install it or add ^<STM32CubeProgrammer path^>\bin' to your PATH environment:
echo https://www.st.com/en/development-tools/stm32cubeprog.html
echo Aborting!
exit 1

:param
:: Parse options
if "%~1"=="" echo Not enough arguments! & set ERROR=2 & goto :usage
if "%~2"=="" echo Not enough arguments! & set ERROR=2 & goto :usage
set FILEPATH=%~2

:: Protocol
:: 0: SWD
:: 1: Serial
:: 2: DFU
if %~1==0 goto :SWD
if %~1==1 goto :SERIAL
if %~1==2 goto :DFU
echo Protocol unknown!
set ERROR=4
goto :usage

:SWD
set PORT=SWD
set MODE=mode=UR
if "%~3"=="" (set OPTS=-rst) else (set OPTS=%3)
goto :prog

:SERIAL
if "%~3"=="" set ERROR=3 & goto :usage
set PORT=%~3

if "%~4"=="" goto :prog
shift
shift
shift
set OPTS=%*
goto :prog

:DFU
set PORT=USB1
goto :prog

:prog
%STM32CP_CLI% -c port=%PORT% %MODE% -q -d %FILEPATH% %ADDRESS% %OPTS%
exit 0

:usage
  echo %0 ^<protocol^> ^<file_path^> [OPTIONS]
  echo.
  echo protocol:
  echo   0: SWD
  echo   1: Serial
  echo   2: DFU
  echo file_path: file path name to be downloaded: (bin, hex)
  echo Options:
  echo   For SWD: -rst
  echo     -rst: Reset system (default)
  echo   For Serial: ^<com_port^> -s
  echo     com_port: serial identifier. Ex: /dev/ttyS0
  echo     -s: start automatically
  echo   For DFU: none
  exit %ERROR%
