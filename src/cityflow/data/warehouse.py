from __future__ import annotations

from pathlib import Path

import duckdb

from cityflow.utils.config import project_path


def connect_warehouse(path: Path | None = None) -> duckdb.DuckDBPyConnection:
    db_path = path or project_path("data", "warehouse", "cityflow.duckdb")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def run_sql_file(conn: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    conn.execute(sql_path.read_text(encoding="utf-8"))


def initialize_schema(conn: duckdb.DuckDBPyConnection) -> None:
    run_sql_file(conn, project_path("sql", "schema.sql"))


def load_dimensions(conn: duckdb.DuckDBPyConnection, cities_path: Path, corridors_path: Path) -> None:
    conn.execute("DELETE FROM dim_city")
    conn.execute("DELETE FROM dim_corridor")
    conn.execute(
        "INSERT INTO dim_city SELECT * FROM read_parquet(?)",
        [str(cities_path)],
    )
    conn.execute(
        "INSERT INTO dim_corridor SELECT * FROM read_parquet(?)",
        [str(corridors_path)],
    )


def load_fact(conn: duckdb.DuckDBPyConnection, fact_path: Path) -> None:
    conn.execute("DELETE FROM fact_mobility_observations")
    conn.execute(
        "INSERT INTO fact_mobility_observations SELECT * FROM read_parquet(?)",
        [str(fact_path)],
    )


def build_marts(conn: duckdb.DuckDBPyConnection) -> None:
    run_sql_file(conn, project_path("sql", "marts.sql"))

