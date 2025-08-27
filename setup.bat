@echo off
chcp 65001 >nul
echo ========================================
echo Telegram 頻道報告工具 - 環境設置
echo ========================================
echo.

echo 正在檢查 Python 版本...
python --version
if errorlevel 1 (
    echo 錯誤: 未找到 Python，請先安裝 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo.
echo 正在創建虛擬環境...
python -m venv venv
if errorlevel 1 (
    echo 錯誤: 創建虛擬環境失敗
    pause
    exit /b 1
)

echo.
echo 正在激活虛擬環境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 錯誤: 激活虛擬環境失敗
    pause
    exit /b 1
)

echo.
echo 正在升級 pip...
python -m pip install --upgrade pip

echo.
echo 正在安裝依賴項...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 安裝依賴項失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo 環境設置完成！
echo ========================================
echo.
echo 現在可以運行 start.bat 來啟動程序
echo.
pause 