from __future__ import annotations

from pathlib import Path

import pandas as pd

from cityflow.data.adapters.base import SourceAdapter, SourceMetadata


class OpenMeteoWeatherAdapter(SourceAdapter):
    metadata = SourceMetadata(
        source_name="Open-Meteo Historical Weather",
        source_url="https://open-meteo.com/",
        refresh_frequency="hourly",
        owner="Open-Meteo",
    )

    def extract(self, source_path: Path | str) -> pd.DataFrame:
        path = Path(source_path)
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        rename_map = {
            "time": "ts",
            "rain": "rainfall_mm",
            "temperature_2m": "temperature_c",
            "relative_humidity_2m": "humidity_pct",
            "visibility": "visibility_km",
        }
        normalized = raw.rename(columns=rename_map).copy()
        required = {"ts", "city_id", "rainfall_mm", "temperature_c", "humidity_pct", "visibility_km"}
        self.validate_required_columns(normalized, required)
        normalized["ts"] = pd.to_datetime(normalized["ts"])
        return normalized[list(required)]

