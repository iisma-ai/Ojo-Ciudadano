"""Base DuckDB en memoria con el esquema real y ayudas para insertar filas sintéticas."""

from datetime import date
from pathlib import Path

import duckdb
import pytest

from ojo_ciudadano.indicadores import ejecutor

RAIZ = Path(__file__).resolve().parents[1]
HOY = date(2026, 11, 17)


class Base:
    def __init__(self):
        self.con = duckdb.connect()
        for ddl in sorted((RAIZ / "sql" / "esquema").glob("*.sql")):
            self.con.execute(ddl.read_text("utf-8"))
        ejecutor.crear_funciones(self.con)
        self.con.execute("INSERT INTO organo (organo_id, nombre) VALUES ('ORG', 'Órgano')")
        self.con.execute("INSERT INTO organo (organo_id, nombre) VALUES ('OTRO', 'Otro órgano')")

    def contrato(self, contrato_id, adjudicaciones=(), **campos):
        fila = {
            "contrato_id": contrato_id,
            "fuente": "placsp",
            "organo_id": "ORG",
            "es_menor": False,
            "url_origen": f"https://ejemplo.test/{contrato_id}",
            "fecha_descarga": HOY,
            **campos,
        }
        self._insertar("contrato", fila)
        for orden, adjudicacion in enumerate(adjudicaciones, start=1):
            adjudicatario = adjudicacion.get("adjudicatario_id")
            if adjudicatario:
                self.con.execute(
                    "INSERT OR IGNORE INTO adjudicatario VALUES (?, ?, 'Empresa', 'juridica')",
                    [adjudicatario, adjudicatario],
                )
            self._insertar(
                "adjudicacion",
                {
                    "contrato_id": contrato_id,
                    "orden": orden,
                    "fuente": fila["fuente"],
                    "url_origen": fila["url_origen"],
                    "fecha_descarga": HOY,
                    **adjudicacion,
                },
            )

    def menor(self, contrato_id, fecha, importe, adjudicatario="B1", **campos):
        self.contrato(
            contrato_id,
            [{"adjudicatario_id": adjudicatario, "importe_con_iva": importe}],
            fuente="portal_cm",
            es_menor=True,
            procedimiento="Contrato menor",
            tipo_contrato=campos.pop("tipo_contrato", "servicios"),
            fecha_contrato=fecha,
            **campos,
        )

    def _insertar(self, tabla, fila):
        columnas = ", ".join(fila)
        marcas = ", ".join("?" for _ in fila)
        self.con.execute(f"INSERT INTO {tabla} ({columnas}) VALUES ({marcas})", list(fila.values()))

    def resultado(self, nombre_sql):
        """Resultado del indicador como {contrato_id: fila}."""
        relacion = ejecutor.ejecutar(self.con, RAIZ / "sql" / "indicadores" / nombre_sql)
        filas = relacion.fetchall()
        return {f[0]: dict(zip(ejecutor.COLUMNAS, f, strict=True)) for f in filas}


@pytest.fixture
def base():
    return Base()
