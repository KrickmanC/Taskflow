$ErrorActionPreference = "Stop"

function Assert-Command {
    param(
        [string]$Name,
        [string]$InstallHint
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "$Name not found. $InstallHint"
    }
}

function Assert-PortFree {
    param([int]$Port)

    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Warning "Port $Port is already in use."
    }
}

Write-Host "[Taskflow] Running preflight checks"

Assert-Command "python" "Install Python 3.12"
Assert-Command "node" "Install Node.js 22"
Assert-Command "pnpm" "Enable Corepack or install pnpm"
Assert-Command "psql" "Install PostgreSQL"
Assert-Command "rabbitmqctl" "Install RabbitMQ"

Assert-PortFree 8000
Assert-PortFree 3000
Assert-PortFree 3001
Assert-PortFree 3002
Assert-PortFree 3100
Assert-PortFree 9000
Assert-PortFree 9090

Write-Host "[Taskflow] Preflight checks completed"
