from __future__ import annotations

from pathlib import Path

import duckdb
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from cityflow.features.build_features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, feature_columns, prepare_model_frame
from cityflow.utils.config import project_path


def load_training_frame(conn: duckdb.DuckDBPyConnection, limit: int = 500_000) -> pd.DataFrame:
    safe_limit = max(1, int(limit))
    return conn.execute(
        f"""
        SELECT *
        FROM mart_model_scoring_frame
        USING SAMPLE reservoir({safe_limit} ROWS) REPEATABLE (42)
        """
    ).fetchdf()


def build_preprocessor() -> ColumnTransformer:
    numeric = NUMERIC_FEATURES + [
        "roadwork_flag",
        "event_flag",
        "peak_hour_flag",
        "load_per_lane",
        "capacity_pressure",
        "rain_peak_interaction",
        "incident_peak_interaction",
    ]
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def train_models(df: pd.DataFrame, output_dir: Path | None = None) -> dict[str, dict[str, float]]:
    output = output_dir or project_path("models")
    output.mkdir(parents=True, exist_ok=True)
    frame = prepare_model_frame(df)
    x = frame[feature_columns()]

    metrics: dict[str, dict[str, float]] = {}

    for target, filename in [
        ("hotspot_label", "hotspot_classifier.joblib"),
        ("severity_label", "severity_classifier.joblib"),
    ]:
        y = frame[target]
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
        model = Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=160,
                        min_samples_leaf=12,
                        max_depth=15,
                        n_jobs=-1,
                        random_state=42,
                        class_weight="balanced_subsample",
                    ),
                ),
            ]
        )
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        metrics[target] = {"accuracy": float(accuracy_score(y_test, predictions))}
        report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
        metrics[target]["macro_f1"] = float(report["macro avg"]["f1-score"])
        joblib.dump(model, output / filename)

    y = frame["delay_min"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    delay_model = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", GradientBoostingRegressor(random_state=42, n_estimators=180, max_depth=4, learning_rate=0.055)),
        ]
    )
    delay_model.fit(x_train, y_train)
    delay_predictions = delay_model.predict(x_test)
    metrics["delay_min"] = {
        "mae": float(mean_absolute_error(y_test, delay_predictions)),
        "r2": float(r2_score(y_test, delay_predictions)),
    }
    joblib.dump(delay_model, output / "delay_estimator.joblib")

    pd.DataFrame(metrics).T.to_json(output / "model_metrics.json", indent=2)
    return metrics
