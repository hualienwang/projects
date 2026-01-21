#!/bin/bash

# 瓊林圖書儀表板 - Nginx 啟動腳本

echo "🚀 正在啟動 Nginx 服務..."

# 檢查 Nginx 是否已安裝
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx 未安裝，請先執行：sudo apt-get install nginx"
    exit 1
fi

# 檢查配置文件是否存在
if [ ! -f "qionglin-dashboard" ]; then
    echo "❌ Nginx 配置文件不存在"
    exit 1
fi

# 檢查 nginx 是否正在運行
if service nginx status | grep -q "is running"; then
    echo "⚠️  Nginx 已經在運行，先停止服務..."
    service nginx stop
    sleep 1
fi

# 測試配置文件
echo "📝 測試 Nginx 配置..."
if ! nginx -t 2>&1 | grep -q "test is successful"; then
    echo "❌ Nginx 配置測試失敗"
    nginx -t
    exit 1
fi
echo "✅ Nginx 配置測試通過"

# 啟動 Nginx
echo "🔧 啟動 Nginx 服務..."
service nginx start

# 等待服務啟動
sleep 1

# 檢查服務狀態
if service nginx status | grep -q "is running"; then
    echo "✅ Nginx 服務已成功啟動"
    echo ""
    echo "📊 儀表板訪問地址："
    echo "   - 本地訪問: http://localhost"
    echo "   - 服務器訪問: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "📝 Nginx 配置文件: /etc/nginx/sites-available/qionglin-dashboard"
    echo "📁 靜態文件目錄: /workspace/projects/dist"
    echo ""
    echo "🔧 常用命令："
    echo "   - 重啟服務: service nginx restart"
    echo "   - 停止服務: service nginx stop"
    echo "   - 查看狀態: service nginx status"
    echo "   - 測試配置: nginx -t"
    echo "   - 查看日誌: tail -f /var/log/nginx/access.log"
else
    echo "❌ Nginx 服務啟動失敗"
    echo "📋 請檢查錯誤日誌: tail -f /var/log/nginx/error.log"
    exit 1
fi
