CREATE OR REPLACE VIEW mart_city_hourly_kpis AS
SELECT
    c.city_name,
    date_trunc('hour', f.ts) AS hour_ts,
    EXTRACT(hour FROM f.ts) AS hour_of_day,
    AVG(f.traffic_density) AS traffic_density,
    AVG(f.delay_min) AS average_delay_min,
    AVG(f.congestion_severity_index) AS congestion_severity_index,
    STDDEV(f.travel_time_min) / NULLIF(AVG(f.travel_time_min), 0) AS commute_variability,
    AVG(f.route_inefficiency_score) AS route_inefficiency_score,
    AVG(f.infrastructure_load) AS infrastructure_load_utilization,
    AVG(CASE WHEN f.transit_delay_min > 5 THEN 1 ELSE 0 END) AS transit_delay_frequency,
    AVG(CASE WHEN f.peak_hour_flag THEN f.congestion_severity_index ELSE NULL END) AS peak_hour_stress_score,
    SUM(f.vehicle_count) AS mobility_throughput,
    AVG(f.weather_disruption_score) AS weather_disruption_score,
    SUM(f.incident_count) AS incident_pressure,
    AVG(f.hotspot_label) AS hotspot_rate,
    AVG(f.avg_speed_kmph / NULLIF(f.free_flow_speed_kmph, 0)) AS travel_speed_index
FROM fact_mobility_observations f
JOIN dim_city c ON f.city_id = c.city_id
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW mart_corridor_stress AS
SELECT
    c.city_name,
    d.corridor_name,
    d.zone_name,
    d.road_class,
    d.start_lat AS lat,
    d.start_lon AS lon,
    AVG(f.infrastructure_load) AS infrastructure_load,
    AVG(f.congestion_severity_index) AS congestion_severity_index,
    AVG(f.delay_min) AS average_delay_min,
    AVG(f.route_inefficiency_score) AS route_inefficiency_score,
    AVG(f.weather_disruption_score) AS weather_disruption_score,
    AVG(f.hotspot_label) AS hotspot_probability,
    COUNT(*) AS observation_count
FROM fact_mobility_observations f
JOIN dim_corridor d ON f.corridor_id = d.corridor_id
JOIN dim_city c ON f.city_id = c.city_id
GROUP BY 1, 2, 3, 4, 5, 6;

CREATE OR REPLACE VIEW mart_model_scoring_frame AS
SELECT
    f.*,
    c.city_name,
    d.corridor_name,
    d.zone_name,
    d.road_class,
    d.lane_count,
    d.corridor_length_km,
    d.design_capacity_vph,
    EXTRACT(hour FROM f.ts) AS hour_of_day,
    EXTRACT(dow FROM f.ts) AS day_of_week,
    CASE WHEN EXTRACT(dow FROM f.ts) IN (0, 6) THEN 1 ELSE 0 END AS weekend_flag
FROM fact_mobility_observations f
JOIN dim_city c ON f.city_id = c.city_id
JOIN dim_corridor d ON f.corridor_id = d.corridor_id;

