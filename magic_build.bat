@echo off
setlocal
echo ========================================
echo   SHUKABASE MAGIC BUILDER 3000
echo ========================================

echo [CLEANUP] Killing zombie processes...
taskkill /F /IM python.exe /IM rag_api_server.exe /IM SHUKABASE.exe /IM app.exe /T 2>nul
echo Done.

echo [CLEANUP] Removing old build artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist src-tauri\target rmdir /s /q src-tauri\target
if exist src-tauri\rag_api_server.exe del /f /q src-tauri\rag_api_server.exe
echo Done.

:: 1. Check/Build Backend ONE TIME
echo.
echo [STEP 1] Building Python Backend...
:: Activate venv if needed
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
pyinstaller --clean rag_api_server.spec
if %errorlevel% neq 0 (
    echo [ERROR] Python build failed!
    pause
    exit /b %errorlevel%
)
echo Copying backend to src-tauri...
copy /Y dist\rag_api_server.exe src-tauri\rag_api_server.exe

:: Ensure builds folder exists
if not exist builds mkdir builds

:: 2. Build EN
echo.
echo [STEP 2] Building ENGLISH Version...
set SHUKABASE_DATA_ID=1QkEi1D5SisVwJTGSpje_qNyIGnt6eTT4
set SHUKABASE_LANG=en
call npm run tauri:build
if %errorlevel% neq 0 exit /b %errorlevel%
move /Y src-tauri\target\release\bundle\nsis\SHUKABASE_0.1.0_x64-setup.exe builds\SHUKABASE_EN_0.1.0_x64-setup.exe

:: 3. Build RU
echo.
echo [STEP 3] Building RUSSIAN Version...
set SHUKABASE_DATA_ID=1kLZ3e0x2i2ivaPZgKSL1NChmxZh5adKG
set SHUKABASE_LANG=ru
call npm run tauri:build
if %errorlevel% neq 0 exit /b %errorlevel%
move /Y src-tauri\target\release\bundle\nsis\SHUKABASE_0.1.0_x64-setup.exe builds\SHUKABASE_RU_0.1.0_x64-setup.exe

:: 4. Build MULTI
echo.
echo [STEP 4] Building MULTILINGUAL Version...
set SHUKABASE_DATA_ID=1eqZDHhw2HbpaiWydGZXKvTPJf6EIShA0
set SHUKABASE_LANG=all
call npm run tauri:build
if %errorlevel% neq 0 exit /b %errorlevel%
move /Y src-tauri\target\release\bundle\nsis\SHUKABASE_0.1.0_x64-setup.exe builds\SHUKABASE_Multi_0.1.0_x64-setup.exe

echo.
echo ========================================
echo   ✨ MAGIC FINISHED! ✨
echo   Check 'builds' folder.
echo ========================================
pause
