# --- CONFIGURACIÓN ---
$repoURL = "https://github.com/omarlopez7/antigravity-agents-public.git" # Reemplaza con tu URL de GitHub
$localRepoPath = "C:\src\antigravity-agents-public"
$userName = $env:USERNAME
$antigravityPath = "C:\Users\$userName\.gemini\antigravity\.agents"

# --- 1. PREPARACIÓN DE CARPETAS ---
if (-not (Test-Path "C:\src")) { New-Item -ItemType Directory -Path "C:\src" }

if (-not (Test-Path $localRepoPath)) {
    New-Item -ItemType Directory -Force -Path $localRepoPath
    Write-Host "Carpeta creada en $localRepoPath" -ForegroundColor Cyan
}

# --- 2. VÍNCULO CON ANTIGRAVITY (SYMLINK) ---
if (-not (Test-Path $antigravityPath)) {
    Write-Host "Creando enlace simbólico para Antigravity..." -ForegroundColor Yellow
    # Ejecuta CMD como admin para crear el Symlink
    Start-Process cmd -ArgumentList "/c mklink /D `"$antigravityPath`" `"$localRepoPath`"" -Verb RunAs -Wait
}

# --- 3. INICIALIZACIÓN DE GIT (Si es nuevo) ---
Set-Location $localRepoPath
if (-not (Test-Path ".git")) {
    git init
    git remote add origin $repoURL
    Write-Host "Repositorio Git inicializado." -ForegroundColor Magenta
}

# --- 4. FUNCIÓN DE SINCRONIZACIÓN MAESTRA ---
function Sync-Now {
    param ([string]$direction)
    try {
        if ($direction -eq "UP") {
            git add .
            git commit -m "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') de $env:COMPUTERNAME"
            git push origin main
            Write-Host ">>> [$(Get-Date -Format 'HH:mm')] Cambios SUBIDOS a GitHub" -ForegroundColor Green
        } else {
            git pull origin main --rebase
            Write-Host "--- [$(Get-Date -Format 'HH:mm')] Cambios DESCARGADOS de GitHub" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Error en la sincronización: $_" -ForegroundColor Red
    }
}

# --- 5. MONITOR DE CAMBIOS (WATCHER) ---
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $localRepoPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Acción cuando algo cambia localmente
$onChanged = Register-ObjectEvent $watcher "Changed" -Action { Sync-Now -direction "UP" }
$onCreated = Register-ObjectEvent $watcher "Created" -Action { Sync-Now -direction "UP" }

Write-Host "==============================================" -ForegroundColor Green
Write-Host " SISTEMA DE AGENTES ANTIGRAVITY ACTIVO " -ForegroundColor Green
Write-Host " Repositorio: $localRepoPath"
Write-Host "==============================================" -ForegroundColor Green

# --- 6. BUCLE DE DESCARGA (CADA 60 SEGUNDOS) ---
while($true) {
    Sync-Now -direction "DOWN"
    Start-Sleep -Seconds 60 # Sincroniza desde GitHub cada minuto
}