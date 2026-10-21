#requires -Version 5.1
<#
.SYNOPSIS
    Build the EyeBreak onedir distribution and wrap it into a Windows installer.

.DESCRIPTION
    Two stages:
      1. PyInstaller build.spec  -> dist\EyeBreak\EyeBreak.exe (+ _internal)
      2. Inno Setup installer.iss -> dist\installer\EyeBreak-Setup-<version>.exe

    The version is read from VERSION and must match version_info.txt, so the
    EXE metadata and the setup metadata can never drift apart.

.PARAMETER SkipAppBuild
    Reuse an existing dist\EyeBreak build and only recompile the installer.

.EXAMPLE
    .\scripts\build_installer.ps1

.EXAMPLE
    .\scripts\build_installer.ps1 -SkipAppBuild
#>
[CmdletBinding()]
param(
    [switch]$SkipAppBuild
)

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    throw $Message
}

# ---------------------------------------------------------------- version ----
$VersionFile = Join-Path $Root 'VERSION'
if (-not (Test-Path -LiteralPath $VersionFile)) {
    Fail "VERSION not found: $VersionFile"
}

$Version = (Get-Content -LiteralPath $VersionFile -Raw).Trim()
if (-not $Version) {
    Fail "VERSION is empty: $VersionFile"
}

$Version = $Version -replace '^[vV]', ''
if ($Version -notmatch '^\d+(\.\d+){1,3}$') {
    Fail "VERSION must look like 3.3 or 3.3.1, got: '$Version'"
}

# version_info.txt drives the EXE version resource; a mismatch produces a
# release whose file says one version and whose setup says another.
$VersionInfoFile = Join-Path $Root 'version_info.txt'
if (Test-Path -LiteralPath $VersionInfoFile) {
    $VersionParts = @($Version.Split('.'))
    while ($VersionParts.Count -lt 4) { $VersionParts += '0' }
    $ExpectedTuple = ($VersionParts | ForEach-Object { [int]$_ }) -join ', '
    $VersionInfoText = Get-Content -LiteralPath $VersionInfoFile -Raw
    if ($VersionInfoText -notmatch [regex]::Escape("filevers=($ExpectedTuple)")) {
        Fail "version_info.txt does not match VERSION ($Version): expected filevers=($ExpectedTuple). Update both before building."
    }
}

Write-Host "EyeBreak $Version" -ForegroundColor Green

# -------------------------------------------------------------- app build ----
if (-not $SkipAppBuild) {
    Write-Step "Building onedir distribution with PyInstaller"

    $Python = Join-Path $Root '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $Python)) {
        $PythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
        if (-not $PythonCommand) {
            Fail "Python not found. Create .venv first: python -m venv .venv"
        }
        $Python = $PythonCommand.Source
    }

    & $Python -c "import PyInstaller" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Fail "PyInstaller is not installed for $Python. Run: $Python -m pip install -r requirements.txt pyinstaller"
    }

    & $Python -m PyInstaller build.spec --noconfirm
    if ($LASTEXITCODE -ne 0) {
        Fail "PyInstaller failed with exit code $LASTEXITCODE"
    }
}

$AppExe = Join-Path $Root 'dist\EyeBreak\EyeBreak.exe'
if (-not (Test-Path -LiteralPath $AppExe)) {
    Fail "Missing build output: $AppExe (run without -SkipAppBuild)"
}

# ------------------------------------------------------------- inno setup ----
Write-Step "Compiling installer with Inno Setup"

$IsccCandidates = @()
$IsccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($IsccCommand) { $IsccCandidates += $IsccCommand.Source }
if (${env:ProgramFiles(x86)}) {
    $IsccCandidates += (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe')
}
if ($env:ProgramFiles) {
    $IsccCandidates += (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe')
}
if ($env:LOCALAPPDATA) {
    $IsccCandidates += (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe')
}

$Iscc = $IsccCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $Iscc) {
    Fail "ISCC.exe not found. Install Inno Setup 6.3+ (winget install --id JRSoftware.InnoSetup -e) or add it to PATH."
}

& $Iscc "/DAppVersion=$Version" (Join-Path $Root 'installer.iss') 2>&1 |
    Where-Object { $_ -notmatch 'Compressing:' } |
    ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) {
    Fail "Inno Setup compilation failed with exit code $LASTEXITCODE"
}

# ---------------------------------------------------------------- summary ----
$SetupPath = Join-Path $Root "dist\installer\EyeBreak-Setup-$Version.exe"
if (-not (Test-Path -LiteralPath $SetupPath)) {
    Fail "Installer was not produced: $SetupPath"
}

$SetupFile = Get-Item -LiteralPath $SetupPath
$Hash = Get-FileHash -LiteralPath $SetupPath -Algorithm SHA256

Write-Host ""
Write-Host "Installer : $($SetupFile.FullName)"
Write-Host ("Size      : {0:N1} MB" -f ($SetupFile.Length / 1MB))
Write-Host "SHA-256   : $($Hash.Hash)"
Write-Host "App EXE   : $AppExe"
Write-Host "Done." -ForegroundColor Green