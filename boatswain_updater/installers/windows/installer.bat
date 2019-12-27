@echo off

:: BatchGotAdmin
:-------------------------------------
REM
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

SET UPDATE_APP_DIR=%1
SET ORIGINAL_APP_DIR=%2

for /f "usebackq delims=|" %%f in (`dir /b /s /a-d %ORIGINAL_APP_DIR%`) do call :RenameCurrentRunningApp "%%f"
goto EndRename

:RenameCurrentRunningApp
SET FILE_ABS_PATH=%1
SET FILE_NAME=%~nx1

IF "%~x1" == ".bak" (
    del %FILE_ABS_PATH%
) ELSE (
    REN %FILE_ABS_PATH% "%FILE_NAME%.bak"
)
:EndRename

move %UPDATE_APP_DIR%\* %ORIGINAL_APP_DIR%