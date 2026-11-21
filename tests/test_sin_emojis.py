"""D-022: no se usan emojis ni emoticonos en el repositorio (docs/marca.md)."""

import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EXTENSIONES = {".py", ".md", ".sql", ".toml", ".css", ".svg", ".txt", ".json", ".yml", ".yaml"}
# Pictogramas, símbolos varios y dingbats, más el selector de variante y el unidor de emojis.
EMOJI = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\u2b00-\u2bff\ufe0f\u200d]")


def test_no_hay_emojis_en_el_repositorio():
    ficheros = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    encontrados = []
    for nombre in ficheros:
        ruta = RAIZ / nombre
        if ruta.suffix not in EXTENSIONES or not ruta.is_file():
            continue
        for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1):
            if EMOJI.search(linea):
                encontrados.append(f"{nombre}:{n}")
    assert not encontrados, "Emojis prohibidos (D-022): " + ", ".join(encontrados)
