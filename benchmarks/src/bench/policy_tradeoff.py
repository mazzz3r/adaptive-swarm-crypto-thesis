from __future__ import annotations

from dataclasses import dataclass

from .config import BenchmarkMode, RuntimeProfile, Scenario
from .policy import select_runtime_profile


PROFILE_TIER = {
    RuntimeProfile.LIGHTWEIGHT: 1,
    RuntimeProfile.BALANCED: 2,
    RuntimeProfile.HEAVY: 3,
}

PROFILE_LABEL = {
    RuntimeProfile.LIGHTWEIGHT: "Lightweight",
    RuntimeProfile.BALANCED: "Balanced",
    RuntimeProfile.HEAVY: "Heavy",
}


@dataclass(frozen=True)
class PolicySegment:
    start_s: float
    end_s: float
    required_profile: RuntimeProfile
    threat: float
    energy: float

    @property
    def duration_s(self) -> float:
        return max(self.end_s - self.start_s, 0.0)


@dataclass(frozen=True)
class StrategyTradeoff:
    label: str
    cumulative_points: list[tuple[float, float]]
    matched_share_pct: float
    overprotected_share_pct: float
    underprotected_share_pct: float
    total_tier_message_units: float


def _value_at(schedule, elapsed_s: float) -> float:
    current = schedule[0].value
    for item in schedule:
        if elapsed_s < item.at_s:
            break
        current = item.value
    return current


def policy_segments(scenario: Scenario) -> list[PolicySegment]:
    boundaries = {0.0, scenario.duration_s}
    boundaries.update(item.at_s for item in scenario.threat_schedule if 0 <= item.at_s <= scenario.duration_s)
    boundaries.update(item.at_s for item in scenario.energy_schedule if 0 <= item.at_s <= scenario.duration_s)
    ordered = sorted(boundaries)

    segments: list[PolicySegment] = []
    for start_s, end_s in zip(ordered, ordered[1:]):
        if end_s <= start_s:
            continue
        threat = _value_at(scenario.threat_schedule, start_s)
        energy = _value_at(scenario.energy_schedule, start_s)
        required_profile, _ = select_runtime_profile(BenchmarkMode.ADAPTIVE, threat, energy)
        segments.append(
            PolicySegment(
                start_s=start_s,
                end_s=end_s,
                required_profile=required_profile,
                threat=threat,
                energy=energy,
            )
        )
    return segments


def compute_strategy_tradeoffs(scenario: Scenario) -> list[StrategyTradeoff]:
    segments = policy_segments(scenario)
    strategies: list[tuple[str, RuntimeProfile | None]] = [
        ("Always heavy", RuntimeProfile.HEAVY),
        ("Always balanced", RuntimeProfile.BALANCED),
        ("Always lightweight", RuntimeProfile.LIGHTWEIGHT),
        ("Adaptive policy", None),
    ]

    tradeoffs: list[StrategyTradeoff] = []
    total_message_time = max(scenario.duration_s * scenario.message_rate_hz, 1e-9)
    for label, static_profile in strategies:
        cumulative = 0.0
        cumulative_points = [(0.0, 0.0)]
        matched = 0.0
        overprotected = 0.0
        underprotected = 0.0

        for segment in segments:
            actual_profile = static_profile or segment.required_profile
            segment_messages = segment.duration_s * scenario.message_rate_hz
            tier_delta = PROFILE_TIER[actual_profile] * segment_messages
            cumulative_points.append((segment.start_s, cumulative))
            cumulative += tier_delta
            cumulative_points.append((segment.end_s, cumulative))

            actual_tier = PROFILE_TIER[actual_profile]
            required_tier = PROFILE_TIER[segment.required_profile]
            if actual_tier == required_tier:
                matched += segment_messages
            elif actual_tier > required_tier:
                overprotected += segment_messages
            else:
                underprotected += segment_messages

        tradeoffs.append(
            StrategyTradeoff(
                label=label,
                cumulative_points=cumulative_points,
                matched_share_pct=round(matched / total_message_time * 100, 3),
                overprotected_share_pct=round(overprotected / total_message_time * 100, 3),
                underprotected_share_pct=round(underprotected / total_message_time * 100, 3),
                total_tier_message_units=round(cumulative, 3),
            )
        )
    return tradeoffs
