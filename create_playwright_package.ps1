#!/usr/bin/env powershell
<#
.SYNOPSIS
    Create Playwright Browsers Package for Offline Installation
.DESCRIPTION
    This script creates a playwright_browsers.zip file containing all installed
    Playwright browser binaries for offline deployment.
.EXAMPLE
    .\create_playwright_package.ps1
#>

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Info "🎭 Playwright Browsers Package Creator"

# Determine playwright browsers directory
$playwrightDir = Join-Path $env:USERPROFILE ".cache\ms-playwright"

if (-not (Test-Path $playwrightDir)) {
    Write-Error "Playwright browsers directory not found: $playwrightDir"
    Write-Info "Please run 'playwright install' first to download browsers"
    exit 1
}

# Check if browsers exist
$browserDirs = Get-ChildItem -Path $playwrightDir -Directory
if ($browserDirs.Count -eq 0) {
    Write-Error "No browser directories found in: $playwrightDir"
    Write-Info "Please run 'playwright install' first to download browsers"
    exit 1
}

Write-Info "Found $($browserDirs.Count) browser installation(s):"
foreach ($dir in $browserDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($size / 1MB, 2)
    Write-Info "  - $($dir.Name) ($sizeMB MB)"
}

# Create the zip file
$outputZip = Join-Path $PSScriptRoot "playwright_browsers.zip"
Write-Info "Creating playwright browsers package: $outputZip"

try {
    # Remove existing zip if it exists
    if (Test-Path $outputZip) {
        Remove-Item $outputZip -Force
        Write-Info "Removed existing package"
    }
    
    # Create the zip file
    Compress-Archive -Path "$playwrightDir\*" -DestinationPath $outputZip -CompressionLevel Optimal
    
    # Get final zip size
    $zipSize = (Get-Item $outputZip).Length
    $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
    
    Write-Success "Playwright browsers package created successfully!"
    Write-Info "Package location: $outputZip"
    Write-Info "Package size: $zipSizeMB MB"
    Write-Info ""
    Write-Info "Usage:"
    Write-Info "1. Copy this zip file to your deployment package"
    Write-Info "2. Place it in the same directory as setup_server.ps1 and setup_client.ps1"
    Write-Info "3. The setup scripts will automatically extract it during installation"
    
} catch {
    Write-Error "Failed to create package: $($_.Exception.Message)"
    exit 1
}

Write-Success "Done! 🎉"
