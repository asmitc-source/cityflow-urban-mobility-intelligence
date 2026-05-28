from __future__ import annotations

from pathlib import Path

import pandas as pd

from cityflow.data.adapters.base import SourceAdapter, SourceMetadata


class MunicipalTrafficAdapter(SourceAdapter):
    metadata = SourceMetadata(
        source_name="Municipal Traffic Operations Export",
        source_url="city open data portal",
        refresh_frequency="daily",
        owner="municipal transport department",
    )

    def extract(self, source_path: Path | str) -> pd.DataFrame:
        path = Path(source_path)
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        normalized = raw.copy()
        required = {
            "ts",
            "city_id",
            "corridor_id",
            "vehicle_count",
            "avg_speed_kmph",
            "travel_time_min",
            "incident_count",
        }
        self.validate_required_columns(normalized, required)
        normalized["ts"] = pd.to_datetime(normalized["ts"])
        return normalized[list(required)]

