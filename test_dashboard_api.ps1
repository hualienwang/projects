# PowerShell 版本的 Dashboard API 測試腳本
# 設置編碼為 UTF-8 以正確顯示中文
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dashboard API 測試工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 測試後端連接
Write-Host "正在測試後端服務連接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 後端服務連接成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 後端服務響應異常" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 錯誤: 無法連接到後端服務" -ForegroundColor Red
    Write-Host "請確保後端服務正在運行: http://localhost:5000" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按任意鍵退出"
    exit 1
}

Write-Host ""

# 測試 1: 獲取可用圖表列表
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 1: 獲取可用圖表列表" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/charts" -UseBasicParsing
    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 2: 獲取圖表類型
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 2: 獲取圖表類型" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/chart-types" -UseBasicParsing
    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 3: 獲取角色列表
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 3: 獲取角色列表" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/roles" -UseBasicParsing
    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 4: 查詢用戶權限
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 4: 查詢用戶權限 (admin)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/permissions/admin" -UseBasicParsing
    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 5: 生成銷售趨勢圖
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 5: 生成銷售趨勢圖" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $body = @{
        chart_type = "sales_trend"
        user_role = "admin"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 6: 生成商品銷售排行
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 6: 生成商品銷售排行" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $body = @{
        chart_type = "product_ranking"
        user_role = "admin"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 7: 生成庫存狀態分佈
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 7: 生成庫存狀態分佈" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $body = @{
        chart_type = "inventory_distribution"
        user_role = "admin"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 8: 生成客戶消費分析
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 8: 生成客戶消費分析" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $body = @{
        chart_type = "customer_analysis"
        user_role = "admin"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 測試 9: 生成供應商統計
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試 9: 生成供應商統計" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $body = @{
        chart_type = "supplier_stats"
        user_role = "admin"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing

    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor White
    Write-Host $response.Content
    Write-Host "✅ 測試通過" -ForegroundColor Green
} catch {
    Write-Host "❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 所有測試完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "如果所有測試都返回 JSON 數據，說明 API 運行正常。" -ForegroundColor Cyan
Write-Host "現在可以刷新前端頁面 http://localhost:3000 查看效果。" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意鍵打開前端頁面..." -ForegroundColor Yellow
Read-Host

Start-Process "http://localhost:3000"
