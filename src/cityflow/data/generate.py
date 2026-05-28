from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROAD_CLASSES = ["arterial", "sub_arterial", "collector", "expressway"]
ZONES = ["CBD", "IT corridor", "Industrial", "Airport link", "Residential", "Transit hub"]


@dataclass(frozen=True)
class CityProfile:
    city_id: int
    city_name: str
    state_name: str
    lat: float
    lon: float
    population_million: float
    vehicles_million: float
    congestion_bias: float


CITY_PROFILES = [
    CityProfile(1, "Bengaluru", "Karnataka", 12.9716, 77.5946, 13.6, 11.1, 1.18),
    CityProfile(2, "Mumbai", "Maharashtra", 19.0760, 72.8777, 21.7, 4.4, 1.14),
    CityProfile(3, "Delhi", "Delhi", 28.6139, 77.2090, 32.9, 12.2, 1.20),
    CityProfile(4, "Hyderabad", "Telangana", 17.3850, 78.4867, 10.8, 7.5, 1.05),
    CityProfile(5, "Chennai", "Tamil Nadu", 13.0827, 80.2707, 11.5, 6.3, 1.02),
    CityProfile(6, "Pune", "Maharashtra", 18.5204, 73.8567, 7.4, 4.8, 1.08),
]


def build_city_dimension() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "city_id": c.city_id,
                "city_name": c.city_name,
                "state_name": c.state_name,
                "centroid_lat": c.lat,
                "centroid_lon": c.lon,
                "population_million": c.population_million,
                "registered_vehicles_million": c.vehicles_million,
            }
            for c in CITY_PROFILES
        ]
    )


