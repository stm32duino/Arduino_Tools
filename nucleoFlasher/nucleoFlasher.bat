@ECHO off

SET SOURCE=%2
SET SRC_PARSE=%SOURCE:/=\%
SET TARGET=%4

FOR %%I IN (D E F G H I J K L M N O P Q R S T U V W X Y Z) DO (
	VOL %%I: 2>NUL | FIND "%TARGET%" >NUL && SET DEST=%%I:
)

IF DEFINED DEST (
	XCOPY %SRC_PARSE% %DEST% /Y /Q >NUL
) ELSE (
	ECHO %TARGET% not found. Please ensure the device is correctly connected
	EXIT /B 1
)
