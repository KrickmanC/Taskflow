$ErrorActionPreference = "Continue"

$WinSWDir = "C:\Program Files\Taskflow\winsw"

$Services = @(
  "taskflow-space",
  "taskflow-admin",
  "taskflow-web",
  "taskflow-live",
  "taskflow-beat",
  "taskflow-worker",
  "taskflow-api",
  "taskflow-minio",
  "taskflow-redis"
)

foreach ($svc in $Services) {
    $exe = Join-Path $WinSWDir "$svc.exe"
    if (Test-Path $exe) {
        Write-Host "[Taskflow] Stopping service $svc"
        & $exe stop
        Write-Host "[Taskflow] Uninstalling service $svc"
        & $exe uninstall
    }
}
