# Install the complete local runtime on Windows 10/11 x64.
$ErrorActionPreference = 'Stop'
$skillDir = Split-Path -Parent $PSScriptRoot
if (-not $IsWindows -and $PSVersionTable.PSEdition -eq 'Core') {
    throw 'This installer is for Windows. Use setup-macos.sh on macOS.'
}
if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
    throw 'This setup supports 64-bit x86 Windows 10/11.'
}

function Refresh-ToolPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $links = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links'
    $localBin = Join-Path $env:USERPROFILE '.local\bin'
    $env:Path = (@($machine, $user, $links, $localBin) | Where-Object { $_ }) -join ';'
}

function Install-Package([string]$id) {
    Write-Host "Installing $id ..."
    & winget install --id $id --exact --source winget --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "WinGet could not install $id (exit $LASTEXITCODE)." }
    Refresh-ToolPath
}

function Find-Chrome {
    foreach ($root in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
        if ($root) {
            $candidate = Join-Path $root 'Google\Chrome\Application\chrome.exe'
            if (Test-Path $candidate) { return $candidate }
        }
    }
    return $null
}

function Ensure-FFmpegPath {
    if ((Get-Command ffmpeg -ErrorAction SilentlyContinue) -and
        (Get-Command ffprobe -ErrorAction SilentlyContinue)) { return }
    $roots = @(
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'),
        (Join-Path $env:ProgramFiles 'WinGet\Packages')
    )
    foreach ($root in $roots) {
        if (-not (Test-Path $root)) { continue }
        $binary = Get-ChildItem -Path $root -Filter ffmpeg.exe -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { Test-Path (Join-Path $_.DirectoryName 'ffprobe.exe') } |
            Select-Object -First 1
        if ($binary) {
            $binDir = $binary.DirectoryName
            $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
            if (-not $userPath) { $userPath = '' }
            if (($userPath -split ';') -notcontains $binDir) {
                $newPath = (@($userPath.TrimEnd(';'), $binDir) | Where-Object { $_ }) -join ';'
                [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
            }
            Refresh-ToolPath
            return
        }
    }
}

Refresh-ToolPath
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw 'Windows Package Manager (WinGet) is required. Install Microsoft App Installer, then rerun this script.'
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Install-Package 'astral-sh.uv'
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'uv was installed but is not on PATH. Open a new PowerShell window and rerun setup-windows.ps1.'
}
Ensure-FFmpegPath
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue) -or
    -not (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
    Install-Package 'Gyan.FFmpeg'
    Ensure-FFmpegPath
}
if (-not (Find-Chrome)) {
    Install-Package 'Google.Chrome'
}
if (-not (Find-Chrome)) {
    throw 'Google Chrome was installed but not found. Open a new PowerShell window and rerun setup-windows.ps1.'
}

Push-Location $skillDir
try {
    $python = Join-Path $skillDir '.venv\Scripts\python.exe'
    if (-not (Test-Path $python)) {
        & uv venv --python 3.12 .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create Python 3.12 environment.' }
    }
    & uv pip install --python $python -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Could not install Python dependencies.' }
    & $python scripts/check_install.py --download-model
    if ($LASTEXITCODE -ne 0) { throw 'Runtime check or Whisper model download failed.' }
    Write-Host 'Video-to-screenplay is ready.'
} finally {
    Pop-Location
}
