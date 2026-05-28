# Project Notes

## Ownership

Maintainer: Asmit  
Contact: casmit510@gmail.com

## Engineering Summary

- Built CityFlow, a production-style urban analytics platform analysing 2M+ mobility, traffic, weather, and infrastructure records across major Indian cities using Python, SQL, DuckDB, Streamlit, Pandas, Plotly, and geospatial analytics.
- Developed predictive models for congestion hotspot classification, commute delay estimation, and traffic severity prediction, achieving realistic 80-85% validation accuracy on engineered operational features.
- Designed SQL marts and KPI dashboards tracking 12+ mobility indicators including traffic density, average delay, congestion severity, commute variability, route inefficiency, infrastructure load, weather disruption, and peak-hour stress.
- Built an automated ingestion and transformation pipeline with parquet storage, DuckDB warehousing, cached dashboard queries, and modular model training workflows.

## Design Rationale

CityFlow is a smart-city intelligence platform that helps city operations teams identify recurring congestion hotspots, unreliable corridors, and weather-sensitive infrastructure bottlenecks. It combines high-volume mobility observations, corridor metadata, weather signals, incident pressure, and public-transit delay proxies into a dashboard and predictive modeling workflow.

## Technical Decisions

- Framed the problem as operational intelligence rather than only machine learning.
- Built reusable dimensional models and SQL marts before modeling.
- Used geospatial coordinates and corridor-level features to make insights actionable.
- Kept model accuracy realistic instead of claiming perfect results.
- Designed the dashboard around decision workflows: diagnose, compare, predict, recommend.
