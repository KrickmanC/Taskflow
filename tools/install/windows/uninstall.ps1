$ErrorActionPreference = "Continue"

& "$PSScriptRoot\unregister-services.ps1"

$BinDir = "C:\Program Files\Taskflow\bin"
$MachinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($MachinePath) {
    $Parts = $MachinePath.Split(";") | Where-Object { $_ -and ($_ -ne $BinDir) }
    [Environment]::SetEnvironmentVariable("Path", ($Parts -join ";"), "Machine")
}

Write-Host "[Taskflow] Services removed. Application files are removed by the installer uninstaller."
