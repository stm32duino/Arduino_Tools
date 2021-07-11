@echo off

rem: Note %~dp0 get path of this batch file
rem: Need to change drive if My Documents is on a drive other than C:
set driverLetter=%~dp0
set driverLetter=%driverLetter:~0,2%
%driverLetter%
cd %~dp0

rem: the two line below are needed to fix path issues with incorrect slashes before the bin file name
set str=%4
set str=%str:/=\%

rem: Sending magic word to enter DFU mode
echo 1EAF > \\.\%1

rem: Delay time uses ping
ping -n 2 127.0.0.1 > nul

rem: Flashing using dfu-util
dfu-util\dfu-util -d %3 -a %2 -s 0x08000000:leave -D %str%
