CREATE TABLE IF NOT EXISTS dim_city (
    city_id INTEGER PRIMARY KEY,
    city_name VARCHAR NOT NULL,
    state_name VARCHAR NOT NULL,
    centroid_lat DOUBLE NOT NULL,
    centroid_lon DOUBLE NOT NULL,
    population_million DOUBLE,
    registered_vehicles_million DOUBLE
);

CREATE TABLE IF NOT EXISTS dim_corridor (
    corridor_id INTEGER PRIMARY KEY,
    city_id INTEGER NOT NULL,
    corridor_name VARCHAR NOT NULL,
    zone_name VARCHAR NOT NULL,
    road_class VARCHAR NOT NULL,
    lane_count INTEGER NOT NULL,
    corridor_length_km DOUBLE NOT NULL,
    design_capacity_vph INTEGER NOT NULL,
    start_lat DOUBLE NOT NULL,
    start_lon DOUBLE NOT NULL,
    end_lat DOUBLE NOT NULL,
    end_lon DOUBLE NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_mobility_observations (
    observation_id BIGINT,
    ts TIMESTAMP NOT NULL,
    city_id INTEGER NOT NULL,
    corridor_id INTEGER NOT NULL,
    lat DOUBLE NOT NULL,
    lon DOUBLE NOT NULL,
    vehicle_count INTEGER NOT NULL,
    avg_speed_kmph DOUBLE NOT NULL,
    free_flow_speed_kmph DOUBLE NOT NULL,
    travel_time_min DOUBLE NOT NULL,
    free_flow_time_min DOUBLE NOT NULL,
    delay_min DOUBLE NOT NULL,
    transit_delay_min DOUBLE NOT NULL,
    rainfall_mm DOUBLE NOT NULL,
    temperature_c DOUBLE NOT NULL,
    humidity_pct DOUBLE NOT NULL,
    visibility_km DOUBLE NOT NULL,
    incident_count INTEGER NOT NULL,
    signal_density_per_km DOUBLE NOT NULL,
    roadwork_flag BOOLEAN NOT NULL,
    event_flag BOOLEAN NOT NULL,
    traffic_density DOUBLE NOT NULL,
    infrastructure_load DOUBLE NOT NULL,
    congestion_severity_index DOUBLE NOT NULL,
    route_inefficiency_score DOUBLE NOT NULL,
    peak_hour_flag BOOLEAN NOT NULL,
    weather_disruption_score DOUBLE NOT NULL,
    hotspot_label INTEGER NOT NULL,
    severity_label INTEGER NOT NULL
);

