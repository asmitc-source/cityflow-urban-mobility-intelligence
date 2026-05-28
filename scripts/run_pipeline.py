from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cityflow.data.generate import build_city_dimension, build_corridor_dimension, generate_mobility_observations, write_partitioned_parquet
from cityflow.data.warehouse import build_marts, connect_warehouse, initialize_schema, load_dimensions, load_fact
from cityflow.utils.config import load_config, project_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CityFlow ingestion and warehouse build.")
    parser.add_argument("--rows", type=int, default=None)
    args = parser.parse_args()

    config = load_config()
    rows = args.rows or int(config["pipeline"]["default_rows"])
    seed = int(config["project"]["random_seed"])

    cities = build_city_dimension()
    corridors = build_corridor_dimension(seed=seed)
    facts = generate_mobility_observations(
        rows=rows,
        corridors=corridors,
        start_date=config["pipeline"]["start_date"],
        days=int(config["pipeline"]["days"]),
        seed=seed,
    )

    city_path = project_path("data", "processed", "dim_city.parquet")
    corridor_path = project_path("data", "processed", "dim_corridor.parquet")
    fact_path = project_path("data", "processed", "fact_mobility_observations.parquet")
    write_partitioned_parquet(cities, city_path)
    write_partitioned_parquet(corridors, corridor_path)
    write_partitioned_parquet(facts, fact_path)

    conn = connect_warehouse()
    initialize_schema(conn)
    load_dimensions(conn, city_path, corridor_path)
    load_fact(conn, fact_path)
    build_marts(conn)
    count = conn.execute("SELECT COUNT(*) FROM fact_mobility_observations").fetchone()[0]
    print(f"CityFlow warehouse ready: {count:,} observations loaded into DuckDB.")


if __name__ == "__main__":
    main()

