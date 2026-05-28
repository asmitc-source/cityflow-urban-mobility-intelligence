from cityflow.data.generate import build_city_dimension, build_corridor_dimension, generate_mobility_observations


def test_generator_creates_expected_columns():
    cities = build_city_dimension()
    corridors = build_corridor_dimension(corridors_per_city=2)
    facts = generate_mobility_observations(1000, corridors, "2024-01-01", 5)
    assert cities.shape[0] >= 6
    assert corridors.shape[0] == 12
    assert facts.shape[0] == 1000
    assert {"congestion_severity_index", "hotspot_label", "weather_disruption_score"}.issubset(facts.columns)

