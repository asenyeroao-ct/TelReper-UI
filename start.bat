@echo off
chcp 65001 >nul
echo ========================================
echo Telegram 頻道報告工具 - 啟動程序
echo ========================================
echo.

echo 正在檢查虛擬環境...
if not exist "venv\Scripts\activate.bat" (
    echo 錯誤: 虛擬環境不存在，請先運行 setup.bat
    pause
    exit /b 1
)

echo 正在激活虛擬環境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 錯誤: 激活虛擬環境失敗
    pause
    exit /b 1
)

echo.
echo 正在啟動 Telegram 頻道報告工具...
python ui.py
if errorlevel 1 (
    echo.
    echo 程序運行時發生錯誤
    pause
    exit /b 1
)

echo.
echo 程序已退出
pause 