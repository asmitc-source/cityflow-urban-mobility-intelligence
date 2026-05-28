# Interview Questions and Answers

## 1. Why did you choose DuckDB?

DuckDB is fast for local analytical workloads, reads parquet efficiently, and avoids the overhead of running a server database for the first deployment. It also keeps the architecture portable because the same dimensional design can move to PostgreSQL, BigQuery, or Snowflake.

## 2. How is this different from a beginner dashboard?

The project uses a warehouse-style schema, SQL marts, scalable parquet files, model training scripts, cached dashboard queries, operational KPIs, geospatial views, and recommendation logic. It is structured like an analytics product rather than a notebook-only project.

## 3. Why generate data if public datasets are available?

Public Indian traffic feeds are fragmented and often not available at event-level scale. The project includes realistic benchmark data so the system can be run immediately, while the adapter design allows public OSM, weather, GTFS, and municipal data to be integrated later.

## 4. What features helped predict congestion?

Important features include infrastructure load, traffic density, delay, speed ratio, rainfall, visibility, incident count, peak-hour flag, road class, lane count, and corridor length.

## 5. Why target 80-85% accuracy?

Operational traffic prediction is noisy because congestion depends on behavior, incidents, weather, construction, and local disruptions. A realistic accuracy band is more credible than an artificially perfect score.

## 6. How would you deploy this?

For a lightweight deployment, I would use Streamlit Cloud with a prebuilt DuckDB file. For production, I would schedule ingestion with Airflow or Prefect, store facts in a warehouse, use dbt for transformations, and deploy the app behind authentication.

## 7. How would you add live data?

I would create source adapters for Open-Meteo weather, OSM road networks, GTFS transit feeds, and municipal traffic incident files. Each adapter would normalize source data into the CityFlow canonical schema.

## 8. What are the main KPIs?

Traffic density, average delay, congestion severity index, commute variability, route inefficiency, infrastructure load utilization, transit delay frequency, peak-hour stress score, mobility throughput, weather disruption score, incident pressure, hotspot probability, and speed index.

## 9. How do you validate model performance?

The training pipeline uses train-test splits, stratification for classifiers, accuracy and macro-F1 for classification, and MAE/R2 for delay estimation. A production version would add time-based validation to avoid leakage.

## 10. What would you improve next?

I would add real GTFS feeds, OSMnx-derived road topology, H3 spatial indexing, scheduled data refreshes, SHAP explainability views in the app, and city-to-city benchmark reporting.
