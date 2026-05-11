$ErrorActionPreference = "Stop"

$InstallDir = "C:\Program Files\Taskflow"
$DataDir = "C:\ProgramData\Taskflow"
$RepoDir = Join-Path $InstallDir "repo"
$VenvDir = Join-Path $InstallDir "venv"
$WinSWDir = Join-Path $InstallDir "winsw"
$BinDir = Join-Path $InstallDir "bin"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
New-Item -ItemType Directory -Force -Path "$DataDir\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataDir\backups" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataDir\minio" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataDir\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path $WinSWDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

Write-Host "[Taskflow] Enabling Corepack"
corepack enable

Write-Host "[Taskflow] Creating Python venv"
python -m venv $VenvDir

Write-Host "[Taskflow] Installing Python dependencies"
Push-Location "$RepoDir\apps\api"
& "$VenvDir\Scripts\python.exe" -m pip install --upgrade pip wheel setuptools
& "$VenvDir\Scripts\python.exe" -m pip install -r requirements\native.txt --compile --no-cache-dir
Pop-Location

Write-Host "[Taskflow] Installing Node dependencies"
Push-Location $RepoDir
pnpm install --frozen-lockfile
Pop-Location

Write-Host "[Taskflow] Initializing env"
& "$VenvDir\Scripts\python.exe" "$RepoDir\tools\taskflowctl\taskflowctl.py" --system init-env

$TaskflowCtl = Join-Path $BinDir "taskflowctl.cmd"
Set-Content -Path $TaskflowCtl -Value "@echo off`r`n`"$VenvDir\Scripts\python.exe`" `"$RepoDir\tools\taskflowctl\taskflowctl.py`" %*`r`n"
$MachinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($MachinePath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$MachinePath;$BinDir", "Machine")
}

Copy-Item "$DataDir\.env" "$RepoDir\.env" -Force
Copy-Item "$DataDir\api.env" "$RepoDir\apps\api\.env" -Force
Copy-Item "$DataDir\web.env" "$RepoDir\apps\web\.env" -Force
Copy-Item "$DataDir\admin.env" "$RepoDir\apps\admin\.env" -Force
Copy-Item "$DataDir\space.env" "$RepoDir\apps\space\.env" -Force
Copy-Item "$DataDir\live.env" "$RepoDir\apps\live\.env" -Force

Write-Host "[Taskflow] Building frontend"
Push-Location $RepoDir
pnpm build
Pop-Location

Write-Host "[Taskflow] Copying WinSW service XML"
Copy-Item "$RepoDir\tools\taskflowctl\templates\windows\*.xml" $WinSWDir -Force

$MinioPasswordLine = Select-String -Path "$DataDir\minio.env" -Pattern "^MINIO_ROOT_PASSWORD=" | Select-Object -First 1
if ($MinioPasswordLine) {
    $MinioPassword = $MinioPasswordLine.Line.Split("=", 2)[1].Trim('"')
    $EscapedMinioPassword = [System.Security.SecurityElement]::Escape($MinioPassword)
    $MinioXml = Join-Path $WinSWDir "taskflow-minio.xml"
    (Get-Content $MinioXml) -replace 'value="secret-key"', "value=`"$EscapedMinioPassword`"" | Set-Content $MinioXml
}

Write-Host "[Taskflow] Initializing PostgreSQL"
& "$VenvDir\Scripts\python.exe" "$RepoDir\tools\taskflowctl\taskflowctl.py" --system db-init

Write-Host "[Taskflow] Initializing RabbitMQ"
& "$VenvDir\Scripts\python.exe" "$RepoDir\tools\taskflowctl\taskflowctl.py" --system rabbitmq-init

Write-Host "[Taskflow] Registering Windows services"
& "$RepoDir\tools\install\windows\register-services.ps1"

Write-Host "[Taskflow] Running migrations"
& "$VenvDir\Scripts\python.exe" "$RepoDir\tools\taskflowctl\taskflowctl.py" --system migrate

Write-Host "[Taskflow] Initializing MinIO bucket"
& "$VenvDir\Scripts\python.exe" "$RepoDir\tools\taskflowctl\taskflowctl.py" --system minio-init

Write-Host "[Taskflow] Starting services"
& "$VenvDir\Scripts\python.exe" "$RepoDir\tools\taskflowctl\taskflowctl.py" --system start

Write-Host "[Taskflow] Installation completed"
Write-Host "Open: http://localhost:3001/god-mode/"
Write-Host "Then: http://localhost:3000/"
