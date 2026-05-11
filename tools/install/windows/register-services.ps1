$ErrorActionPreference = "Stop"

$InstallDir = "C:\Program Files\Taskflow"
$WinSWDir = Join-Path $InstallDir "winsw"

$Services = @(
  "taskflow-redis",
  "taskflow-minio",
  "taskflow-api",
  "taskflow-worker",
  "taskflow-beat",
  "taskflow-live",
  "taskflow-web",
  "taskflow-admin",
  "taskflow-space"
)

foreach ($svc in $Services) {
    $exe = Join-Path $WinSWDir "$svc.exe"
    if (-not (Test-Path $exe)) {
        Copy-Item (Join-Path $WinSWDir "WinSW-x64.exe") $exe
    }

    Write-Host "[Taskflow] Installing service $svc"
    & $exe install
}
