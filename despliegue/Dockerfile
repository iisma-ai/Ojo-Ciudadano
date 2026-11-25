# Imagen de la web de Ojo Ciudadano para el despliegue (D-056, docs/15-despliegue.md).
#
# Solo lleva el código y las dependencias: la base de datos y las cachés van en el volumen
# `ojo-ciudadano-datos` (montado en /app/data) y la clave del modelo de lenguaje, en el .env de la
# carpeta de despliegue. Así una actualización de código reconstruye en segundos y los datos no
# viajan nunca dentro de la imagen.

FROM python:3.12-slim

# uv, la misma versión con la que se trabaja en el proyecto
COPY --from=ghcr.io/astral-sh/uv:0.10.6 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 1) Dependencias en su propia capa: solo se reinstalan si cambian pyproject.toml o uv.lock.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) El código. El proyecto se instala en modo editable: las rutas a data/ se calculan desde
#    src/, así que tiene que quedar en /app/src (no en site-packages).
COPY . .
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

# Streamlit trae su comprobación de salud. La usa Docker para reiniciar y la portada para saber
# si la web responde.
HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=4)"

CMD ["streamlit", "run", "src/ojo_ciudadano/app/main.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
