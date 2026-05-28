# SQL Schema

The warehouse is defined in `sql/schema.sql` and analytical marts are defined in `sql/marts.sql`.

## Core Tables

### dim_city

City-level reference data including state, centroid, population, and registered vehicle estimates.

### dim_corridor

Road corridor metadata including zone, road class, lane count, design capacity, length, and geographic endpoints.

### fact_mobility_observations

High-volume event-level table containing mobility, delay, weather, incident, infrastructure load, and predictive label fields.

## Analytical Marts

### mart_city_hourly_kpis

Hourly city-level KPI view powering executive dashboard cards and temporal analysis.

### mart_corridor_stress

Corridor-level utilization and hotspot view powering geospatial maps, risk tables, and recommendations.

### mart_model_scoring_frame

Feature-rich training view for congestion hotspot, traffic severity, and delay estimation models.

