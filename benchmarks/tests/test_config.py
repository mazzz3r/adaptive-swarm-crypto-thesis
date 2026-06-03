from pathlib import Path

import pytest

from bench.config import Scenario, load_scenario


def test_load_stable_scenario() -> None:
    scenario = load_scenario(Path("scenarios/stable.yaml"))
    assert scenario.name == "stable"
    assert scenario.peer_count >= 2
    assert scenario.threat_schedule[0].at_s == 0
    assert scenario.resources.cpu_limit_cores is None


def test_load_constrained_scenario() -> None:
    scenario = load_scenario(Path("scenarios/stable-constrained.yaml"))
    assert scenario.resources.cpu_limit_cores == 0.5
    assert scenario.resources.memory_limit_mb == 256


def test_invalid_scenario_rejects_bad_peer_count() -> None:
    with pytest.raises(Exception):
        Scenario(
            name="bad",
            mode="adaptive",
            duration_s=1,
            message_rate_hz=1,
            message_size_bytes=16,
            peer_count=1,
            rekey_interval_s=1,
        )
