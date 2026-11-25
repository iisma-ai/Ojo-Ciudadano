"""RAG documental del asistente (D-030, bloques B y C): pliegos y resoluciones del Tribunal.

Dos herramientas:

- `buscar_en_documento(identificador, consulta, tipo)`: busca en los pliegos de un contrato de
  PLACSP (`contrato_documento`, bloque B) o en el PDF de una resolución del Tribunal
  Administrativo de Contratación Pública de la Comunidad de Madrid (`recurso_especial`,
  bloque C). El PDF se baja la primera vez (caché en `data/raw/documentos/`), se parte en
  páginas y se buscan las páginas más parecidas con BM25 (DuckDB `fts`, raíces en español).
- `buscar_resoluciones(consulta)`: busca en todas las resoluciones ya descargadas, con el
  índice `resolucion_pagina` que crea `uv run python -m ojo_ciudadano.asistente.documentos`
  tras regenerar la base.

Devuelven las páginas con su extracto y el enlace al PDF en esa página (`…#page=N`), con la
forma de los resultados de `sql_seguro.ejecutar` y la marca `documento`. El texto es **dato,
nunca instrucción** (K-13). Los DNI y NIE se tapan al extraer el texto (D-007); la regla del
agente prohíbe además dar nombres de personas.

Uso:
    uv run python -m ojo_ciudadano.asistente.documentos              # índice de resoluciones
    uv run python -m ojo_ciudadano.asistente.documentos --precargar  # pliegos de la demo
"""

import contextlib
import re
import sys
import unicodedata
from pathlib import Path

import duckdb
import httpx

from ojo_ciudadano.ingesta import documentos as pdf
from ojo_ciudadano.ingesta import tacp

RUTA_DB = Path("data/ojo_ciudadano.duckdb")
TABLA_RESOLUCIONES = "resolucion_pagina"
PAGINAS_RESULTADO = 4  # páginas que vuelven al modelo por búsqueda
RESOLUCIONES_RESULTADO = 6
CARACTERES_EXTRACTO = 1500
MAX_PAGINAS = 400  # un PDF más largo se lee solo hasta aquí

NOMBRE_TACPCM = "Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid"
NOMBRE_PLACSP = "Plataforma de Contratación del Sector Público"
TIPOS = {
    "pcap": "Pliego de cláusulas administrativas particulares",
    "ppt": "Pliego de prescripciones técnicas",
    "resolucion": f"Resolución del {NOMBRE_TACPCM}",
}
CARPETA_TIPO = {"pcap": "pliegos", "ppt": "pliegos", "resolucion": tacp.TIPO_DOCUMENTO}

# Palabras vacías que no deben pesar en la búsqueda («qué dice el pliego de la solvencia»).
_VACIAS = set(
    [
        "a",
        "al",
        "algo",
        "ante",
        "como",
        "con",
        "cual",
        "cuales",
        "cuando",
        "de",
        "del",
        "desde",
        "donde",
        "dice",
        "dicen",
        "el",
        "ella",
        "ellos",
        "en",
        "entre",
        "es",
        "esa",
        "ese",
        "esta",
        "este",
        "esto",
        "fue",
        "ha",
        "han",
        "hay",
        "la",
        "las",
        "le",
        "les",
        "lo",
        "los",
        "mas",
        "me",
        "mi",
        "muy",
        "no",
        "nos",
        "o",
        "para",
        "pero",
        "por",
        "porque",
        "que",
        "quien",
        "se",
        "segun",
        "ser",
        "si",
        "sin",
        "sobre",
        "su",
        "sus",
        "tiene",
        "un",
        "una",
        "uno",
        "unos",
        "unas",
        "y",
        "ya",
        "pliego",
        "pliegos",
        "documento",
        "resolucion",
        "contrato",
    ]
)


class DocumentoNoDisponible(ValueError):
    """No hay documento para ese identificador, o no se puede bajar o leer."""


def _plano(texto: str) -> str:
    """Minúsculas sin tildes, con la misma longitud que el texto (para situar el extracto)."""
    return "".join(unicodedata.normalize("NFD", c)[0] for c in texto.lower())


def palabras_clave(consulta: str) -> list[str]:
    palabras = re.findall(r"[a-z0-9ñ]+", _plano(consulta))
    return [p for p in palabras if p not in _VACIAS and len(p) > 1]