def build_corridor_dimension(corridors_per_city: int = 36, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    corridor_id = 1
    for city in CITY_PROFILES:
        for idx in range(corridors_per_city):
            zone = ZONES[idx % len(ZONES)]
            road_class = rng.choice(ROAD_CLASSES, p=[0.36, 0.30, 0.24, 0.10])
            lane_count = int(rng.choice([2, 3, 4, 6, 8], p=[0.18, 0.24, 0.34, 0.18, 0.06]))
            length = float(rng.uniform(1.2, 18.0))
            capacity = int(lane_count * rng.integers(650, 950))
            lat_shift = rng.normal(0, 0.075)
            lon_shift = rng.normal(0, 0.075)
            rows.append(
                {
                    "corridor_id": corridor_id,
                    "city_id": city.city_id,
                    "corridor_name": f"{city.city_name} {zone} Corridor {idx + 1:02d}",
                    "zone_name": zone,
                    "road_class": road_class,
                    "lane_count": lane_count,
                    "corridor_length_km": round(length, 2),
                    "design_capacity_vph": capacity,
                    "start_lat": city.lat + lat_shift,
                    "start_lon": city.lon + lon_shift,
                    "end_lat": city.lat + lat_shift + rng.normal(0, 0.035),
                    "end_lon": city.lon + lon_shift + rng.normal(0, 0.035),
                }
            )
            corridor_id += 1
    return pd.DataFrame(rows)


def generate_mobility_observations(
    rows: int,
    corridors: pd.DataFrame,
    start_date: str,
    days: int,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    corridor_sample = corridors.sample(rows, replace=True, random_state=seed).reset_index(drop=True)
    city_bias = {c.city_id: c.congestion_bias for c in CITY_PROFILES}

    minute_offsets = rng.integers(0, days * 24 * 60, size=rows)
    ts = pd.to_datetime(start_date) + pd.to_timedelta(minute_offsets, unit="m")
    hour = ts.hour.to_numpy()
    dow = ts.dayofweek.to_numpy()
    weekend = np.isin(dow, [5, 6])
    peak = np.isin(hour, [8, 9, 10, 17, 18, 19, 20])
    night = np.isin(hour, [0, 1, 2, 3, 4, 5])

    road_class = corridor_sample["road_class"].to_numpy()
    lane_count = corridor_sample["lane_count"].to_numpy()
    capacity = corridor_sample["design_capacity_vph"].to_numpy()
    length = corridor_sample["corridor_length_km"].to_numpy()
    city_ids = corridor_sample["city_id"].to_numpy()
    bias = np.vectorize(city_bias.get)(city_ids)

    monsoon_month = pd.Series(ts.month).isin([6, 7, 8, 9]).to_numpy()
    rainfall = rng.gamma(1.3, 2.2, rows) * monsoon_month * rng.binomial(1, 0.38, rows)
    temperature = rng.normal(29, 4.5, rows) + np.where(np.isin(city_ids, [3, 4]), 1.5, 0)
    humidity = np.clip(rng.normal(62, 14, rows) + rainfall * 2.4, 25, 98)
    visibility = np.clip(12 - rainfall * 0.42 - rng.normal(0, 1.2, rows), 1.5, 15)

    roadwork = rng.binomial(1, 0.045 + 0.02 * (road_class == "arterial"), rows).astype(bool)
    events = rng.binomial(1, 0.025 + 0.025 * peak, rows).astype(bool)
    incidents = rng.poisson(0.06 + 0.18 * peak + 0.04 * (rainfall > 8) + 0.08 * roadwork, rows)
    signal_density = np.clip(rng.normal(3.2, 1.4, rows) + (road_class == "collector") * 1.3, 0.4, 8.5)

    temporal_load = 0.55 + 0.50 * peak - 0.26 * night - 0.10 * weekend
    weather_pressure = np.clip(rainfall / 22 + (humidity - 65) / 130 + (10 - visibility) / 22, 0, 0.65)
    disruption = weather_pressure + incidents * 0.08 + roadwork * 0.14 + events * 0.11
    infrastructure_load = np.clip((temporal_load * bias) + disruption + rng.normal(0, 0.11, rows), 0.15, 1.65)

    vehicle_count = np.maximum(25, (capacity * infrastructure_load * rng.normal(1.0, 0.12, rows))).astype(int)
    free_flow_speed = np.select(
        [road_class == "expressway", road_class == "arterial", road_class == "sub_arterial"],
        [62, 44, 36],
        default=28,
    ).astype(float)
    avg_speed = np.clip(free_flow_speed * (1.22 - infrastructure_load * 0.58 - weather_pressure * 0.16), 6, free_flow_speed)
    free_flow_time = length / free_flow_speed * 60
    travel_time = length / avg_speed * 60 + incidents * rng.uniform(1.5, 6.0, rows) + roadwork * rng.uniform(2, 9, rows)
    delay = np.maximum(0, travel_time - free_flow_time)
    transit_delay = np.maximum(0, delay * rng.uniform(0.30, 0.85, rows) + events * rng.uniform(1, 7, rows))

    traffic_density = vehicle_count / np.maximum(lane_count * length, 1)
    route_inefficiency = np.clip((travel_time / np.maximum(free_flow_time, 0.1) - 1) * 100, 0, 240)
    congestion_index = np.clip(
        100
        * (0.42 * infrastructure_load + 0.25 * route_inefficiency / 100 + 0.18 * delay / 30 + 0.15 * disruption),
        0,
        100,
    )
    weather_score = np.clip(100 * weather_pressure, 0, 100)
    unobserved_operating_noise = rng.normal(0, 16, rows) + rng.choice([-8, 0, 7], size=rows, p=[0.16, 0.68, 0.16])
    noisy_congestion_score = np.clip(congestion_index + unobserved_operating_noise, 0, 100)
    hotspot_probability = 1 / (1 + np.exp(-(noisy_congestion_score - 63) / 8))
    hotspot = rng.binomial(1, hotspot_probability, rows)
    severity_score = np.clip(congestion_index + rng.normal(0, 4, rows), 0, 100)
    severity = np.select([severity_score < 38, severity_score < 62, severity_score < 78], [0, 1, 2], default=3)

    return pd.DataFrame(
        {
            "observation_id": np.arange(rows, dtype=np.int64),
            "ts": ts,
            "city_id": city_ids,
            "corridor_id": corridor_sample["corridor_id"].to_numpy(),
            "lat": corridor_sample["start_lat"].to_numpy() + rng.normal(0, 0.008, rows),
            "lon": corridor_sample["start_lon"].to_numpy() + rng.normal(0, 0.008, rows),
            "vehicle_count": vehicle_count,
            "avg_speed_kmph": np.round(avg_speed, 2),
            "free_flow_speed_kmph": free_flow_speed,
            "travel_time_min": np.round(travel_time, 2),
            "free_flow_time_min": np.round(free_flow_time, 2),
            "delay_min": np.round(delay, 2),
            "transit_delay_min": np.round(transit_delay, 2),
            "rainfall_mm": np.round(rainfall, 2),
            "temperature_c": np.round(temperature, 2),
            "humidity_pct": np.round(humidity, 2),
            "visibility_km": np.round(visibility, 2),
            "incident_count": incidents,
            "signal_density_per_km": np.round(signal_density, 2),
            "roadwork_flag": roadwork,
            "event_flag": events,
            "traffic_density": np.round(traffic_density, 2),
            "infrastructure_load": np.round(infrastructure_load, 3),
            "congestion_severity_index": np.round(congestion_index, 2),
            "route_inefficiency_score": np.round(route_inefficiency, 2),
            "peak_hour_flag": peak,
            "weather_disruption_score": np.round(weather_score, 2),
            "hotspot_label": hotspot,
            "severity_label": severity,
        }
    )


def write_partitioned_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
