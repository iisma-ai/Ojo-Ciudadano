# Copia los datos que usa la web al volumen de Docker «ojo-ciudadano-datos» y reinicia la web.
# Se usa la primera vez y cada vez que se regenere la base (docs/15-despliegue.md).
#
#   powershell -ExecutionPolicy Bypass -File despliegue\cargar_datos.ps1
#   powershell -ExecutionPolicy Bypass -File despliegue\cargar_datos.ps1 -Origen D:\otra\data
#
# Solo copia lo que la web lee en marcha: la base y las cachés del catálogo, los documentos
# (pliegos y resoluciones) y los habitantes del INE. El resto de data\raw solo sirve para
# regenerar la base. La sal de seudónimos no se copia: la web no la necesita.

param(
    [string]$Origen = (Join-Path $env:USERPROFILE "Ojo-Ciudadano\data")
)
# Continue: los errores de docker y git se comprueban a mano ($LASTEXITCODE). Con «Stop», Windows
# PowerShell 5.1 corta el script cuando un programa escribe en stderr aunque sea un aviso.
$ErrorActionPreference = "Continue"
$compose = Join-Path $PSScriptRoot "docker-compose.yml"

if (-not (Test-Path (Join-Path $Origen "ojo_ciudadano.duckdb"))) {
    throw "No encuentro $Origen\ojo_ciudadano.duckdb. Indica la carpeta con -Origen."
}

Write-Host "Copiando datos de $Origen al volumen ojo-ciudadano-datos..."
docker volume create ojo-ciudadano-datos | Out-Null

# Se copia con otro nombre y se renombra al final: la web nunca ve una base a medio copiar.
$copia = @'
set -e
mkdir -p /destino/raw
cp /origen/ojo_ciudadano.duckdb /destino/.nueva.duckdb
mv -f /destino/.nueva.duckdb /destino/ojo_ciudadano.duckdb
for d in catalogo documentos ine; do
  if [ -d "/origen/raw/$d" ]; then
    rm -rf "/destino/raw/$d.nuevo"
    cp -a "/origen/raw/$d" "/destino/raw/$d.nuevo"
    rm -rf "/destino/raw/$d"
    mv "/destino/raw/$d.nuevo" "/destino/raw/$d"
  fi
done
du -sh /destino/ojo_ciudadano.duckdb /destino/raw/* 2>/dev/null
'@
docker run --rm -v "ojo-ciudadano-datos:/destino" -v "${Origen}:/origen:ro" alpine:3.20 sh -c $copia
if ($LASTEXITCODE -ne 0) { throw "La copia de datos ha fallado." }

# Si la web ya está en marcha, se reinicia para que abra la base nueva.
$enMarcha = docker compose -f $compose ps --status running --services 2>$null
if ($enMarcha -contains "web") {
    Write-Host "Reiniciando la web para que use los datos nuevos..."
    docker compose -f $compose restart web | Out-Null
}
Write-Host "Datos cargados."
