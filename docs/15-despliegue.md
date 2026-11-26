# 15 · Despliegue de la web (D-056)

Cómo está publicada Ojo Ciudadano para la entrega del 26-nov-2026, cómo se pone en marcha la
primera vez y cómo se opera si algo falla. Objetivo: que funcione estable, fluida y con poca
latencia el día de la entrega. No es un despliegue para siempre.

## Cómo está montado

```
Visitante ──> https://ojo-ciudadano.iismael.workers.dev   portada (Cloudflare, gratis)
                │  comprueba qué servidor responde y lo muestra a pantalla completa
                └──> https://oc-origen.sourcia.solutions   túnel de Cloudflare «ojo-ciudadano»
                        └──> ordenador fijo, Docker:
                               web    Streamlit: web, consultas y asistente (puerto 8501)
                               tunel  cloudflared (sin abrir puertos del router)
                               volumen ojo-ciudadano-datos: base DuckDB y cachés
```

- **Portada** (`portada/`): un HTML estático. Prueba los servidores de `portada/config.js` en
  orden, abre el primero que responde (`/_stcore/health`), lo vigila cada 20 s y, si falla dos
  veces seguidas, avisa y salta al siguiente o reintenta sola. Conserva la ruta del enlace
  (`/empresa?empresa=…` abre esa ficha). La barra del navegador muestra siempre
  `ojo-ciudadano.iismael.workers.dev`.
- **Servidor** (`despliegue/`): la app entera en un contenedor, con los datos en un volumen de
  Docker (en Windows es mucho más rápido que leer la base desde una carpeta de Windows). El túnel
  es propio de Ojo Ciudadano: no comparte nada con otros proyectos del mismo ordenador.
- **Actualización desde GitHub**: una tarea programada mira `main` cada minuto en una carpeta de
  despliegue aparte. Si ha cambiado, construye la imagen nueva **antes** de tocar la que está en
  marcha, la arranca y, si no queda sana en 2 minutos, vuelve sola a la anterior. Un cambio en
  `main` llega a la web en unos 1–2 minutos. La portada se publica sola con cada push.
- **Los datos no pasan por GitHub.** Si se regenera la base, se copia con
  `despliegue\cargar_datos.ps1` (ver «Operación»).

Medido en local: la web responde en 4–11 ms y el contenedor usa unos 70 MB en reposo.

## Puesta en marcha (una vez)

Rutas de ejemplo: carpeta de trabajo `C:\Users\harra\Ojo-Ciudadano` y carpeta de despliegue
`C:\Users\harra\OjoCiudadano-despliegue`. Todos los comandos, en PowerShell.

### 1. Túnel en Cloudflare (panel web, 5 min)

El panel de Cloudflare cambió en 2026: los túneles están en el panel principal
(`dash.cloudflare.com`, menú **Networking → Tunnels**) y las direcciones públicas se llaman
«published application routes» y se añaden en la pestaña **Routes** del túnel.

1. https://dash.cloudflare.com → la cuenta de siempre → **Networking → Tunnels** → crear un
   túnel de tipo **Cloudflared** con el nombre `ojo-ciudadano`.
2. Al crearlo, en las instrucciones de instalación (opción **Docker**) sale un comando con
   `--token eyJ…`: copia **solo el token** (lo que va después de `--token`) y guárdalo en
   `despliegue\tunel.env`. No lo subas a git.
3. Arranca el túnel (paso 2). En **Networking → Tunnels**, `ojo-ciudadano` debe salir
   **Healthy**.
4. Pulsa el túnel `ojo-ciudadano` → pestaña **Routes** → **Add route** → **Published
   application**:
   - subdominio: `oc-origen` · **Domain**: `sourcia.solutions` · ruta: vacía
   - **Service URL**: **`http://web:8501`** (el nombre del servicio de Docker, no `localhost`)
   - **Add route**. Cloudflare crea solo el registro DNS.
   Si usas otro subdominio, cámbialo también en `portada/config.js`.

### 2. Carpeta de despliegue (10 min, la primera vez tarda por la imagen)

```powershell
git clone https://github.com/iisma-ai/Ojo-Ciudadano.git C:\Users\harra\OjoCiudadano-despliegue
cd C:\Users\harra\OjoCiudadano-despliegue
Copy-Item C:\Users\harra\Ojo-Ciudadano\.env .env            # clave del asistente (no se sube)
Set-Content despliegue\tunel.env "TUNNEL_TOKEN=PEGA_AQUI_EL_TOKEN"   # no se sube (.gitignore)
powershell -ExecutionPolicy Bypass -File despliegue\cargar_datos.ps1 -Origen C:\Users\harra\Ojo-Ciudadano\data
powershell -ExecutionPolicy Bypass -File despliegue\actualizar.ps1 -Forzar
powershell -ExecutionPolicy Bypass -File despliegue\registrar_tarea.ps1
powershell -ExecutionPolicy Bypass -File despliegue\estado.ps1
```

`estado.ps1` debe decir «OK» desde este ordenador y desde internet
(`https://oc-origen.sourcia.solutions`).

### 3. Portada en Cloudflare (panel web, 10 min)

