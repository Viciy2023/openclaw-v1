# ============================================================
# ClawMate 补丁同步脚本
# 用途：从 clawmate-main 子项目同步文件到 patches 目录
# 使用：在 huggingface-new/patches 目录下运行此脚本
# ============================================================

Write-Host "=== ClawMate 补丁同步脚本 ===" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# 定义源目录和目标目录
$clawmateRoot = "../../clawmate-main/packages/clawmate-companion"
$patchesDir = "./clawmate"

# 检查源目录是否存在
if (-not (Test-Path $clawmateRoot)) {
    Write-Host "❌ 错误：找不到 clawmate-main 目录" -ForegroundColor Red
    Write-Host "   期望路径：$clawmateRoot" -ForegroundColor Yellow
    exit 1
}

# 创建目标目录（如果不存在）
if (-not (Test-Path $patchesDir)) {
    New-Item -ItemType Directory -Path $patchesDir -Force | Out-Null
}

# 定义文件映射
$fileMappings = @(
    @{
        Source = "$clawmateRoot/src/core/types.ts"
        Target = "$patchesDir/types.ts"
        Name = "types.ts"
    },
    @{
        Source = "$clawmateRoot/src/core/prepare.ts"
        Target = "$patchesDir/prepare.ts"
        Name = "prepare.ts"
    },
    @{
        Source = "$clawmateRoot/src/plugin.ts"
        Target = "$patchesDir/plugin.ts"
        Name = "plugin.ts"
    },
    @{
        Source = "$clawmateRoot/src/video-pipeline.ts"
        Target = "$patchesDir/video-pipeline.ts"
        Name = "video-pipeline.ts"
    },
    @{
        Source = "$clawmateRoot/skills/clawmate-companion/SKILL.md"
        Target = "$patchesDir/SKILL.md"
        Name = "SKILL.md"
    },
    @{
        Source = "$clawmateRoot/skills/clawmate-companion/SKILL.zh.md"
        Target = "$patchesDir/SKILL.zh.md"
        Name = "SKILL.zh.md"
    },
    @{
        Source = "$clawmateRoot/openclaw.plugin.json"
        Target = "$patchesDir/openclaw.plugin.json"
        Name = "openclaw.plugin.json"
    }
)

Write-Host "开始同步文件..." -ForegroundColor Green
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($mapping in $fileMappings) {
    try {
        if (-not (Test-Path $mapping.Source)) {
            Write-Host "⚠️  跳过：$($mapping.Name) (源文件不存在)" -ForegroundColor Yellow
            $failCount++
            continue
        }

        Copy-Item -Path $mapping.Source -Destination $mapping.Target -Force
        Write-Host "✅ 已同步：$($mapping.Name)" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "❌ 失败：$($mapping.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "=== 同步完成 ===" -ForegroundColor Cyan
Write-Host "成功：$successCount 个文件" -ForegroundColor Green
Write-Host "失败：$failCount 个文件" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Upload files in patches/clawmate/ to Supabase" -ForegroundColor White
    Write-Host "2. Restart HuggingFace Space to apply updates" -ForegroundColor White
    Write-Host ""
    Write-Host "Supabase upload path: hf-deploy/patches/clawmate/" -ForegroundColor Cyan
}

if ($failCount -eq 0) {
    exit 0
} else {
    exit 1
}
