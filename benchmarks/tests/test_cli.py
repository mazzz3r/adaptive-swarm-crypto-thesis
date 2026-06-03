import pytest

from bench.cli import parse_float_list, parse_modes, parse_network_profiles, parse_rates
from bench.config import BenchmarkMode


def test_parse_rates() -> None:
    assert parse_rates("50,100,200") == [50.0, 100.0, 200.0]


def test_parse_modes() -> None:
    assert parse_modes("static-heavy,static-balanced,adaptive") == [
        BenchmarkMode.STATIC_HEAVY,
        BenchmarkMode.STATIC_BALANCED,
        BenchmarkMode.ADAPTIVE,
    ]


def test_parse_rates_rejects_invalid() -> None:
    with pytest.raises(Exception):
        parse_rates("0,-1")


def test_parse_float_list() -> None:
    assert parse_float_list("0.05,0.10,0.25") == [0.05, 0.10, 0.25]


def test_parse_network_profiles() -> None:
    profiles = parse_network_profiles("clean=0/0/0,mild=20/5/2,lossy=50/15/5%")
    assert [profile.label for profile in profiles] == ["clean", "mild", "lossy"]
    assert profiles[1].delay_ms == 20
    assert profiles[1].jitter_ms == 5
    assert profiles[1].loss_pct == 2
