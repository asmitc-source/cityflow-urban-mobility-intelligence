from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from cityflow.data.warehouse import build_marts, connect_warehouse
from cityflow.services.recommendations import build_recommendations
from cityflow.utils.config import project_path


st.set_page_config(page_title="CityFlow", page_icon="CF", layout="wide")

CUSTOM_CSS = """
<style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(20,31,43,.92), rgba(25,54,68,.78));
        border: 1px solid rgba(255,255,255,.08);
        padding: 16px 18px;
        border-radius: 8px;
        box-shadow: 0 12px 28px rgba(0,0,0,.16);
    }
    [data-testid="stMetricLabel"] {color: #9fb3c8;}
    .section-title {font-size: 1.2rem; font-weight: 700; margin: 1.2rem 0 .4rem;}
    .recommendation {
        border: 1px solid rgba(148,163,184,.22);
        border-radius: 8px;
        padding: 14px 16px;
        margin: 8px 0;
        background: rgba(15,23,42,.72);
    }
    .small-muted {color: #94a3b8; font-size: .9rem;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    conn = connect_warehouse()
    build_marts(conn)
    return conn


@st.cache_data(ttl=600)
def load_city_list() -> list[str]:
    conn = get_connection()
    return [row[0] for row in conn.execute("SELECT city_name FROM dim_city ORDER BY city_name").fetchall()]


@st.cache_data(ttl=600)
def load_hourly(city: str) -> pd.DataFrame:
    conn = get_connection()
    return conn.execute(
        """
        SELECT *
        FROM mart_city_hourly_kpis
        WHERE city_name = ?
        ORDER BY hour_ts
        """,
        [city],
    ).fetchdf()


@st.cache_data(ttl=600)
def load_corridors(city: str) -> pd.DataFrame:
    conn = get_connection()
    return conn.execute(
        """
        SELECT *
        FROM mart_corridor_stress
        WHERE city_name = ?
        ORDER BY congestion_severity_index DESC
        """,
        [city],
    ).fetchdf()


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label, value, delta=delta)


def render_header(city: str) -> None:
    left, right = st.columns([0.72, 0.28])
    with left:
        st.title("CityFlow")
        st.caption("Urban Mobility & Infrastructure Intelligence System")
    with right:
        st.markdown(f"<div class='small-muted'>Command center view</div><h3>{city}</h3>", unsafe_allow_html=True)


def render_kpis(df: pd.DataFrame) -> None:
    latest = df.tail(168)
    cols = st.columns(4)
    with cols[0]:
        metric_card("Traffic Density", f"{latest['traffic_density'].mean():,.0f}", "vehicles / lane-km")
    with cols[1]:
        metric_card("Avg Delay", f"{latest['average_delay_min'].mean():.1f} min", "rolling 7 days")
    with cols[2]:
        metric_card("Congestion Severity", f"{latest['congestion_severity_index'].mean():.1f}", "0-100 index")
    with cols[3]:
        metric_card("Peak Stress", f"{latest['peak_hour_stress_score'].mean():.1f}", "peak-hour CSI")

    cols = st.columns(4)
    with cols[0]:
        metric_card("Route Inefficiency", f"{latest['route_inefficiency_score'].mean():.1f}%", "vs free-flow")
    with cols[1]:
        metric_card("Infra Load", f"{latest['infrastructure_load_utilization'].mean():.2f}x", "capacity ratio")
    with cols[2]:
        metric_card("Weather Disruption", f"{latest['weather_disruption_score'].mean():.1f}", "rain/visibility")
    with cols[3]:
        metric_card("Throughput", f"{latest['mobility_throughput'].sum()/1_000_000:.2f}M", "vehicles observed")


def render_trends(df: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Temporal Traffic Pattern Analysis</div>", unsafe_allow_html=True)
    left, right = st.columns([0.62, 0.38])
    with left:
        trend = df.set_index("hour_ts")[["congestion_severity_index", "average_delay_min", "weather_disruption_score"]].rolling(24).mean().reset_index()
        fig = px.line(
            trend,
            x="hour_ts",
            y=["congestion_severity_index", "average_delay_min", "weather_disruption_score"],
            labels={"value": "Index / minutes", "hour_ts": ""},
            template="plotly_dark",
        )
        fig.update_layout(height=390, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        heat = df.pivot_table(index="hour_of_day", columns=df["hour_ts"].dt.day_name(), values="congestion_severity_index", aggfunc="mean")
        ordered = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heat = heat[[c for c in ordered if c in heat.columns]]
        fig = px.imshow(heat, color_continuous_scale="Reds", aspect="auto", template="plotly_dark")
        fig.update_layout(height=390, xaxis_title="", yaxis_title="Hour")
        st.plotly_chart(fig, use_container_width=True)


def render_map(corridors: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Congestion Hotspot Map</div>", unsafe_allow_html=True)
    fig = px.scatter_mapbox(
        corridors,
        lat="lat",
        lon="lon",
        color="congestion_severity_index",
        size="infrastructure_load",
        hover_name="corridor_name",
        hover_data=["zone_name", "road_class", "average_delay_min", "hotspot_probability"],
        color_continuous_scale="Turbo",
        zoom=10,
        height=470,
    )
    fig.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)


def render_corridor_table(corridors: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Infrastructure Utilization Metrics</div>", unsafe_allow_html=True)
    cols = [
        "corridor_name",
        "zone_name",
        "road_class",
        "infrastructure_load",
        "congestion_severity_index",
        "average_delay_min",
        "route_inefficiency_score",
        "hotspot_probability",
    ]
    st.dataframe(corridors[cols].head(15), use_container_width=True, hide_index=True)


def render_predictive_section(corridors: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Predictive Insights</div>", unsafe_allow_html=True)
    metrics_path = project_path("models", "model_metrics.json")
    left, right = st.columns([0.45, 0.55])
    with left:
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            st.metric("Hotspot Model Accuracy", f"{metrics.get('hotspot_label', {}).get('accuracy', 0):.2%}")
            st.metric("Severity Model Accuracy", f"{metrics.get('severity_label', {}).get('accuracy', 0):.2%}")
            st.metric("Delay Estimator MAE", f"{metrics.get('delay_min', {}).get('mae', 0):.2f} min")
        else:
            st.info("Run `python scripts/train_models.py` to populate production model metrics.")
    with right:
        top = corridors.head(10).sort_values("hotspot_probability")
        fig = go.Figure(
            go.Bar(
                x=top["hotspot_probability"],
                y=top["corridor_name"],
                orientation="h",
                marker_color=top["congestion_severity_index"],
            )
        )
        fig.update_layout(template="plotly_dark", height=360, xaxis_title="Hotspot probability", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)


def render_recommendations(corridors: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Operational Recommendations</div>", unsafe_allow_html=True)
    for rec in build_recommendations(corridors):
        st.markdown(
            f"<div class='recommendation'><b>{rec['corridor']}</b><br>"
            f"<span class='small-muted'>{rec['risk']}</span><br>{rec['action']}</div>",
            unsafe_allow_html=True,
        )


def main() -> None:
    try:
        cities = load_city_list()
    except Exception:
        st.error("CityFlow warehouse not found. Run `python scripts/run_pipeline.py --rows 250000` first.")
        st.stop()

    with st.sidebar:
        st.header("Controls")
        city = st.selectbox("City", cities, index=cities.index("Bengaluru") if "Bengaluru" in cities else 0)
        st.caption("Use this control center to compare congestion, delay, weather disruption, and infrastructure stress.")

    hourly = load_hourly(city)
    corridors = load_corridors(city)
    render_header(city)
    render_kpis(hourly)
    render_map(corridors)
    render_trends(hourly)
    render_corridor_table(corridors)
    render_predictive_section(corridors)
    render_recommendations(corridors)


if __name__ == "__main__":
    main()