> **Dirección pública final: `https://ojo-ciudadano.iismael.workers.dev/`.** La portada quedó publicada en Cloudflare Workers, no en
> Pages: la dirección `ojo-ciudadano.pages.dev` que aparecía antes no existe. Los pasos de abajo son
> los del plan original con Pages; el resultado (el contenido de `portada/` publicado con cada push
> a `main`) es el mismo.

1. Panel de Cloudflare → **Workers & Pages → Create → Pages → Connect to Git** → autoriza
   GitHub y elige `iisma-ai/Ojo-Ciudadano`.
2. Project name: **`ojo-ciudadano`** (si está cogido: `ojociudadano`, `ojo-ciudadano-madrid`…
   y la dirección cambia en consecuencia). Production branch: **`main`**.
3. Framework preset: **None** · Build command: **vacío** · Build output directory:
   **`portada`** → **Save and Deploy**.
4. Abre la dirección que te haya dado Cloudflare. La de la entrega es `https://ojo-ciudadano.iismael.workers.dev/`.

### 4. Blindar el ordenador para mañana

- **Energía:** Configuración → Sistema → Inicio/apagado y suspensión → Suspender: **Nunca**.
- **Windows Update:** Configuración → Windows Update → **Pausar 7 días**.
- **Docker Desktop:** Settings → General → **Start Docker Desktop when you sign in**.
- **Inicio de sesión sin contraseña tras un reinicio** (`netplwiz`, opcional): sin él, tras un
  corte de luz Docker no arranca hasta que inicies sesión por AnyDesk.
- **BIOS** (opcional): «Restore on AC power loss: Power On», para que se encienda solo si vuelve
  la luz.
- **AnyDesk:** acceso desatendido con contraseña.
- **OpenRouter:** pon un **límite de gasto a la clave** (panel de OpenRouter → Keys → la clave →
  credit limit). Con la web pública, cualquiera puede preguntar al modelo.
- **Aviso si se cae** (opcional): un vigilante gratuito (p. ej. UptimeRobot) sobre
  `https://oc-origen.sourcia.solutions/_stcore/health` que avise al móvil.

## Operación

| Quiero… | Cómo |
| --- | --- |
| Ver si todo va bien | `powershell -ExecutionPolicy Bypass -File despliegue\estado.ps1` |
| Publicar un cambio | Push a `main`. En 1–2 min está en la web (mira `despliegue\registros\actualizar.log`) |
| Forzar la actualización | `powershell -ExecutionPolicy Bypass -File despliegue\actualizar.ps1 -Forzar` |
| Cargar una base regenerada | `powershell -ExecutionPolicy Bypass -File despliegue\cargar_datos.ps1 -Origen <carpeta data>` |
| Reiniciar la web | `docker compose -f despliegue\docker-compose.yml restart web` |
| Ver errores de la web | `docker compose -f despliegue\docker-compose.yml logs --tail 100 web` |
| Cambiar de servidor | Editar `portada/config.js` (orden de la lista) y push: la portada nueva sale en < 1 min |
| Parar las actualizaciones | `powershell -ExecutionPolicy Bypass -File despliegue\registrar_tarea.ps1 -Quitar` |
| Volver a una versión anterior | Revertir el commit en `main` (`git revert`) y push |
| Probar la web sin internet | `http://localhost:8601` en el ordenador fijo |

## Qué pasa si…

- **Se reinicia el contenedor** (actualización o fallo): unos segundos. Streamlit se reconecta
  solo; la portada no hace nada salvo que falle dos veces seguidas (40 s).
- **Se cae el túnel o el ordenador:** la portada muestra «La web no responde» y reintenta cada
  8 s; vuelve sola cuando el servidor responde. Si hay una reserva en `config.js`, salta a ella.
- **Una actualización rompe la web:** `actualizar.ps1` vuelve a la imagen anterior y lo anota en
  el registro. Hay que arreglar `main`; mientras, sigue la versión anterior.
- **Se acaba el saldo de OpenRouter:** el asistente sigue con las respuestas preparadas; las
  demás dicen que el modelo no responde.

## Decisiones de configuración

- `STREAMLIT_SERVER_ENABLE_CORS=false` y `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false`: dentro
  del marco de otro dominio, Safari y algunos móviles bloquean la cookie de Streamlit y la página
  se queda en «Connecting». La app no recibe ficheros ni formularios que cambien nada.
- Sin vigilancia de ficheros ni recarga al guardar (`fileWatcherType=none`): en producción solo
  gastan CPU.
- `client.showErrorDetails=none`: ante un error, el visitante ve un aviso, no el código.
- La portada no tiene `404.html`: Cloudflare Pages sirve entonces `index.html` en cualquier ruta
  y los enlaces a una pantalla concreta funcionan.

## Reserva (opcional, no montada)

La portada ya admite una segunda dirección en `config.js`. Candidata: una copia en Streamlit
Community Cloud (`ojo-ciudadano.streamlit.app`, gratis, se actualiza desde GitHub). Pegas: la
base (1,15 GB) no cabe en GitHub y tendría que descargarse al arrancar desde otro sitio, la
memoria es justa (de 690 MB a 2,7 GB) y se duerme tras 12 h sin visitas. Hugging Face Spaces
gratis ya no es fiable para cuentas nuevas (desde julio de 2026 piden PRO para Docker).
