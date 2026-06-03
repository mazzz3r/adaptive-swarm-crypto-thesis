from pathlib import Path
from dataclasses import replace

from bench.config import BenchmarkMode, load_scenario
from bench.plots import generate_comparison_plot, generate_plots, generate_sensitivity_plot, generate_sweep_plot
from bench.results import aggregate_run, collect_summaries, collect_summaries_from_run_dirs, load_summary, write_comparison, write_summary


def test_aggregation_and_plot_generation(tmp_path: Path) -> None:
    scenario = load_scenario("scenarios/stable.yaml")
    primary_metrics = {
        "latencies_ms": [10.0, 12.0, 14.0, 20.0],
        "messages_attempted": 4,
        "messages_sent": 4,
        "messages_received": 0,
        "send_errors": 0,
        "bytes_plaintext": 2048,
        "bytes_ciphertext": 2304,
        "bytes_overhead": 256,
        "rekey_count": 1,
        "bootstrap_times_ms": [15.0],
        "rekey_times_ms": [5.0],
        "mode_switches": [{"at_s": 10.0, "profile": "heavy", "reason": "high-threat"}],
        "heavy_messages": 1,
        "balanced_messages": 2,
        "lightweight_messages": 1,
    }
    receiver_metrics = {
        "messages_received": 4,
        "bootstrap_times_ms": [15.0],
    }
    summary = aggregate_run(
        scenario=scenario,
        primary_metrics=primary_metrics,
        receiver_metrics=receiver_metrics,
        cpu_pct_avg=12.5,
        memory_mb_avg=32.0,
        cpu_time_s=1.5,
    )
    csv_path, json_path = write_summary(summary, tmp_path)
    stored_summary = load_summary(json_path)
    assert csv_path.exists()
    assert json_path.exists()
    assert summary.cpu_limit_cores is None
    assert summary.memory_limit_mb is None
    assert summary.energy_proxy_per_delivered_message > 0
    assert summary.heavy_messages == 1
    assert summary.balanced_messages == 2
    assert summary.lightweight_messages == 1
    assert summary.crypto_work_mib_per_delivered_message > 0
    assert summary.attempted_rate_msgs_s == 4.0 / scenario.duration_s
    assert summary.duration_s == scenario.duration_s
    assert summary.network_delay_ms == scenario.network.delay_ms
    assert summary.rekey_interval_s == scenario.rekey_interval_s
    assert stored_summary.source_run_dir == str(tmp_path.resolve())
    generated = generate_plots(
        output_dir=tmp_path,
        summary=summary,
        latencies_ms=primary_metrics["latencies_ms"],
        mode_switches=primary_metrics["mode_switches"],
    )
    assert generated
    assert all(path.exists() for path in generated)


def test_comparison_artifacts(tmp_path: Path) -> None:
    scenario = load_scenario("scenarios/stable.yaml")
    receiver_metrics = {
        "messages_received": 4,
        "bootstrap_times_ms": [15.0],
    }
    primary_a = {
        "latencies_ms": [10.0, 12.0, 14.0, 20.0],
        "messages_attempted": 4,
        "messages_sent": 4,
        "messages_received": 0,
        "send_errors": 0,
        "bytes_plaintext": 2048,
        "bytes_ciphertext": 2304,
        "bytes_overhead": 256,
        "rekey_count": 1,
        "bootstrap_times_ms": [15.0],
        "rekey_times_ms": [5.0],
        "mode_switches": [],
        "heavy_messages": 1,
        "balanced_messages": 2,
        "lightweight_messages": 1,
    }
    primary_b = {
        **primary_a,
        "latencies_ms": [8.0, 9.0, 10.0, 11.0],
        "bytes_ciphertext": 2200,
        "heavy_messages": 0,
        "balanced_messages": 0,
        "lightweight_messages": 4,
    }
    summary_a = aggregate_run(
        scenario=scenario,
        primary_metrics=primary_a,
        receiver_metrics=receiver_metrics,
        cpu_pct_avg=12.5,
        memory_mb_avg=32.0,
        cpu_time_s=1.5,
    )
    summary_b = aggregate_run(
        scenario=scenario.model_copy(update={"mode": BenchmarkMode.STATIC_LIGHTWEIGHT, "name": "stable-light"}),
        primary_metrics=primary_b,
        receiver_metrics=receiver_metrics,
        cpu_pct_avg=10.0,
        memory_mb_avg=30.0,
        cpu_time_s=1.0,
    )
    write_summary(summary_a, tmp_path / "run-a")
    write_summary(summary_b, tmp_path / "run-b")

    summaries = collect_summaries(tmp_path)
    comparison_dir = tmp_path / "comparison"
    csv_path, json_path = write_comparison(summaries, comparison_dir)
    generated = generate_comparison_plot(output_dir=comparison_dir, summaries=summaries)

    assert len(summaries) == 2
    assert csv_path.exists()
    assert json_path.exists()
    assert all(summary.source_run_dir for summary in summaries)
    assert generated
    assert all(path.exists() for path in generated)


