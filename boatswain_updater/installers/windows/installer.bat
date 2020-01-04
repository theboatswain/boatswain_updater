::  This file is part of Boatswain.
::
::      Boatswain<https://github.com/theboatswain> is free software: you can redistribute it and/or modify
::      it under the terms of the GNU General Public License as published by
::      the Free Software Foundation, either version 3 of the License, or
::      (at your option) any later version.
::
::      Boatswain is distributed in the hope that it will be useful,
::      but WITHOUT ANY WARRANTY; without even the implied warranty of
::      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
::      GNU General Public License for more details.
::
::      You should have received a copy of the GNU General Public License
::      along with Boatswain.  If not, see <https://www.gnu.org/licenses/>.
::
::
:: Run this script with elevation
@echo off

SET UPDATE_APP_DIR=%~1
SET ORIGINAL_APP_DIR=%~2
SET STATUS_FILE=%TEMP%\boatswain-status.txt

echo Update App Dir: %UPDATE_APP_DIR%
echo Original App Dir: %ORIGINAL_APP_DIR%

call :RequestAdminElevation "%~dpfs0" %* || goto:eof

echo Starting to clean up

for /f "usebackq delims=|" %%f in (`dir /b /s /a-d "%ORIGINAL_APP_DIR%"`) do call :CleaningUpPreviousUpdate "%%f"

echo Starting to rename from %ORIGINAL_APP_DIR%

for /f "usebackq delims=|" %%f in (`dir /b /s /a-d "%ORIGINAL_APP_DIR%"`) do call :RenameCurrentRunningApp "%%f"

echo Starting to move FROM %UPDATE_APP_DIR% to %ORIGINAL_APP_DIR%

move "%UPDATE_APP_DIR%\*" "%ORIGINAL_APP_DIR%"

echo Reset permission

icacls "%ORIGINAL_APP_DIR%" /q /c /t /reset

echo Finished
echo 1 > "%STATUS_FILE%"
goto:eof

:CleaningUpPreviousUpdate
SET FILE_ABS_PATH=%~1
SET FILE_NAME=%~nx1

IF "%~x1" == ".bak" (
    echo Deleting file %FILE_ABS_PATH%
    del "%FILE_ABS_PATH%"
)
goto:eof

:RenameCurrentRunningApp
SET FILE_ABS_PATH=%~1
SET FILE_NAME=%~nx1

echo Renaming file %FILE_ABS_PATH%
ren "%FILE_ABS_PATH%" "%FILE_NAME%.bak"

goto:eof

:WaitForScriptDone
IF EXIST "%STATUS_FILE%" (goto:eof)
ping 1.0.0.0 -n 1 -w 500 >nul
goto:WaitForScriptDone

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:RequestAdminElevation FilePath %* || goto:eof
:: Credit: https://stackoverflow.com/questions/1894967/how-to-request-administrator-access-inside-a-batch-file
:: By:   Cyberponk,     v1.5 - 10/06/2016 - Changed the admin rights test method from cacls to fltmc
::          v1.4 - 17/05/2016 - Added instructions for arguments with ! char
::          v1.3 - 01/08/2015 - Fixed not returning to original folder after elevation successful
::          v1.2 - 30/07/2015 - Added error message when running from mapped drive
::          v1.1 - 01/06/2015
::
:: Func: opens an admin elevation prompt. If elevated, runs everything after the function call, with elevated rights.
:: Returns: -1 if elevation was requested
::           0 if elevation was successful
::           1 if an error occured
::
:: USAGE:
:: If function is copied to a batch file:
::     call :RequestAdminElevation "%~dpf0" %* || goto:eof
::
:: If called as an external library (from a separate batch file):
::     set "_DeleteOnExit=0" on Options
::     (call :RequestAdminElevation "%~dpf0" %* || goto:eof) && CD /D %CD%
::
:: If called from inside another CALL, you must set "_ThisFile=%~dpf0" at the beginning of the file
::     call :RequestAdminElevation "%_ThisFile%" %* || goto:eof
::
:: If you need to use the ! char in the arguments, the calling must be done like this, and afterwards you must use %args% to get the correct arguments:
::      set "args=%* "
::      call :RequestAdminElevation .....   use one of the above but replace the %* with %args:!={a)%
::      set "args=%args:{a)=!%"
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
setlocal ENABLEDELAYEDEXPANSION & set "_FilePath=%~1"
  if NOT EXIST "!_FilePath!" (echo/Read RequestAdminElevation usage information)
  :: UAC.ShellExecute only works with 8.3 filename, so use %~s1
  set "_FN=_%~ns1" & echo/%TEMP%| findstr /C:"(" >nul && (echo/ERROR: %%TEMP%% path can not contain parenthesis &pause &endlocal &fc;: 2>nul & goto:eof)
  :: Remove parenthesis from the temp filename
  set _FN=%_FN:(=%
  set _vbspath="%temp:~%\%_FN:)=%.vbs" & set "_batpath=%temp:~%\%_FN:)=%.bat"

  :: Test if we gave admin rights
  fltmc >nul 2>&1 || goto :_getElevation

  :: Elevation successful
  (if exist %_vbspath% ( del %_vbspath% )) & (if exist %_batpath% ( del %_batpath% ))
  :: Set ERRORLEVEL 0, set original folder and exit
  endlocal & CD /D "%~dp1" & ver >nul & goto:eof

  :_getElevation
  echo/Requesting elevation...
  :: Try to create %_vbspath% file. If failed, exit with ERRORLEVEL 1
  echo/Set UAC = CreateObject^("Shell.Application"^) > %_vbspath% || (echo/&echo/Unable to create %_vbspath% & endlocal &md; 2>nul &goto:eof)
  echo/UAC.ShellExecute "%_batpath%", "", "", "runas", 0 >> %_vbspath% & echo/wscript.Quit(1)>> %_vbspath%
  :: Try to create %_batpath% file. If failed, exit with ERRORLEVEL 1
  echo/@%* ^> %TEMP%\boatswain-installer.log > "%_batpath%" || (echo/&echo/Unable to create %_batpath% & endlocal &md; 2>nul &goto:eof)
  echo/@if %%errorlevel%%==9009 (echo/^&echo/Admin user could not read the batch file. If running from a mapped drive or UNC path, check if Admin user can read it.)^&echo/^& @if %%errorlevel%% NEQ 0 pause >> "%_batpath%"

  echo/&echo/_batpath = %_batpath%

  :: Run %_vbspath%, that calls %_batpath%, that calls the original file
  %_vbspath% && (echo/&echo/Failed to run VBscript %_vbspath% &endlocal &md; 2>nul & goto:eof)

  call :WaitForScriptDone
  del "%STATUS_FILE%"

  :: Vbscript has been run, exit with ERRORLEVEL -1
  echo/&echo/Elevation was requested on a new CMD window &endlocal &fc;: 2>nul & goto:eof
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
