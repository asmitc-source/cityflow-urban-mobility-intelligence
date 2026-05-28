from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from cityflow.data.generate import build_city_dimension, build_corridor_dimension, generate_mobility_observations, write_partitioned_parquet
from cityflow.utils.config import load_config, project_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate scalable CityFlow mobility data.")
    parser.add_argument("--rows", type=int, default=None)
    args = parser.parse_args()

    config = load_config()
    rows = args.rows or int(config["pipeline"]["default_rows"])
    cities = build_city_dimension()
    corridors = build_corridor_dimension(seed=int(config["project"]["random_seed"]))
    observations = generate_mobility_observations(
        rows=rows,
        corridors=corridors,
        start_date=config["pipeline"]["start_date"],
        days=int(config["pipeline"]["days"]),
        seed=int(config["project"]["random_seed"]),
    )

    write_partitioned_parquet(cities, project_path("data", "processed", "dim_city.parquet"))
    write_partitioned_parquet(corridors, project_path("data", "processed", "dim_corridor.parquet"))
    write_partitioned_parquet(observations, project_path("data", "processed", "fact_mobility_observations.parquet"))
    print(f"Generated {rows:,} mobility observations across {cities.shape[0]} cities and {corridors.shape[0]} corridors.")


if __name__ == "__main__":
    main()

