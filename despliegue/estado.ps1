# Estado del despliegue de un vistazo (útil por AnyDesk):
#
#   powershell -ExecutionPolicy Bypass -File despliegue\estado.ps1
#
# Contenedores y su salud, versión en marcha frente a la de GitHub, la web desde este ordenador
# y desde internet, y las últimas líneas del registro de actualizaciones.

$ErrorActionPreference = "Continue"
$raiz = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $PSScriptRoot "docker-compose.yml"
$log = Join-Path $PSScriptRoot "registros\actualizar.log"

function Probar([string]$url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 6
        return "OK ($($r.StatusCode))"
    } catch { return "NO RESPONDE ($($_.Exception.Message))" }
}

Write-Host "`n== Contenedores"
docker compose -f $compose --profile publico ps --format "table {{.Service}}\t{{.Status}}"

Write-Host "`n== Versión"
Push-Location $raiz
git fetch --quiet origin main 2>$null
Write-Host ("En marcha: " + (git log -1 --format="%h %ci %s" HEAD))
Write-Host ("En GitHub: " + (git log -1 --format="%h %ci %s" origin/main))
Pop-Location

Write-Host "`n== La web"
Write-Host ("Desde este ordenador (localhost:8601): " + (Probar "http://127.0.0.1:8601/_stcore/health"))
$config = Join-Path $raiz "portada\config.js"
if (Test-Path $config) {
    $primero = [regex]::Match((Get-Content $config -Raw), 'url:\s*"([^"]+)"').Groups[1].Value
    if ($primero) { Write-Host ("Desde internet ($primero): " + (Probar "$primero/_stcore/health")) }
}

Write-Host "`n== Últimas actualizaciones"
if (Test-Path $log) { Get-Content $log -Tail 8 } else { Write-Host "(todavía ninguna)" }
