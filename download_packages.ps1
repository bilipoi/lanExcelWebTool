# 离线安装依赖脚本
# 在有网络的环境中运行此脚本下载所有依赖包

Write-Host "========================================" -ForegroundColor Green
Write-Host "  下载离线依赖包" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""

# 创建 packages 目录
$packagesDir = "packages"
if (-not (Test-Path $packagesDir)) {
    New-Item -ItemType Directory -Path $packagesDir | Out-Null
}

Write-Host "正在下载依赖包到 packages/ 目录..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟，请耐心等待..." -ForegroundColor Gray
Write-Host ""

# 下载依赖
pip download -r requirements.txt -d $packagesDir

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] 依赖包下载完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "packages/ 目录内容：" -ForegroundColor Cyan
    Get-ChildItem $packagesDir | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  下一步：将整个项目目录复制到目标机器" -ForegroundColor Green
    Write-Host "========================================"
} else {
    Write-Host ""
    Write-Host "[错误] 下载失败，请检查网络连接" -ForegroundColor Red
}

Write-Host ""
pause