# 2026-11-25 · Despliegue para la entrega (D-056)

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `feat/despliegue` (sale de `main` en `101a877`)

## Qué se ha hecho

- **Opciones comparadas con El Harrak:** ordenador fijo, Streamlit Community Cloud, Hugging Face Spaces, servidor alquilado, componentes separados y dominio propio. La app de Streamlit es la página y el servidor a la vez, así que separar la página de los datos no es viable para mañana. Elegido: ordenador fijo detrás de una portada con marco en Cloudflare Pages.
- **Comprobado en el ordenador fijo:** ya tiene Docker y un túnel de Cloudflare con nombre sobre `sourcia.solutions`. El de Ojo Ciudadano será otro túnel, independiente.
- **`despliegue/`:**
  - `Dockerfile`: Python 3.12 y uv 0.10.6; dependencias en su propia capa; proyecto en modo editable para que las rutas a `data/` funcionen; comprobación de salud.
  - `docker-compose.yml`: web y túnel, con reinicio automático; el túnel espera a que la web esté sana.
  - `cargar_datos.ps1`: copia al volumen solo lo que lee la web (base 1,1 GB, catálogo 29 MB, documentos 547 MB e INE) y renombra la base al final para no dejarla a medias.
  - `actualizar.ps1`: sigue a `main` con cerrojo y registro; construye antes de cambiar y vuelve atrás si la versión nueva no queda sana.
  - `registrar_tarea.ps1` y `ejecutar_oculto.vbs`: la tarea de cada minuto, sin ventanas.
  - `estado.ps1`: resumen para AnyDesk.
  Los `.ps1` van con marca UTF-8, para que Windows PowerShell 5.1 lea bien las tildes, y con comprobación a mano de los errores de `docker` y `git`.
- **`portada/`:** `index.html`, `config.js`, `_headers` y el logo. Sin `_redirects`: Cloudflare Pages, sin `404.html`, ya sirve la portada en cualquier ruta.
- **Pruebas en local:**
  - **Imagen y salud:** la imagen se construye; el contenedor queda sano y la salud responde «ok» con `access-control-allow-origin: *`; ninguna cabecera impide el marco; 4–11 ms por petición y 70 MB de memoria.
  - **La portada en otro puerto:** salta un servidor apagado; dentro del marco se ven la intro 3D y la navegación, «¿De dónde viene el dinero?» funciona y el asistente responde una pregunta preparada; el enlace directo a `/asistente` abre esa pantalla.
  - **Caídas:** con el contenedor parado, la portada avisa y reintenta; al volver se recupera sola.
- **No probado todavía:**
  - el túnel real y la portada publicada (faltan el token y el proyecto de Pages);
  - `actualizar.ps1` y `registrar_tarea.ps1` en marcha: aquí no se pueden ejecutar scripts con `-ExecutionPolicy Bypass`; están revisados con el analizador de PowerShell y sus pasos de Docker se probaron por separado.

## Siguiente paso

1. Fusionar `feat/despliegue` en `main`: la carpeta de despliegue y Cloudflare Pages leen `main`.
2. El Harrak: túnel, carpeta de despliegue, Pages y ajustes del ordenador (`docs/15-despliegue.md`).
3. Probar desde un móvil con datos: las nueve pantallas, el asistente y una caída del contenedor.
