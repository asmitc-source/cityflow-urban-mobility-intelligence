# Dataset Integration Plan

CityFlow is runnable with deterministic benchmark data, and the schema is ready for public datasets.

## Recommended Indian-City Data Sources

| Source | Data type | Integration path |
| --- | --- | --- |
| OpenStreetMap / Geofabrik India | Road network, road class, geometry | Build `dim_corridor`, lane proxies, junction density |
| OSMnx | Network extraction and route features | Route inefficiency, alternate path analysis |
| Open-Meteo Historical Weather API | Hourly weather | Rainfall, visibility, temperature, humidity |
| GTFS transit feeds from city agencies | Stops, routes, schedules | Transit delay frequency and route service coverage |
| Municipal open data portals | Incidents, roadworks, public infrastructure | Incident pressure, roadwork flag, event disruption |
| Census and city reports | Population, ward density, vehicle ownership | Demand normalization and benchmarking |

## Canonical Mapping

All external sources should be normalized into:

- `dim_city`
- `dim_corridor`
- `fact_mobility_observations`

This keeps Streamlit, SQL marts, and ML training stable even when source systems change.

## Real-Data Adapter Backlog

1. `OpenMeteoWeatherAdapter`
2. `OsmRoadNetworkAdapter`
3. `GtfsTransitAdapter`
4. `MunicipalIncidentAdapter`
5. `PopulationDensityAdapter`
