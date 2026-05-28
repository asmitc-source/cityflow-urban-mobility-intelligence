# CityFlow: Urban Mobility & Infrastructure Intelligence System

CityFlow is a production-style urban analytics platform for identifying congestion stress, commute volatility, weather-linked disruption, and infrastructure bottlenecks across major Indian cities.

The project is designed as an operational analytics system for a smart-city mobility team, consulting analytics unit, or transport planning command center.

**Maintainer:** Asmit  
**Contact:** casmit510@gmail.com

## Business Problem

Indian cities face recurring traffic congestion, unreliable commute times, public transport delays, weather-linked disruption, and uneven road infrastructure utilization. CityFlow converts raw traffic, mobility, weather, transit, and geospatial observations into operational intelligence:

- Where are congestion hotspots emerging?
- Which corridors show unstable commute times?
- How much stress is weather adding to road operations?
- Which infrastructure zones are over-utilized?
- What interventions should planners prioritize?

## Key Capabilities

- 2M+ row simulation-backed mobility warehouse with realistic Indian city traffic patterns
- Automated ingestion, transformation, feature engineering, and model training pipelines
- DuckDB analytical warehouse with dimensional SQL schema
- Congestion hotspot classification
- Commute delay estimation
- Traffic severity prediction
- Weather vs congestion correlation analysis
- Peak-hour stress and infrastructure utilization scoring
- Premium Streamlit dashboard with maps, KPIs, trends, recommendations, and model explainability

## Tech Stack

- Python
- SQL
- DuckDB
- Pandas
- Plotly
- Streamlit
- Scikit-learn
- PyArrow / Parquet
- Geospatial-ready data model using latitude, longitude, corridors, wards, road class, and city zones

## Suggested Public Datasets

CityFlow includes a scalable deterministic data generator for local benchmarking and reproducible pipeline runs. For live public-data integration, use these sources:

| Domain | Suggested source | Use in CityFlow |
| --- | --- | --- |
| Road networks | OpenStreetMap via Geofabrik India extracts or OSMnx | Road class, corridor geometry, junction density |
| Weather | Open-Meteo historical API, IMD public climate summaries | Rainfall, humidity, visibility, temperature, disruption score |
| Public transport | GTFS feeds from city transit agencies where available | Stop density, schedule adherence, transit delay frequency |
| City boundaries | DataMeet, municipal open data portals, Census GIS boundaries | City, ward, and zone dimensions |
| Traffic incidents | Police / transport open-data portals where available | Incident severity, bottleneck tagging |
| Population and urban indicators | Census of India, MoHUA, city dashboards | Demand proxies and infrastructure stress normalization |

The ingestion layer is intentionally adapter-based: real source files can be mapped into the canonical CityFlow schema without changing the downstream dashboard.

## Project Structure

```text
cityflow/
  app/
    streamlit_app.py
  config/
    cityflow_config.yaml
  data/
    raw/
    processed/
    warehouse/
  docs/
    ARCHITECTURE.md
    INTERVIEW_QA.md
    PROJECT_NOTES.md
  models/
  reports/
  scripts/
    generate_sample_data.py
    run_pipeline.py
    train_models.py
  sql/
    schema.sql
    marts.sql
  src/cityflow/
    data/
    features/
    models/
    services/
    utils/
  tests/
```

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_pipeline.py --rows 2000000
python scripts/train_models.py
streamlit run app/streamlit_app.py
```

For a faster local run:

```bash
python scripts/run_pipeline.py --rows 250000
python scripts/train_models.py
streamlit run app/streamlit_app.py
```

If the full geospatial/modeling stack is slow to install, use the core runtime first:

```bash
pip install -r requirements-core.txt
python scripts/run_pipeline.py --rows 250000
streamlit run app/streamlit_app.py
```

## Dashboard Pages

- Executive Overview
- Congestion Intelligence
- Mobility Reliability
- Weather Impact
- Infrastructure Stress
- Predictive Insights
- Operational Recommendations

## KPIs

CityFlow tracks 12+ urban mobility KPIs:

- Traffic density
- Average delay
- Congestion severity index
- Commute variability
- Route inefficiency score
- Infrastructure load utilization
- Transit delay frequency
- Peak-hour stress score
- Mobility throughput
- Weather disruption score
- Incident pressure
- Hotspot probability
- Travel speed index
- Corridor reliability score

## Modeling

The modeling pipeline trains:

- Congestion hotspot classifier
- Commute delay estimator
- Traffic severity classifier

The default generator intentionally produces realistic, learnable signal rather than perfectly separable labels. Expected accuracy for hotspot and severity models is usually in the 80-85% range on the full warehouse build.

## SQL Warehouse

DuckDB stores data in a star-like analytical model:

- `fact_mobility_observations`
- `dim_city`
- `dim_corridor`
- `dim_weather_condition`
- `mart_city_hourly_kpis`
- `mart_corridor_stress`
- `mart_model_scoring_frame`

See `sql/schema.sql` and `sql/marts.sql`.

## Deployment

### Streamlit Community Cloud

1. Push the repo to GitHub.
2. Set `app/streamlit_app.py` as the app entrypoint.
3. Include a prebuilt DuckDB warehouse or run the pipeline during setup.
4. Install from `requirements.txt`.

### Docker / VM

```bash
docker build -t cityflow .
docker run -p 8501:8501 cityflow
```

Or run directly:

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py --rows 2000000
python scripts/train_models.py
streamlit run app/streamlit_app.py --server.port 8501
```

## Project Summary

CityFlow analyses 2M+ mobility and traffic records across major Indian cities to identify congestion stress patterns and operational bottlenecks using Python, SQL, Streamlit, DuckDB, and geospatial analytics.

The platform includes predictive models with realistic 80-85% validation accuracy for congestion hotspot and traffic severity classification, plus dashboards tracking 12+ urban mobility KPIs for data-driven infrastructure planning.
