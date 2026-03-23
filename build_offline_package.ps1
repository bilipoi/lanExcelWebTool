# 局域网多人 Excel 编辑器 - 离线打包工具
# 使用说明：
# 1. 在有网络的环境中运行此脚本
# 2. 将生成的 zip 文件复制到离线服务器
# 3. 解压后运行 start.bat 即可使用

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  局域网 Excel 编辑器 - 离线打包工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查当前目录
if (-not (Test-Path "app.py")) {
    Write-Host "[错误] 请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 步骤 1：下载依赖
Write-Host "步骤 1/3: 下载 Python 依赖包..." -ForegroundColor Yellow
$packagesDir = "packages"
if (-not (Test-Path $packagesDir)) {
    New-Item -ItemType Directory -Path $packagesDir | Out-Null
}

pip download -r requirements.txt -d $packagesDir
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 依赖下载失败，请检查网络连接" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] 依赖包已下载到 packages/ 目录" -ForegroundColor Green
Write-Host ""

# 步骤 2：检查前端依赖
Write-Host "步骤 2/3: 检查前端依赖..." -ForegroundColor Yellow
$frontendFiles = @(
    "static/css/handsontable.full.min.css",
    "static/js/handsontable.full.min.js",
    "static/js/socket.io.min.js"
)

$allExist = $true
foreach ($file in $frontendFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "  [缺失] $file" -ForegroundColor Red
        $allExist = $false
    } else {
        Write-Host "  [OK] $file" -ForegroundColor Gray
    }
}

if (-not $allExist) {
    Write-Host ""
    Write-Host "[警告] 部分前端依赖缺失，运行 download_deps.py 下载" -ForegroundColor Yellow
    python download_deps.py
}

Write-Host "[OK] 前端依赖检查完成" -ForegroundColor Green
Write-Host ""

# 步骤 3：打包
Write-Host "步骤 3/3: 生成离线安装包..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "lan_excel_editor_offline_$timestamp.zip"
$excludeDirs = @("venv", "__pycache__", ".git", "data")
$excludeFiles = @("*.pyc", "*.pyo", "*.log", ".gitignore")

# 使用 Compress-Archive
$itemsToZip = Get-ChildItem -Path "." -Exclude $excludeDirs | Where-Object {
    $_.Name -notin $excludeDirs -and
    $_.Extension -notin @('.pyc', '.pyo')
}

Compress-Archive -Path $itemsToZip -DestinationPath $zipName -Force

if (Test-Path $zipName) {
    $size = (Get-Item $zipName).Length / 1MB
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  离线包生成成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "文件名: $zipName" -ForegroundColor Cyan
    Write-Host "大小: $($size.ToString('F1')) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "使用说明：" -ForegroundColor Yellow
    Write-Host "1. 将 $zipName 复制到目标服务器" -ForegroundColor White
    Write-Host "2. 解压到任意目录" -ForegroundColor White
    Write-Host "3. 安装 Python 3.9+（如果尚未安装）" -ForegroundColor White
    Write-Host "4. 运行 start.bat 启动服务" -ForegroundColor White
    Write-Host ""
    Write-Host "详细说明见 DEPLOY.md" -ForegroundColor Gray
} else {
    Write-Host "[错误] 打包失败" -ForegroundColor Red
}

Write-Host ""
pause