EXTRACTO_OCULTO = (
    "Esta página puede contener datos de una persona física y no se muestra. Puedes leerla en "
    "el PDF oficial."
)


def _comprobar_consulta(consulta: str) -> list[str]:
    """Palabras de la búsqueda. Las búsquedas son por temas: con un DNI, un NIE o un nombre
    con tratamiento («D. …») se rechazan (D-007)."""
    from ojo_ciudadano.asistente.bateria import PATRON_DNI

    if PATRON_DNI.search(consulta) or pdf.TRATAMIENTO.search(consulta):
        raise DocumentoNoDisponible("La búsqueda en documentos es por temas, no por personas.")
    palabras = palabras_clave(consulta)
    if not palabras:
        raise DocumentoNoDisponible("La búsqueda está vacía: usa palabras del tema.")
    return palabras


def extracto(texto: str, palabras: list[str], largo: int = CARACTERES_EXTRACTO) -> str:
    """Trozo de la página alrededor de la zona con más palabras de la búsqueda. Si la página
    puede tratar de una persona física («en nombre propio»), no se da el texto."""
    if pdf.puede_tener_persona_fisica(texto):
        return EXTRACTO_OCULTO
    if len(texto) <= largo:
        return texto
    plano = _plano(texto)
    raices = [p[:5] for p in palabras]
    posiciones = sorted(m.start() for r in raices for m in re.finditer(re.escape(r), plano))
    if not posiciones:
        return texto[:largo].rstrip() + " …"
    # La ventana que contiene más apariciones.
    mejor, inicio_mejor = 0, posiciones[0]
    for i, inicio in enumerate(posiciones):
        dentro = sum(1 for p in posiciones[i:] if p < inicio + largo)
        if dentro > mejor:
            mejor, inicio_mejor = dentro, inicio
    inicio = max(0, inicio_mejor - largo // 5)
    trozo = texto[inicio : inicio + largo].strip()
    return ("… " if inicio > 0 else "") + trozo + (" …" if inicio + largo < len(texto) else "")


def _con_fts(con: duckdb.DuckDBPyConnection) -> bool:
    try:
        con.execute("LOAD fts")
        return True
    except duckdb.Error:
        try:
            con.execute("INSTALL fts; LOAD fts")
            return True
        except duckdb.Error:
            return False


def mejores_paginas(textos: list[str], consulta: str, n: int = PAGINAS_RESULTADO) -> list[int]:
    """Índices (desde 0) de las páginas más parecidas a la consulta, de más a menos. BM25 con
    raíces en español; si la extensión `fts` no está, cuenta palabras en común."""
    palabras = palabras_clave(consulta)
    if not palabras or not textos:
        return []
    con = duckdb.connect()
    try:
        con.execute("CREATE TABLE pagina (i INTEGER, texto VARCHAR)")
        con.executemany("INSERT INTO pagina VALUES (?, ?)", list(enumerate(textos)))
        if _con_fts(con):
            con.execute(
                "PRAGMA create_fts_index('pagina', 'i', 'texto', stemmer='spanish', "
                "stopwords='none', strip_accents=1, lower=1, overwrite=1)"
            )
            filas = con.execute(
                "SELECT i FROM (SELECT i, fts_main_pagina.match_bm25(i, $q) AS r FROM pagina) "
                "WHERE r IS NOT NULL ORDER BY r DESC, i LIMIT $n",
                {"q": " ".join(palabras), "n": n},
            ).fetchall()
            return [f[0] for f in filas]
    finally:
        con.close()
    raices = [p[:5] for p in palabras]
    puntos = [(sum(_plano(t).count(r) for r in raices), -i) for i, t in enumerate(textos)]
    return [-i for p, i in sorted(puntos, reverse=True)[:n] if p > 0]


# ---------------------------------------------------------------- documentos de la base


def _hay_tabla(con, tabla: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {tabla} LIMIT 0")
        return True
    except duckdb.Error:
        return False


def documentos_de(con: duckdb.DuckDBPyConnection, identificador: str) -> list[dict]:
    """Documentos de un contrato (pliegos) o de una resolución del Tribunal (su PDF)."""
    identificador = identificador.strip()
    if identificador.startswith(f"{tacp.FUENTE}:"):
        if not _hay_tabla(con, "recurso_especial"):
            raise DocumentoNoDisponible("La base no tiene las resoluciones del Tribunal.")
        filas = con.execute(
            "SELECT resolucion_id, url_documento, url_origen, fecha, tipo_resolucion, "
            "acto_recurrido, contrato_id FROM recurso_especial WHERE resolucion_id = ?",
            [identificador],
        ).fetchall()
        return [
            {
                "identificador": f[0],
                "tipo": "resolucion",
                "titulo": f"Resolución {f[0].split(':', 1)[1]} ({f[4]}; acto recurrido: {f[5]})",
                "url_documento": f[1],
                "url_origen": f[2],
                "fuente": NOMBRE_TACPCM,
                "contrato_id": f[6],
            }
            for f in filas
            if f[1]
        ]
    if not _hay_tabla(con, "contrato_documento"):
        raise DocumentoNoDisponible(
            "Los enlaces de los pliegos no están disponibles todavía en esta versión de la web."
        )
    # Una licitación del portal regional que repite una de PLACSP usa los pliegos de esa.
    duplicado = con.execute(
        "SELECT duplicado_de FROM contrato WHERE contrato_id = ?", [identificador]
    ).fetchall()
    if duplicado and duplicado[0][0]:
        identificador = duplicado[0][0]
    filas = con.execute(
        "SELECT d.tipo, d.nombre, d.url_documento, d.url_origen, c.titulo "
        "FROM contrato_documento d LEFT JOIN contrato c USING (contrato_id) "
        "WHERE d.contrato_id = ? ORDER BY d.orden",
        [identificador],
    ).fetchall()
    return [
        {
            "identificador": identificador,
            "tipo": f[0],
            "titulo": f"{TIPOS.get(f[0], f[0])} · {f[4] or identificador}",
            "url_documento": f[2],
            "url_origen": f[3],
            "fuente": NOMBRE_PLACSP,
            "contrato_id": identificador,
        }
        for f in filas
    ]


def _paginas_de(documento: dict, carpeta: Path) -> tuple[list[str], str]:
    ruta = pdf.descargar(documento["url_documento"], CARPETA_TIPO[documento["tipo"]], carpeta)
    return pdf.paginas(ruta)[:MAX_PAGINAS], pdf.fecha_descarga(ruta).isoformat()


COLUMNAS = ["documento", "pagina", "extracto", "enlace_pagina", "fuente", "fecha_descarga"]


def buscar_en_documento(
    con: duckdb.DuckDBPyConnection,
    identificador: str,
    consulta: str,
    tipo: str | None = None,
    carpeta: Path = pdf.CARPETA,
) -> dict:
    """Las páginas más parecidas a la consulta en los documentos de ese contrato o
    resolución. `tipo` (pcap o ppt) limita a un pliego; sin él, se busca en todos."""
    palabras = _comprobar_consulta(consulta)
    documentos = documentos_de(con, identificador)
    if tipo in ("pcap", "ppt"):
        documentos = [d for d in documentos if d["tipo"] == tipo]
    if not documentos:
        raise DocumentoNoDisponible(
            f"No hay documentos enlazados para {identificador}"
            + (f" del tipo {tipo}" if tipo else "")
            + ". Los pliegos solo están en las licitaciones de PLACSP (contrato_id 'placsp:…'); "
            "los menores, las emergencias y el portal regional no los enlazan."
        )
    filas, fallos, leidos = [], [], []
    for documento in documentos:
        try:
            textos, descarga = _paginas_de(documento, carpeta)
        except (httpx.HTTPError, pdf.DocumentoNoDisponible) as error:
            fallos.append(f"{documento['titulo']}: {error}")
            continue
        leidos.append({**documento, "paginas": len(textos), "fecha_descarga": descarga})
        for i in mejores_paginas(textos, consulta):
            filas.append(
                [
                    documento["titulo"],
                    i + 1,
                    extracto(textos[i], palabras),
                    f"{documento['url_documento']}#page={i + 1}",
                    documento["fuente"],
                    descarga,
                ]
            )
    if not leidos:
        raise DocumentoNoDisponible("No se ha podido leer ningún documento: " + "; ".join(fallos))
    return {
        "sql": f"-- Búsqueda en los documentos de {identificador}: «{consulta}»",
        "columnas": COLUMNAS,
        "filas": filas,
        "recortado": False,
        "documento": identificador,
        "consulta_documento": consulta,
        "documentos": [
            {k: d[k] for k in ("titulo", "tipo", "url_documento", "url_origen", "paginas")}
            for d in leidos
        ],
        "fuente": documentos[0]["fuente"],
        "url_origen": documentos[0]["url_origen"],
        "fecha_descarga": max(d["fecha_descarga"] for d in leidos),
        "fallos": fallos,
    }


# ---------------------------------------------------------- índice de todas las resoluciones


def construir_resoluciones(con: duckdb.DuckDBPyConnection, carpeta: Path = pdf.CARPETA) -> int:
    """Tabla `resolucion_pagina` (una fila por página de cada resolución ya descargada) y su
    índice BM25, en una conexión con escritura. No baja nada: usa la caché de `tacp --pdf`.
    Devuelve las páginas indexadas. No es una tabla del esquema ni se consulta con SQL: solo
    la usa `buscar_resoluciones`."""
    filas = []
    for resolucion_id, url in con.execute(
        "SELECT resolucion_id, url_documento FROM recurso_especial "
        "WHERE url_documento IS NOT NULL ORDER BY resolucion_id"
    ).fetchall():
        ruta = pdf.ruta_local(url, tacp.TIPO_DOCUMENTO, carpeta)
        if not ruta.exists():
            continue
        try:
            textos = pdf.paginas(ruta)[:MAX_PAGINAS]
        except pdf.DocumentoNoDisponible:
            continue
        descarga = pdf.fecha_descarga(ruta)
        filas += [
            (f"{resolucion_id}#{i + 1}", resolucion_id, i + 1, t, descarga)
            for i, t in enumerate(textos)
            if t.strip()
        ]
    con.execute("INSTALL fts; LOAD fts")
    con.execute(
        f"CREATE OR REPLACE TABLE {TABLA_RESOLUCIONES} (id VARCHAR PRIMARY KEY, "
        "resolucion_id VARCHAR, pagina INTEGER, texto VARCHAR, fecha_descarga DATE)"
    )
    if filas:
        con.executemany(f"INSERT INTO {TABLA_RESOLUCIONES} VALUES (?, ?, ?, ?, ?)", filas)
    con.execute(
        f"PRAGMA create_fts_index('{TABLA_RESOLUCIONES}', 'id', 'texto', stemmer='spanish', "
        "stopwords='none', strip_accents=1, lower=1, overwrite=1)"
    )
    return len(filas)


def resoluciones_disponibles(con: duckdb.DuckDBPyConnection) -> bool:
    try:
        con.execute(f"SELECT fts_main_{TABLA_RESOLUCIONES}.match_bm25('x', 'x')").fetchall()
        return True
    except duckdb.Error:
        return False


COLUMNAS_RESOLUCIONES = [
    "resolucion",
    "fecha",
    "tipo_resolucion",
    "acto_recurrido",
    "procedencia",
    "contrato_id",
    "pagina",
    "extracto",
    "enlace_pagina",
    "url_origen",
    "fuente",
    "fecha_descarga",
]


def buscar_resoluciones(
    con: duckdb.DuckDBPyConnection,
    consulta: str,
    tipo_resolucion: str | None = None,
    n: int = RESOLUCIONES_RESULTADO,
) -> dict:
    """Las resoluciones del Tribunal cuyo texto más se parece a la consulta, con su mejor
    página. `tipo_resolucion` filtra (p. ej. «Estimatoria»: incluye las parciales)."""
    palabras = _comprobar_consulta(consulta)
    if not resoluciones_disponibles(con):
        raise DocumentoNoDisponible(
            "El texto de las resoluciones del Tribunal no está disponible todavía en esta versión "
            "de la web."
        )
    filtro = ""
    parametros = {"q": " ".join(palabras), "n": n}
    if tipo_resolucion:
        filtro = "AND r.tipo_resolucion ILIKE $tipo"
        parametros["tipo"] = f"%{tipo_resolucion.strip()}%"
        if tipo_resolucion.strip().lower().startswith("estim"):
            # «Estimatoria» no debe traer «Desestimatoria»
            filtro = "AND list_has_any(string_split(r.tipo_resolucion, '; '), $tipos)"
            parametros.pop("tipo")
            parametros["tipos"] = ["Estimatoria", "Estimatoria parcial"]
    sql = f"""
    WITH c AS (
        SELECT p.*, fts_main_{TABLA_RESOLUCIONES}.match_bm25(p.id, $q) AS relevancia
        FROM {TABLA_RESOLUCIONES} AS p
    ), mejor AS (
        SELECT * FROM c WHERE relevancia IS NOT NULL
        QUALIFY row_number() OVER (PARTITION BY resolucion_id ORDER BY relevancia DESC) = 1
    )
    SELECT r.numero, r.fecha, r.tipo_resolucion, r.acto_recurrido, r.procedencia, r.contrato_id,
           m.pagina, m.texto, r.url_documento, r.url_origen, m.fecha_descarga
    FROM mejor AS m JOIN recurso_especial AS r USING (resolucion_id)
    WHERE true {filtro}
    ORDER BY m.relevancia DESC LIMIT $n
    """
    filas = []
    for f in con.execute(sql, parametros).fetchall():
        filas.append(
            [
                f[0],
                f[1],
                f[2],
                f[3],
                f[4],
                f[5],
                f[6],
                extracto(f[7], palabras),
                f"{f[8]}#page={f[6]}",
                f[9],
                NOMBRE_TACPCM,
                f[10],
            ]
        )
    total = con.execute(
        f"SELECT count(DISTINCT resolucion_id) FROM {TABLA_RESOLUCIONES}"
    ).fetchall()[0][0]
    return {
        "sql": f"-- Búsqueda en el texto de las resoluciones del Tribunal: «{consulta}»"
        + (f" (tipo: {tipo_resolucion})" if tipo_resolucion else ""),
        "columnas": COLUMNAS_RESOLUCIONES,
        "filas": filas,
        "recortado": False,
        "documento": "resoluciones",
        "consulta_documento": consulta,
        "resoluciones_indexadas": total,
        "fuente": NOMBRE_TACPCM,
        "fecha_descarga": max((f[-1] for f in filas), default=None),
    }


# ------------------------------------------------------------------------ precarga


def contratos_demo(con: duckdb.DuckDBPyConnection, n: int = 50) -> list[str]:
    """Licitaciones de PLACSP con pliego y alguna señal R-01, R-02, R-05 o R-06 (las que el
    pliego ayuda a explicar), más las de la batería. Para dejar sus pliegos en caché."""
    from ojo_ciudadano.asistente import bateria

    propios = [p for p in bateria.CONTRATOS_DOCUMENTO]
    filas = con.execute(
        """
        SELECT DISTINCT i.contrato_id
        FROM indicador_resultado i JOIN contrato_documento d USING (contrato_id)
        WHERE i.indicador IN ('R-01', 'R-02', 'R-05', 'R-06') AND i.activado
        ORDER BY i.contrato_id DESC LIMIT ?
        """,
        [n],
    ).fetchall()
    return list(dict.fromkeys([*propios, *(f[0] for f in filas)]))


def precargar(con: duckdb.DuckDBPyConnection, n: int = 50) -> tuple[int, int]:
    """Baja los pliegos de `contratos_demo`. Devuelve (bajados, fallidos)."""
    urls = []
    for contrato_id in contratos_demo(con, n):
        urls += [d["url_documento"] for d in documentos_de(con, contrato_id)]
    resultado = pdf.descargar_varios(urls, "pliegos")
    for ruta in resultado.values():
        if ruta is not None:
            with contextlib.suppress(pdf.DocumentoNoDisponible):
                pdf.paginas(ruta)
    bien = sum(r is not None for r in resultado.values())
    return bien, len(resultado) - bien


def main() -> None:
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    ruta = Path(argumentos[0]) if argumentos else RUTA_DB
    with duckdb.connect(str(ruta)) as con:
        if "--precargar" in sys.argv:
            bien, mal = precargar(con)
            print(f"Pliegos en caché: {bien} (fallidos: {mal}).")
        print(f"{TABLA_RESOLUCIONES}: {construir_resoluciones(con)} páginas indexadas en {ruta}.")


if __name__ == "__main__":
    main()
