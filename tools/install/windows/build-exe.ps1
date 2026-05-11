$ErrorActionPreference = "Stop"

$Inno = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WinSWDir = Join-Path $ScriptDir "winsw"
$MinioDir = Join-Path $ScriptDir "minio"

if (-not (Test-Path $Inno)) {
    throw "Inno Setup not found"
}

New-Item -ItemType Directory -Force -Path $WinSWDir | Out-Null
New-Item -ItemType Directory -Force -Path $MinioDir | Out-Null

$WinSWExe = Join-Path $WinSWDir "WinSW-x64.exe"
if (-not (Test-Path $WinSWExe)) {
    Invoke-WebRequest "https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW-x64.exe" -OutFile $WinSWExe
}

$MinioExe = Join-Path $MinioDir "minio.exe"
if (-not (Test-Path $MinioExe)) {
    Invoke-WebRequest "https://dl.min.io/server/minio/release/windows-amd64/minio.exe" -OutFile $MinioExe
}

& $Inno (Join-Path $ScriptDir "taskflow.iss")
