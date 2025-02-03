Clear-Host

# Get the directory where this script is located
# $basePath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectName = "lazyllms"
$basePath = "D:\Users\Pradeep\Downloads\Documents\Code\Projects\GenerativeAI\$projectName"
$venvName = "${projectName}_venv"
$venvPath = "$basePath\$venvName"

Write-Host "🚀 Setting up LazyLLMs in: $basePath" -ForegroundColor Cyan

# Ensure Python is installed
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if (-Not $pythonInstalled) {
    Write-Host "❌ Python is not installed. Please install Python before running this script!" -ForegroundColor Red
    Exit
}

# Ensure the base project directory exists
if (-Not (Test-Path -Path $basePath)) {
    New-Item -ItemType Directory -Path $basePath -Force | Out-Null
    Write-Host "📂 Created base folder: $basePath" -ForegroundColor Green
}

# Create subfolders dynamically
$folders = @(
    "$basePath\core",
    "$basePath\cli",
    "$basePath\tests"
)

foreach ($folder in $folders) {
    if (-Not (Test-Path -Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "📂 Created folder: $folder" -ForegroundColor Cyan
    }
}

# Create necessary files
$files = @(
    "$basePath\main.py",
    "$basePath\config.yaml",
    "$basePath\requirements.txt",
    "$basePath\core\ollama_api.py",
    "$basePath\core\monitor.py",
    "$basePath\cli\commands.py",
    "$basePath\cli\tui.py",
    "$basePath\tests\test_ollama.py",
    "$basePath\tests\test_monitor.py"
)

foreach ($file in $files) {
    if (-Not (Test-Path -Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "📝 Created file: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ LazyLLMs project structure created successfully!" -ForegroundColor Green

# Create virtual environment with project name
if (-Not (Test-Path -Path $venvPath)) {
    Write-Host "🐍 Creating virtual environment: $venvName ..." -ForegroundColor Magenta
    python -m venv $venvPath
    Write-Host "✅ Virtual environment created at $venvPath" -ForegroundColor Green
}

# Activate virtual environment (Windows vs. Linux/macOS)
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Magenta
$venvActivateWin = "$venvPath\Scripts\Activate.ps1"
$venvActivateUnix = "$venvPath/bin/activate"

if (Test-Path -Path $venvActivateWin) {
    & $venvActivateWin
    Write-Host "✅ Virtual environment activated (Windows)" -ForegroundColor Green
} elseif (Test-Path -Path $venvActivateUnix) {
    Write-Host "🔧 You are on Linux/macOS. Run the following command to activate the venv:" -ForegroundColor Yellow
    Write-Host "   source $venvActivateUnix" -ForegroundColor Cyan
} else {
    Write-Host "❌ Virtual environment activation failed!" -ForegroundColor Red
}

# Write dependencies to requirements.txt
Write-Host "📌 Writing dependencies to requirements.txt..." -ForegroundColor Yellow
$requirements = @"
rich
textual
requests
psutil
pynvml
pyyaml
argparse
"@

Set-Content -Path "$basePath\requirements.txt" -Value $requirements
Write-Host "✅ requirements.txt created" -ForegroundColor Green

# Install dependencies only if not already installed
Write-Host "📦 Installing dependencies..." -ForegroundColor Magenta
if (Test-Path -Path "$basePath\requirements.txt") {
    pip install -r "$basePath\requirements.txt"
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt not found. Skipping dependency installation." -ForegroundColor Red
}

# Run the main script to verify setup
Write-Host "🚀 Running LazyLLMs to verify setup..." -ForegroundColor Cyan
python "$basePath\main.py" --help

# Navigate to project directory
Write-Host "`n📂 Changing directory to LazyLLMs project..." -ForegroundColor Yellow
Set-Location $basePath

Write-Host "`n🎉 Setup Complete! You can now run LazyLLMs using:" -ForegroundColor Green
Write-Host "   python main.py tui" -ForegroundColor Yellow
$OutputEncoding = [System.Text.UTF8Encoding]::new()

chcp 65001
