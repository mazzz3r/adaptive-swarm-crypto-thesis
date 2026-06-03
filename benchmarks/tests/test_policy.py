from bench.config import BenchmarkMode
from bench.policy import select_runtime_profile


def test_threshold_policy_prefers_heavy_on_high_threat() -> None:
    profile, reason = select_runtime_profile(BenchmarkMode.ADAPTIVE, threat=0.95, energy=0.9)
    assert profile.value == "heavy"
    assert reason == "high-threat"


def test_threshold_policy_prefers_lightweight_on_low_energy() -> None:
    profile, reason = select_runtime_profile(BenchmarkMode.ADAPTIVE, threat=0.2, energy=0.1)
    assert profile.value == "lightweight"
    assert reason == "low-energy"


def test_static_balanced_policy_uses_balanced_profile() -> None:
    profile, reason = select_runtime_profile(BenchmarkMode.STATIC_BALANCED, threat=0.95, energy=0.1)
    assert profile.value == "balanced"
    assert reason == "static-balanced"


def test_threshold_policy_uses_balanced_default() -> None:
    profile, reason = select_runtime_profile(BenchmarkMode.ADAPTIVE, threat=0.2, energy=0.8)
    assert profile.value == "balanced"
    assert reason == "balanced-default"
