@echo off
setlocal
mkdir builds 2>nul

echo ========================================
echo   STARTING MASTER BUILD SEQUENCE
echo ========================================

REM ------------------------------------------
REM 1. EN BUILD
REM ------------------------------------------
echo.
echo [1/3] Building ENGLISH Release...
set SHUKABASE_DATA_ID=1QkEi1D5SisVwJTGSpje_qNyIGnt6eTT4
set SHUKABASE_LANG=en

echo   - Building Backend (EN)...
call .\venv\Scripts\activate.bat
pyinstaller --clean rag_api_server.spec
if %errorlevel% neq 0 exit /b %errorlevel%

echo   - Copying Backend...
copy /Y dist\rag_api_server.exe src-tauri\rag_api_server.exe

echo   - Building Tauri App (EN)...
call npm run tauri:build
if %errorlevel% neq 0 exit /b %errorlevel%

echo   - Moving Artifact...
move /Y src-tauri\target\release\bundle\nsis\SHUKABASE_0.1.0_x64-setup.exe builds\SHUKABASE_EN_0.1.0_x64-setup.exe


REM ------------------------------------------
REM 2. RU BUILD
REM ------------------------------------------
echo.
echo [2/3] Building RUSSIAN Release...
set SHUKABASE_DATA_ID=1kLZ3e0x2i2ivaPZgKSL1NChmxZh5adKG
set SHUKABASE_LANG=ru

echo   - Building Backend (RU)...
pyinstaller --clean rag_api_server.spec
if %errorlevel% neq 0 exit /b %errorlevel%

echo   - Copying Backend...
copy /Y dist\rag_api_server.exe src-tauri\rag_api_server.exe

echo   - Building Tauri App (RU)...
call npm run tauri:build
if %errorlevel% neq 0 exit /b %errorlevel%

echo   - Moving Artifact...
move /Y src-tauri\target\release\bundle\nsis\SHUKABASE_0.1.0_x64-setup.exe builds\SHUKABASE_RU_0.1.0_x64-setup.exe


REM ------------------------------------------
REM 3. MULTILINGUAL BUILD
REM ------------------------------------------
echo.
echo [3/3] Building MULTILINGUAL Release...
set SHUKABASE_DATA_ID=1eqZDHhw2HbpaiWydGZXKvTPJf6EIShA0
set SHUKABASE_LANG=all

echo   - Building Backend (Multi)...
pyinstaller --clean rag_api_server.spec
if %errorlevel% neq 0 exit /b %errorlevel%

echo   - Copying Backend...
copy /Y dist\rag_api_server.exe src-tauri\rag_api_server.exe

echo   - Building Tauri App (Multi)...
call npm run tauri:build
if %errorlevel% neq 0 exit /b %errorlevel%

echo   - Moving Artifact...
move /Y src-tauri\target\release\bundle\nsis\SHUKABASE_0.1.0_x64-setup.exe builds\SHUKABASE_Multi_0.1.0_x64-setup.exe

echo.
echo ========================================
echo   ALL BUILDS COMPLETED SUCCESSFULLY!
echo   Files are located in: builds\
echo ========================================
