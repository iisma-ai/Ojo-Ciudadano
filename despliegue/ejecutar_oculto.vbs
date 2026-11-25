' Lanza actualizar.ps1 sin abrir ninguna ventana (la tarea programada lo ejecuta cada minuto).
' Uso: wscript.exe ejecutar_oculto.vbs
Dim carpeta
carpeta = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
CreateObject("WScript.Shell").Run "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File """ & carpeta & "\actualizar.ps1""", 0, False
