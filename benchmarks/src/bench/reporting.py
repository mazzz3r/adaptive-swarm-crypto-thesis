from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev

from .results import RunSummary


def _format_mode(mode: str) -> str:
    mapping = {
        "static-heavy": "Heavy",
        "static-lightweight": "Lightweight",
        "adaptive": "Adaptive",
    }
    return mapping.get(mode, mode)


def _std(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _group_by(items: list[RunSummary], fields: tuple[str, ...]) -> dict[tuple, list[RunSummary]]:
    grouped: dict[tuple, list[RunSummary]] = defaultdict(list)
    for item in items:
        grouped[tuple(getattr(item, field) for field in fields)].append(item)
    return grouped


def write_thesis_report(
    *,
    results_root: str | Path,
    comparison_dir: str | Path,
    summaries: list[RunSummary],
) -> Path:
    results_root = Path(results_root)
    comparison_dir = Path(comparison_dir)
    comparison_dir.mkdir(parents=True, exist_ok=True)
    report_path = comparison_dir / "REPORT.md"

    by_mode: dict[str, list[RunSummary]] = defaultdict(list)
    for summary in summaries:
        by_mode[summary.mode].append(summary)
    for items in by_mode.values():
        items.sort(key=lambda item: item.message_rate_hz)

    lines: list[str] = []
    lines.append("# Thesis Benchmark Report")
    lines.append("")
    if summaries:
        reference = summaries[0]
        lines.append("## Setup")
        lines.append("")
        lines.append(f"- CPU cap per peer: `{reference.cpu_limit_cores}` cores")
        lines.append(f"- Memory cap per peer: `{reference.memory_limit_mb}` MiB")
        lines.append(f"- Message size: `{reference.message_size_bytes}` bytes")
        lines.append(f"- Peer count: `{reference.peer_count}`")
        lines.append("- Traffic pattern: `peer_a -> peer_b` pairwise exchange; extra peers are not part of the measured data path.")
        lines.append("")

    lines.append("## Key Finding")
    lines.append("")
    lines.append(
        "Under constrained compute, the end-to-end throughput curves are dominated by the shared containerized transport "
        "and CPU cap. Profile differences are therefore reported separately through cryptographic work: bytes processed "
        "by encryption, decryption, and authentication primitives. Lightweight has the lowest cryptographic work per "
        "delivered message, heavy has the highest, and adaptive remains between the static extremes. The sweep should "
        "be read as offered-load probes against the same pairwise prototype, not as validated multi-peer swarm scaling."
    )
    lines.append("")

    main_items = [summary for summary in summaries if summary.matrix_group == "main-stability"]
    if not main_items:
        main_items = summaries

    lines.append("## Main Stability Sweep")
    lines.append("")
    lines.append("| Offered rate | Mode | Runs | Median P50 (ms) | Median P95 (ms) | Median P99 (ms) | Median throughput | Median drop % | Median crypto work (MiB/msg) | Median energy/msg | Throughput std |")
    lines.append("| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for (rate, mode), items in sorted(_group_by(main_items, ("message_rate_hz", "mode")).items()):
        lines.append(
            f"| {rate:.0f} | {_format_mode(mode)} | {len(items)} | "
            f"{median(item.p50_latency_ms for item in items):.3f} | "
            f"{median(item.p95_latency_ms for item in items):.3f} | "
            f"{median(item.p99_latency_ms for item in items):.3f} | "
            f"{median(item.throughput_msgs_s for item in items):.1f} | "
            f"{median(item.drop_rate_pct for item in items):.3f} | "
            f"{median(item.crypto_work_mib_per_delivered_message for item in items):.4f} | "
            f"{median(item.energy_proxy_per_delivered_message for item in items):.4f} | "
            f"{_std([item.throughput_msgs_s for item in items]):.2f} |"
        )
    lines.append("")

    lines.append("## Individual Rate Runs")
    lines.append("")
    lines.append("| Group | Offered rate | Attempted rate | Mode | Repeat | P50 latency (ms) | Throughput (msg/s) | Drop % | Crypto work (MiB/msg) | Energy / delivered message |")
    lines.append("| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for summary in sorted(summaries, key=lambda item: (item.matrix_group, item.message_rate_hz, item.mode, item.repeat_index)):
        lines.append(
            f"| {summary.matrix_group} | {summary.message_rate_hz:.0f} | {summary.attempted_rate_msgs_s:.1f} | {_format_mode(summary.mode)} | "
            f"{summary.repeat_index} | "
            f"{summary.p50_latency_ms:.3f} | {summary.throughput_msgs_s:.1f} | "
            f"{summary.drop_rate_pct:.3f} | "
            f"{summary.crypto_work_mib_per_delivered_message:.4f} | "
            f"{summary.energy_proxy_per_delivered_message:.4f} |"
        )
    lines.append("")

    lines.append("## Mode Averages")
    lines.append("")

    for group_name, fields, title in (
        ("cpu-sensitivity", ("cpu_limit_cores", "message_rate_hz", "mode"), "CPU Sensitivity"),
        ("rekey-sensitivity", ("rekey_interval_s", "message_rate_hz", "mode"), "Rekey Sensitivity"),
        ("network-impairment", ("network_label", "message_rate_hz", "mode"), "Network Impairment"),
    ):
        group_items = [summary for summary in summaries if summary.matrix_group == group_name]
        if not group_items:
            continue
        lines.append(f"## {title}")
        lines.append("")
        leading = "Parameter"
        lines.append(f"| {leading} | Offered rate | Mode | Runs | Median throughput | Median drop % | Mean throughput | Throughput std | Median crypto work (MiB/msg) | Median energy/msg |")
        lines.append("| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for key, items in sorted(_group_by(group_items, fields).items(), key=lambda pair: tuple(str(part) for part in pair[0])):
            parameter, rate, mode = key
            throughputs = [item.throughput_msgs_s for item in items]
            lines.append(
                f"| {parameter} | {rate:.0f} | {_format_mode(mode)} | {len(items)} | "
                f"{median(throughputs):.1f} | "
                f"{median(item.drop_rate_pct for item in items):.3f} | "
                f"{mean(throughputs):.1f} | "
                f"{_std(throughputs):.2f} | "
                f"{median(item.crypto_work_mib_per_delivered_message for item in items):.4f} | "
                f"{median(item.energy_proxy_per_delivered_message for item in items):.4f} |"
            )
        lines.append("")
    lines.append("| Mode | Avg P50 latency (ms) | Avg throughput (msg/s) | Avg crypto work (MiB/msg) | Avg energy / delivered message |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for mode in ("static-heavy", "adaptive", "static-lightweight"):
        items = by_mode.get(mode, [])
        if not items:
            continue
        avg_p50 = sum(item.p50_latency_ms for item in items) / len(items)
        avg_throughput = sum(item.throughput_msgs_s for item in items) / len(items)
        avg_crypto = sum(item.crypto_work_mib_per_delivered_message for item in items) / len(items)
        avg_energy = sum(item.energy_proxy_per_delivered_message for item in items) / len(items)
        lines.append(f"| {_format_mode(mode)} | {avg_p50:.3f} | {avg_throughput:.1f} | {avg_crypto:.4f} | {avg_energy:.4f} |")
    lines.append("")

    lines.append("## Selected Runs")
    lines.append("")
    lines.append("| Offered rate | Mode | Run directory |")
    lines.append("| ---: | --- | --- |")
    resolved_root = results_root.resolve()
    for summary in sorted(summaries, key=lambda item: (item.message_rate_hz, item.mode)):
        run_dir = Path(summary.source_run_dir) if summary.source_run_dir else Path()
        try:
            run_dir_display = str(run_dir.resolve().relative_to(resolved_root))
        except Exception:  # noqa: BLE001
            run_dir_display = str(run_dir) if summary.source_run_dir else "unknown"
        lines.append(f"| {summary.message_rate_hz:.0f} | {_format_mode(summary.mode)} | `{run_dir_display}` |")
    lines.append("")

    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- Comparison CSV: `{comparison_dir / 'comparison.csv'}`")
    lines.append(f"- Comparison JSON: `{comparison_dir / 'comparison.json'}`")
    lines.append(f"- Comparison plot: `{comparison_dir / 'comparison_metrics.svg'}`")
    sweep_plot = comparison_dir / "sweep_metrics.svg"
    if sweep_plot.exists():
        lines.append(f"- Sweep plot: `{sweep_plot}`")
    for artifact in ("cpu_sensitivity.svg", "rekey_sensitivity.svg", "network_impairment.svg"):
        path = comparison_dir / artifact
        if path.exists():
            lines.append(f"- {artifact}: `{path}`")
    lines.append("")
    lines.append("Each comparison row now carries `source_run_dir`, and the table above identifies the exact run directory used for each point.")
    lines.append("Per-run folders under the results root contain the individual latency histograms and adaptive switch plots.")
    lines.append(f"- Results root: `{results_root}`")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
