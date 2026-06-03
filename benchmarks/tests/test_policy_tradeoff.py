from pathlib import Path

from bench.policy_tradeoff import compute_strategy_tradeoffs, policy_segments
from bench.config import load_scenario


def test_policy_segments_follow_scenario_schedule() -> None:
    scenario = load_scenario(Path("scenarios/saturation-adaptive-long.yaml"))
    segments = policy_segments(scenario)

    assert [(segment.start_s, segment.end_s, segment.required_profile.value) for segment in segments] == [
        (0.0, 12.0, "balanced"),
        (12.0, 24.0, "heavy"),
        (24.0, 36.0, "balanced"),
        (36.0, 48.0, "lightweight"),
        (48.0, 60.0, "heavy"),
    ]


def test_adaptive_policy_matches_without_underprotection() -> None:
    scenario = load_scenario(Path("scenarios/saturation-adaptive-long.yaml"))
    tradeoffs = {item.label: item for item in compute_strategy_tradeoffs(scenario)}

    assert tradeoffs["Adaptive policy"].matched_share_pct == 100.0
    assert tradeoffs["Adaptive policy"].underprotected_share_pct == 0.0
    assert tradeoffs["Always balanced"].underprotected_share_pct == 40.0
    assert tradeoffs["Always heavy"].total_tier_message_units > tradeoffs["Adaptive policy"].total_tier_message_units
    assert tradeoffs["Always lightweight"].total_tier_message_units < tradeoffs["Adaptive policy"].total_tier_message_units
