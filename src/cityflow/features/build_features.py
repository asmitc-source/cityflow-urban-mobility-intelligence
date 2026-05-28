from __future__ import annotations

import pandas as pd


CATEGORICAL_FEATURES = ["city_name", "zone_name", "road_class"]
NUMERIC_FEATURES = [
    "vehicle_count",
    "free_flow_speed_kmph",
    "rainfall_mm",
    "temperature_c",
    "humidity_pct",
    "visibility_km",
    "incident_count",
    "signal_density_per_km",
    "weather_disruption_score",
    "lane_count",
    "corridor_length_km",
    "design_capacity_vph",
    "hour_of_day",
    "day_of_week",
    "weekend_flag",
]


def prepare_model_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    bool_cols = ["roadwork_flag", "event_flag", "peak_hour_flag"]
    for col in bool_cols:
        frame[col] = frame[col].astype(int)
    frame["load_per_lane"] = frame["vehicle_count"] / frame["lane_count"].clip(lower=1)
    frame["capacity_pressure"] = frame["vehicle_count"] / frame["design_capacity_vph"].clip(lower=1)
    frame["rain_peak_interaction"] = frame["rainfall_mm"] * frame["peak_hour_flag"]
    frame["incident_peak_interaction"] = frame["incident_count"] * frame["peak_hour_flag"]
    return frame


def feature_columns() -> list[str]:
    return NUMERIC_FEATURES + [
        "roadwork_flag",
        "event_flag",
        "peak_hour_flag",
        "load_per_lane",
        "capacity_pressure",
        "rain_peak_interaction",
        "incident_peak_interaction",
    ] + CATEGORICAL_FEATURES
