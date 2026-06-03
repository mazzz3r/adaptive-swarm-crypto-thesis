from bench.config import ResourceLimits
from pathlib import Path

from bench.orchestrator import build_resource_update_kwargs, prepare_output_root


def test_build_resource_update_kwargs() -> None:
    update_kwargs = build_resource_update_kwargs(ResourceLimits(cpu_limit_cores=0.5, memory_limit_mb=256))
    assert update_kwargs["cpu_period"] == 100_000
    assert update_kwargs["cpu_quota"] == 50_000
    assert update_kwargs["mem_limit"] == 256 * 1024 * 1024
    assert update_kwargs["memswap_limit"] == 256 * 1024 * 1024


def test_build_resource_update_kwargs_empty() -> None:
    assert build_resource_update_kwargs(ResourceLimits()) == {}


def test_prepare_output_root_falls_back_from_file(tmp_path: Path) -> None:
    blocked = tmp_path / "results"
    blocked.write_text("occupied", encoding="utf-8")
    prepared = prepare_output_root(blocked)
    assert prepared == tmp_path / "benchmark-results"
    assert prepared.is_dir()
