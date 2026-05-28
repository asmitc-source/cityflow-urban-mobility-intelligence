from __future__ import annotations

import pandas as pd


def build_recommendations(corridor_df: pd.DataFrame) -> list[dict[str, str]]:
    if corridor_df.empty:
        return []
    ranked = corridor_df.sort_values(
        ["hotspot_probability", "infrastructure_load", "average_delay_min"],
        ascending=False,
    ).head(6)
    recommendations = []
    for _, row in ranked.iterrows():
        if row["infrastructure_load"] > 1.05:
            action = "Re-time signals, add reversible-lane controls, and prioritize bus movement during peak windows."
        elif row["weather_disruption_score"] > 25:
            action = "Improve drainage response, incident dispatch readiness, and rain-day traveler communication."
        else:
            action = "Monitor recurrent delay, optimize junction turning phases, and review corridor-level parking enforcement."
        recommendations.append(
            {
                "corridor": row["corridor_name"],
                "risk": f"{row['congestion_severity_index']:.1f} CSI / {row['average_delay_min']:.1f} min delay",
                "action": action,
            }
        )
    return recommendations

