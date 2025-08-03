#!/usr/bin/env powershell
<#
.SYNOPSIS
    Octopus Server Setup and Launch Script
.DESCRIPTION
    This script sets up the conda environment, installs dependencies, and starts the Octopus server.
    It handles both fresh installations and updates to existing environments.
.PARAMETER SkipEnvSetup
    Skip conda environment setup (useful if environment already exists)
.PARAMETER Port
    Port to run the server on (default: 8000)
.EXAMPLE
    .\setup_server.ps1
    .\setup_server.ps1 -SkipEnvSetup
    .\setup_server.ps1 -Port 9000
#>

param(
    [switch]$SkipEnvSetup,
    [int]$Port = 8000
)

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

# Configuration
$ENV_NAME = "octopus_server"
$PYTHON_VERSION = "3.11"
$SCRIPT_DIR = $PSScriptRoot
$SERVER_DIR = Join-Path $SCRIPT_DIR "octopus_server"

Write-Info "🐙 Octopus Server Setup Script"
Write-Info "Server Directory: $SERVER_DIR"
Write-Info "Target Port: $Port"

# Check if conda is available
try {
    $condaVersion = conda --version 2>$null
    Write-Success "Conda found: $condaVersion"
} catch {
    Write-Error "Conda not found! Please install Anaconda or Miniconda first."
    Write-Info "Download from: https://www.anaconda.com/products/distribution"
    exit 1
}

# Check if server directory exists
if (-not (Test-Path $SERVER_DIR)) {
    Write-Error "Server directory not found: $SERVER_DIR"
    Write-Info "Please ensure you're running this script from the octopus project root directory."
    exit 1
}

if (-not $SkipEnvSetup) {
    Write-Info "Setting up conda environment..."
    
    # Check if environment already exists
    $envExists = conda env list | Select-String $ENV_NAME
    
    if ($envExists) {
        Write-Warning "Environment '$ENV_NAME' already exists."
        $response = Read-Host "Do you want to recreate it? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Info "Removing existing environment..."
            conda env remove -n $ENV_NAME -y
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to remove existing environment"
                exit 1
            }
        } else {
            Write-Info "Using existing environment..."
        }
    }
    
    # Create or update environment
    if (-not $envExists -or ($response -eq 'y' -or $response -eq 'Y')) {
        Write-Info "Creating conda environment '$ENV_NAME' with Python $PYTHON_VERSION..."
        conda create -n $ENV_NAME python=$PYTHON_VERSION -y
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create conda environment"
            exit 1
        }
        Write-Success "Conda environment created successfully"
    }
    
    # Activate environment and install dependencies
    Write-Info "Installing server dependencies..."
    
    # Create a temporary batch file to handle conda activation
    $tempBatch = Join-Path $env:TEMP "octopus_server_setup.bat"
    @"
@echo off
call conda activate $ENV_NAME
if errorlevel 1 (
    echo Failed to activate conda environment
    exit /b 1
)

cd /d "$SERVER_DIR"
if errorlevel 1 (
    echo Failed to change to server directory
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements
    exit /b 1
)

echo Dependencies installed successfully
"@ | Out-File -FilePath $tempBatch -Encoding ASCII
    
    # Execute the batch file
    cmd /c $tempBatch
    $installResult = $LASTEXITCODE
    Remove-Item $tempBatch -Force
    
    if ($installResult -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
    
    Write-Success "Dependencies installed successfully"
} else {
    Write-Info "Skipping environment setup as requested"
}

# Check if playwright browsers need to be installed
$playwrightZip = Join-Path $SCRIPT_DIR "playwright_browsers.zip"
if (Test-Path $playwrightZip) {
    Write-Info "Found playwright browsers zip file, extracting..."
    
    # Determine playwright browsers directory
    $playwrightDir = Join-Path $env:USERPROFILE ".cache\ms-playwright"
    if (-not (Test-Path $playwrightDir)) {
        New-Item -ItemType Directory -Path $playwrightDir -Force | Out-Null
    }
    
    try {
        Expand-Archive -Path $playwrightZip -DestinationPath $playwrightDir -Force
        Write-Success "Playwright browsers extracted successfully"
    } catch {
        Write-Warning "Failed to extract playwright browsers: $($_.Exception.Message)"
        Write-Info "You may need to run 'playwright install' manually later"
    }
} else {
    Write-Info "No playwright browsers zip found at: $playwrightZip"
    Write-Info "If you need playwright, you may need to run 'playwright install' later"
}

# Start the server
Write-Info "Starting Octopus Server on port $Port..."
Write-Info "Press Ctrl+C to stop the server"
Write-Info "Dashboard will be available at: http://localhost:$Port/dashboard"

# Create startup batch file
$startupBatch = Join-Path $env:TEMP "octopus_server_start.bat"
@"
@echo off
title Octopus Server - Port $Port
call conda activate $ENV_NAME
if errorlevel 1 (
    echo Failed to activate conda environment
    pause
    exit /b 1
)

cd /d "$SERVER_DIR"
if errorlevel 1 (
    echo Failed to change to server directory
    pause
    exit /b 1
)

echo.
echo 🐙 Starting Octopus Server...
echo Dashboard: http://localhost:$Port/dashboard
echo API: http://localhost:$Port/api
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py --port $Port
pause
"@ | Out-File -FilePath $startupBatch -Encoding ASCII

# Execute the startup batch file
cmd /c $startupBatch

# Cleanup
Remove-Item $startupBatch -Force -ErrorAction SilentlyContinue

Write-Info "Server stopped. Goodbye! 👋"