def test_sweep_plot_artifacts(tmp_path: Path) -> None:
    scenario = load_scenario("scenarios/stable.yaml")
    receiver_metrics = {
        "messages_received": 4,
        "bootstrap_times_ms": [15.0],
    }
    summaries = []
    for rate, mode in [(50.0, BenchmarkMode.STATIC_HEAVY), (100.0, BenchmarkMode.STATIC_HEAVY), (50.0, BenchmarkMode.STATIC_LIGHTWEIGHT)]:
        primary = {
            "latencies_ms": [10.0, 12.0, 14.0, 20.0],
            "messages_attempted": 4,
            "messages_sent": 4,
            "messages_received": 0,
            "send_errors": 0,
            "bytes_plaintext": 2048,
            "bytes_ciphertext": 2304,
            "bytes_overhead": 256,
            "rekey_count": 1,
            "bootstrap_times_ms": [15.0],
            "rekey_times_ms": [5.0],
            "mode_switches": [],
            "heavy_messages": 4 if mode == BenchmarkMode.STATIC_HEAVY else 0,
            "balanced_messages": 0,
            "lightweight_messages": 4 if mode == BenchmarkMode.STATIC_LIGHTWEIGHT else 0,
        }
        summaries.append(
            aggregate_run(
                scenario=scenario.model_copy(update={"message_rate_hz": rate, "mode": mode, "name": f"{mode.value}-{int(rate)}"}),
                primary_metrics=primary,
                receiver_metrics=receiver_metrics,
                cpu_pct_avg=12.0,
                memory_mb_avg=30.0,
                cpu_time_s=1.0,
            )
        )
    generated = generate_sweep_plot(output_dir=tmp_path, summaries=summaries)
    assert generated
    assert all(path.exists() for path in generated)


def test_sensitivity_plot_artifacts(tmp_path: Path) -> None:
    scenario = load_scenario("scenarios/stable.yaml")
    receiver_metrics = {
        "messages_received": 4,
        "bootstrap_times_ms": [15.0],
    }
    primary = {
        "latencies_ms": [10.0, 12.0, 14.0, 20.0],
        "messages_attempted": 4,
        "messages_sent": 4,
        "messages_received": 0,
        "send_errors": 0,
        "bytes_plaintext": 2048,
        "bytes_ciphertext": 2304,
        "bytes_overhead": 256,
        "rekey_count": 1,
        "bootstrap_times_ms": [15.0],
        "rekey_times_ms": [5.0],
        "mode_switches": [],
        "heavy_messages": 4,
        "balanced_messages": 0,
        "lightweight_messages": 0,
    }
    summaries = []
    for cpu_limit in (0.05, 0.10):
        summary = aggregate_run(
            scenario=scenario.model_copy(update={"mode": BenchmarkMode.STATIC_HEAVY, "name": f"cpu-{cpu_limit}"}),
            primary_metrics=primary,
            receiver_metrics=receiver_metrics,
            cpu_pct_avg=12.0,
            memory_mb_avg=30.0,
            cpu_time_s=1.0,
        )
        summaries.append(replace(summary, matrix_group="cpu-sensitivity", cpu_limit_cores=cpu_limit))
    generated = generate_sensitivity_plot(
        output_dir=tmp_path,
        summaries=summaries,
        matrix_group="cpu-sensitivity",
        x_field="cpu_limit_cores",
        x_label="CPU cap (cores)",
        filename="cpu_sensitivity.svg",
    )
    assert generated
    assert all(path.exists() for path in generated)


def test_collect_summaries_from_run_dirs_only_reads_selected_runs(tmp_path: Path) -> None:
    scenario = load_scenario("scenarios/stable.yaml")
    receiver_metrics = {
        "messages_received": 4,
        "bootstrap_times_ms": [15.0],
    }
    primary = {
        "latencies_ms": [10.0, 12.0, 14.0, 20.0],
        "messages_attempted": 4,
        "messages_sent": 4,
        "messages_received": 0,
        "send_errors": 0,
        "bytes_plaintext": 2048,
        "bytes_ciphertext": 2304,
        "bytes_overhead": 256,
        "rekey_count": 1,
        "bootstrap_times_ms": [15.0],
        "rekey_times_ms": [5.0],
        "mode_switches": [],
        "heavy_messages": 4,
        "balanced_messages": 0,
        "lightweight_messages": 0,
    }
    summary_a = aggregate_run(
        scenario=scenario.model_copy(update={"name": "selected-run"}),
        primary_metrics=primary,
        receiver_metrics=receiver_metrics,
        cpu_pct_avg=12.0,
        memory_mb_avg=30.0,
        cpu_time_s=1.0,
    )
    summary_b = aggregate_run(
        scenario=scenario.model_copy(update={"name": "ignored-run", "mode": BenchmarkMode.STATIC_LIGHTWEIGHT}),
        primary_metrics={**primary, "heavy_messages": 0, "lightweight_messages": 4},
        receiver_metrics=receiver_metrics,
        cpu_pct_avg=12.0,
        memory_mb_avg=30.0,
        cpu_time_s=1.0,
    )
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    write_summary(summary_a, run_a)
    write_summary(summary_b, run_b)

    summaries = collect_summaries_from_run_dirs([run_a])

    assert [summary.scenario_name for summary in summaries] == ["selected-run"]
