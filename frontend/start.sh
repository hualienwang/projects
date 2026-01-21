#!/bin/bash

echo "🚀 啟動瓊林圖書進銷存系統 - 前端開發服務器"
echo "=============================================="
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 錯誤: 未找到 Node.js，請先安裝 Node.js >= 16.x"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 錯誤: 未找到 npm"
    exit 1
fi

echo "✅ npm 版本: $(npm --version)"
echo ""

# 检查依赖是否已安装
if [ ! -d "node_modules" ]; then
    echo "📦 首次啟動，正在安裝依賴..."
    npm install
    echo ""
fi

echo "🌟 啟動開發服務器..."
echo "📍 訪問地址: http://localhost:3000"
echo "🔗 API 代理: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服務器"
echo ""

npm run dev
