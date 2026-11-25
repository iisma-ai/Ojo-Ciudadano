# Registra la tarea programada «OjoCiudadano-actualizar»: cada minuto mira si main ha cambiado en
# GitHub y, si es así, pone en marcha la versión nueva (actualizar.ps1). No abre ventanas.
#
#   powershell -ExecutionPolicy Bypass -File despliegue\registrar_tarea.ps1            registrar
#   powershell -ExecutionPolicy Bypass -File despliegue\registrar_tarea.ps1 -Quitar    borrarla
#
# Funciona mientras tu sesión de Windows esté iniciada (Docker Desktop también lo necesita).

param([switch]$Quitar)
$nombre = "OjoCiudadano-actualizar"

if ($Quitar) {
    Unregister-ScheduledTask -TaskName $nombre -Confirm:$false
    Write-Host "Tarea $nombre borrada."
    exit 0
}

$lanzador = Join-Path $PSScriptRoot "ejecutar_oculto.vbs"
$accion = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$lanzador`""
# Cada minuto desde ahora y, tras un reinicio, otra vez cada minuto desde que inicies sesión.
$cadaMinuto = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 1)
$alIniciar = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$alIniciar.Repetition = $cadaMinuto.Repetition
$disparador = @($cadaMinuto, $alIniciar)
$ajustes = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

Register-ScheduledTask -TaskName $nombre -Action $accion -Trigger $disparador -Settings $ajustes `
    -Description "Ojo Ciudadano: pone en marcha la última versión de main (despliegue\actualizar.ps1)." `
    -Force | Out-Null
Start-ScheduledTask -TaskName $nombre
Write-Host "Tarea $nombre registrada y lanzada. Registro: despliegue\registros\actualizar.log"
