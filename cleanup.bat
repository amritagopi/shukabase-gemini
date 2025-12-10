@echo off
setlocal
chcp 65001 > nul
echo 🦜 Shukabase Deep Cleaner - Глубокая очистка
echo ===================================================
echo.
echo ⚠️  ВНИМАНИЕ! Этот скрипт удалит ВСЕ данные приложения:
echo    - Настройки
echo    - Историю чатов
echo    - Скачанную базу знаний
echo    - Временные файлы
echo.
echo Нажмите любую клавишу для продолжения или закройте окно для отмены.
pause > nul

echo.
echo 🗑️  Очистка Local AppData...
rmdir /s /q "%LOCALAPPDATA%\com.shukabase.desktop" 2>nul
rmdir /s /q "%LOCALAPPDATA%\Shukabase" 2>nul
echo ✅ Local AppData очищена.

echo.
echo 🗑️  Очистка Roaming AppData...
rmdir /s /q "%APPDATA%\com.shukabase.desktop" 2>nul
rmdir /s /q "%APPDATA%\Shukabase" 2>nul
echo ✅ Roaming AppData очищена.

echo.
echo 🗑️  Очистка кэша WebView2 (Tauri)...
rmdir /s /q "%LOCALAPPDATA%\com.shukabase.desktop.WebView2" 2>nul
rmdir /s /q "%ABSPATH%\src-tauri\target" 2>nul
echo ✅ Кэш WebView2 очищен.

echo.
echo 🗑️  Очистка локальной истории (если запускали из исходников)...
if exist "chat_history" (
    echo    Найдена папка chat_history в текущей директории.
    echo    Удаляю...
    rmdir /s /q "chat_history"
)
if exist "rag_data" (
    echo    Найдена папка rag_data в текущей директории.
    echo    Удаляю...
    rmdir /s /q "rag_data"
)
echo ✅ Локальные папки очищены.

echo.
echo ===================================================
echo ✨ Все чисто! Можете запускать установщик заново.
echo ===================================================
pause
