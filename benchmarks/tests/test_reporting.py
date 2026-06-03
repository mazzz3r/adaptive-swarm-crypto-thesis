from pathlib import Path

from bench.reporting import write_thesis_report
from bench.results import RunSummary


def make_summary(*, mode: str, rate: float, p50: float, throughput: float, energy_per_message: float) -> RunSummary:
    return RunSummary(
        scenario_name=f"demo-{mode}-{int(rate)}",
        source_run_dir=f"/tmp/{mode}-{int(rate)}",
        mode=mode,
        cpu_limit_cores=0.05,
        memory_limit_mb=128,
        message_size_bytes=65536,
        message_rate_hz=rate,
        attempted_rate_msgs_s=throughput,
        peer_count=2,
        p50_latency_ms=p50,
        p95_latency_ms=95.0,
        p99_latency_ms=97.0,
        throughput_msgs_s=throughput,
        drop_rate_pct=0.0,
        error_rate_pct=0.0,
        bootstrap_time_ms=1.0,
        rekey_time_ms=1.0,
        bytes_sent=1000,
        crypto_overhead_bytes=100,
        cpu_pct_avg=3.5,
        memory_mb_avg=32.0,
        energy_proxy=100.0,
        energy_label="proxy",
        energy_proxy_per_delivered_message=energy_per_message,
        energy_per_message_label="proxy/msg",
        modeled_crypto_cost_total_ms=10.0,
        modeled_crypto_cost_avg_ms=1.0,
        modeled_crypto_cost_label="cost",
        mode_switches=0,
        messages_sent=10,
        messages_attempted=10,
        messages_received=10,
        rekey_count=1,
        heavy_messages=10 if mode == "static-heavy" else 0,
        balanced_messages=0,
        lightweight_messages=10 if mode == "static-lightweight" else 0,
        crypto_work_bytes=2048,
        crypto_work_mib_per_delivered_message=0.2,
        crypto_primitive_calls=20,
    )


def test_write_thesis_report(tmp_path: Path) -> None:
    comparison_dir = tmp_path / "comparison"
    comparison_dir.mkdir(parents=True)
    (comparison_dir / "comparison.csv").write_text("", encoding="utf-8")
    (comparison_dir / "comparison.json").write_text("[]", encoding="utf-8")
    (comparison_dir / "comparison_metrics.svg").write_text("", encoding="utf-8")
    (comparison_dir / "sweep_metrics.svg").write_text("", encoding="utf-8")

    report_path = write_thesis_report(
        results_root=tmp_path,
        comparison_dir=comparison_dir,
        summaries=[
            make_summary(mode="static-heavy", rate=100.0, p50=1.0, throughput=60.0, energy_per_message=13.5),
            make_summary(mode="adaptive", rate=100.0, p50=0.95, throughput=62.0, energy_per_message=13.4),
            make_summary(mode="static-lightweight", rate=100.0, p50=0.9, throughput=65.0, energy_per_message=13.2),
        ],
    )

    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "Thesis Benchmark Report" in text
    assert "Lightweight" in text
    assert "comparison_metrics.svg" in text
    assert "Attempted rate" in text
    assert "Selected Runs" in text
    assert "source_run_dir" in text
    assert "crypto work" in text
