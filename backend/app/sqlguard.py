import re

MAX_ROWS = 1000

# Palabras que jamás deben aparecer (incluye CTEs que modifican datos: WITH ... DELETE ...).
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|grant|revoke|create|comment|"
    r"copy|merge|call|vacuum|reindex|refresh|lock|security|attach)\b",
    re.IGNORECASE,
)


class SQLError(Exception):
    pass


def guard(sql: str) -> str:
    """Valida que sea una única consulta SELECT/WITH de solo lectura y le impone un LIMIT duro."""
    s = (sql or "").strip().rstrip(";").strip()
    if not s:
        raise SQLError("La consulta está vacía.")
    if ";" in s:
        raise SQLError("Solo se permite una sentencia SQL.")

    head = s.lstrip("(").lstrip().lower()
    if not (head.startswith("select") or head.startswith("with")):
        raise SQLError("Solo se permiten consultas de lectura (SELECT).")

    if _FORBIDDEN.search(s):
        raise SQLError("La consulta contiene operaciones no permitidas (solo lectura).")

    # Envuelve para forzar un tope de filas sin importar lo que traiga la consulta.
    return f"select * from (\n{s}\n) as _wrap limit {MAX_ROWS}"
