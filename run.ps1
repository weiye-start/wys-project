$ErrorActionPreference = "Stop"
Write-Host "正在编译" -ForegroundColor Cyan

gcc wy.c -o wy.exe

if ($LASTEXITCODE -eq 0) {
    Write-Host "编译成功，正在运行…" -ForegroundColor Green
    .\wy.exe
} else {
    Write-Host "编译失败，请检查代码!" -ForegroundColor Red
}