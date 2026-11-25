# Pone en marcha la última versión de main si ha cambiado (docs/15-despliegue.md).
# Lo lanza cada minuto la tarea programada «OjoCiudadano-actualizar» (registrar_tarea.ps1).
# También se puede lanzar a mano, por ejemplo por AnyDesk:
#
#   powershell -ExecutionPolicy Bypass -File despliegue\actualizar.ps1            si hay cambios
#   powershell -ExecutionPolicy Bypass -File despliegue\actualizar.ps1 -Forzar    reconstruye igual
#
# Funciona en la CARPETA DE DESPLIEGUE (un clon aparte de la carpeta de trabajo), que solo sigue
# a main. Seguridad:
#   - construye la imagen nueva ANTES de tocar la que está en marcha: un fallo de construcción
#     no tumba la web;
#   - si la versión nueva no está sana en 2 minutos, vuelve sola a la imagen anterior;
#   - un cerrojo impide que dos actualizaciones se pisen; todo queda en registros\actualizar.log.

param([switch]$Forzar)

# Continue: los errores de docker y git se comprueban a mano ($LASTEXITCODE). Con «Stop», Windows
# PowerShell 5.1 corta el script cuando un programa escribe en stderr aunque sea un aviso.
$ErrorActionPreference = "Continue"
$raiz = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $PSScriptRoot "docker-compose.yml"
$tunel = Join-Path $PSScriptRoot "tunel.env"
$registros = Join-Path $PSScriptRoot "registros"
New-Item -ItemType Directory -Force -Path $registros | Out-Null
$log = Join-Path $registros "actualizar.log"
$cerrojo = Join-Path $registros "actualizar.lock"

function Anotar([string]$mensaje) {
    $linea = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $mensaje"
    Add-Content -Path $log -Value $linea -Encoding UTF8
    Write-Host $linea
}

function Compose {
    # Con el token del túnel, también el túnel; sin él, solo la web (pruebas en local).
    $perfil = @()
    if (Test-Path $tunel) { $perfil = @("--profile", "publico") }
    & docker compose -f $compose @perfil @args
    if ($LASTEXITCODE -ne 0) { throw "docker compose $($args -join ' ') ha fallado ($LASTEXITCODE)" }
}

function EsperarSana([int]$segundos) {
    $limite = (Get-Date).AddSeconds($segundos)
    while ((Get-Date) -lt $limite) {
        $estado = docker inspect -f "{{.State.Health.Status}}" ojo-ciudadano-web-1 2>$null
        if ($estado -eq "healthy") { return $true }
        Start-Sleep -Seconds 3
    }
    return $false
}

# Cerrojo: si otra actualización lleva menos de 15 minutos, esta no hace nada.
if ((Test-Path $cerrojo) -and ((Get-Item $cerrojo).LastWriteTime -gt (Get-Date).AddMinutes(-15))) {
    exit 0
}
Set-Content -Path $cerrojo -Value $PID

try {
    Set-Location $raiz
    git fetch --quiet origin main
    if ($LASTEXITCODE -ne 0) { throw "git fetch ha fallado (¿sin internet o sin acceso a GitHub?)" }
    $antes = (git rev-parse HEAD).Trim()
    $remoto = (git rev-parse origin/main).Trim()
    if ($antes -eq $remoto -and -not $Forzar) { exit 0 }

    Anotar "Actualizando: $($antes.Substring(0,7)) -> $($remoto.Substring(0,7))"
    # La carpeta de despliegue nunca tiene cambios propios: solo avanza hasta main.
    git merge --ff-only --quiet origin/main
    if ($LASTEXITCODE -ne 0) { throw "La carpeta de despliegue tiene cambios propios; no se actualiza." }

    # Se guarda la imagen en marcha por si hay que volver a ella.
    docker image inspect ojo-ciudadano-web:latest *> $null
    $habiaImagen = ($LASTEXITCODE -eq 0)
    if ($habiaImagen) { docker tag ojo-ciudadano-web:latest ojo-ciudadano-web:anterior | Out-Null }

    Compose build web
    Compose up -d
    if (EsperarSana 120) {
        Anotar "En marcha y sana: $($remoto.Substring(0,7)) $((git log -1 --format=%s).Trim())"
    } elseif ($habiaImagen) {
        Anotar "ERROR: la versión nueva no arranca sana. Se vuelve a la anterior."
        docker tag ojo-ciudadano-web:anterior ojo-ciudadano-web:latest | Out-Null
        Compose up -d --no-build --force-recreate web
        if (EsperarSana 120) { Anotar "Vuelta a la versión anterior: sana." }
        else { Anotar "ERROR: tampoco arranca la anterior. Revisa: docker compose logs web" }
    } else {
        Anotar "ERROR: la web no arranca sana. Revisa: docker compose logs web"
    }
}
catch {
    Anotar "ERROR: $($_.Exception.Message)"
    exit 1
}
finally {
    Remove-Item -Path $cerrojo -ErrorAction SilentlyContinue
}
