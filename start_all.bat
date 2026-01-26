@echo off
chcp 65001 >nul
title 瓊林圖書進銷存系統 - 一鍵啟動

echo ========================================
echo 瓊林圖書進銷存系統
echo 一鍵啟動腳本
echo ========================================
echo.

REM 檢查 Python 是否安裝
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 錯誤: 未找到 Python
    pause
    exit /b 1
)

REM 檢查 Node.js 是否安裝
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 錯誤: 未找到 Node.js
    echo 請先安裝 Node.js: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ 環境檢查通過
echo.
echo Python 版本:
python --version
echo.
echo Node.js 版本:
node --version
echo npm 版本:
npm --version
echo.

REM 檢查端口 5000 是否被占用
netstat -ano | findstr :5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  端口 5000 已被占用，正在停止舊進程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 檢查端口 3000 是否被占用
netstat -ano | findstr :3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  端口 3000 已被占用，正在停止舊進程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo ========================================
echo 正在啟動後端服務...
echo ========================================
start "Backend Server" cmd /k "python src/main.py -m http -p 5000 --host 127.0.0.1"

REM 等待後端啟動
echo 等待後端服務啟動...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 正在啟動前端服務...
echo ========================================
start "Frontend Server" cmd /k "cd frontend && npm run dev"

REM 等待前端啟動
echo 等待前端服務啟動...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ✅ 所有服務已啟動！
echo ========================================
echo.
echo 服務訪問地址：
echo.
echo 📊 後端 API 文檔 (Swagger UI):
echo    http://127.0.0.1:5000/docs
echo.
echo 🖥️  前端應用:
echo    http://127.0.0.1:3000
echo.
echo 🏥 後端健康檢查:
echo    http://127.0.0.1:5000/health
echo.
echo ========================================
echo 提示：
echo - 後端和前端服務將在單獨的窗口中運行
echo - 關閉對應的窗口即可停止服務
echo - 按 Ctrl+C 可以停止此腳本
echo ========================================
echo.

REM 保持窗口打開
:menu
echo.
echo 輸入選項：
echo   [1] 打開後端 API 文檔
echo   [2] 打開前端應用
echo   [3] 查看服務狀態
echo   [0] 退出
echo.
set /p choice=請輸入選項 (0-3):

if "%choice%"=="1" (
    start http://127.0.0.1:5000/docs
    goto menu
)
if "%choice%"=="2" (
    start http://127.0.0.1:3000
    goto menu
)
if "%choice%"=="3" (
    echo.
    echo 檢查服務狀態...
    echo.
    echo 後端服務 (端口 5000):
    netstat -ano | findstr :5000
    echo.
    echo 前端服務 (端口 3000):
    netstat -ano | findstr :3000
    echo.
    goto menu
)
if "%choice%"=="0" (
    echo.
    echo 正在退出...
    exit /b 0
)

echo.
echo 無效選項，請重新選擇
goto menu
