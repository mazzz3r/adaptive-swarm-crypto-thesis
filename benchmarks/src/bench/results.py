from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from .config import Scenario
from .crypto_work import CRYPTO_WORK_LABEL, compute_crypto_work
from .energy import (
    CRYPTO_COST_PROXY_LABEL,
    ENERGY_PROXY_LABEL,
    compute_energy_proxy,
    compute_modeled_crypto_cost_ms,
)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 3)
    index = (len(ordered) - 1) * pct
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return round(ordered[int(index)], 3)
    weight = index - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 3)


@dataclass(frozen=True)
class RunSummary:
    scenario_name: str
    source_run_dir: str
    mode: str
    cpu_limit_cores: float | None
    memory_limit_mb: int | None
    message_size_bytes: int
    message_rate_hz: float
    attempted_rate_msgs_s: float
    peer_count: int
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_msgs_s: float
    drop_rate_pct: float
    error_rate_pct: float
    bootstrap_time_ms: float
    rekey_time_ms: float
    bytes_sent: int
    crypto_overhead_bytes: int
    cpu_pct_avg: float
    memory_mb_avg: float
    energy_proxy: float
    energy_label: str
    energy_proxy_per_delivered_message: float
    energy_per_message_label: str
    modeled_crypto_cost_total_ms: float
    modeled_crypto_cost_avg_ms: float
    modeled_crypto_cost_label: str
    mode_switches: int
    messages_sent: int
    messages_attempted: int
    messages_received: int
    rekey_count: int
    container_cpu_time_s: float = 0.0
    container_cpu_ms_per_delivered_message: float = 0.0
    heavy_messages: int = 0
    balanced_messages: int = 0
    lightweight_messages: int = 0
    crypto_work_bytes: int = 0
    crypto_work_mib_per_delivered_message: float = 0.0
    crypto_primitive_calls: int = 0
    crypto_work_label: str = CRYPTO_WORK_LABEL
    duration_s: float = 0.0
    repeat_index: int = 1
    matrix_group: str = "default"
    network_label: str = "clean"
    network_delay_ms: float = 0.0
    network_jitter_ms: float = 0.0
    network_loss_pct: float = 0.0
    rekey_interval_s: float = 0.0


def aggregate_run(
    *,
    scenario: Scenario,
    primary_metrics: dict,
    receiver_metrics: dict,
    cpu_pct_avg: float,
    memory_mb_avg: float,
    cpu_time_s: float,
) -> RunSummary:
    latencies = primary_metrics["latencies_ms"]
    attempted = primary_metrics["messages_attempted"]
    sent = primary_metrics["messages_sent"]
    duration = max(scenario.duration_s, 1e-6)
    throughput = round(sent / duration, 3)
    attempted_rate = round(attempted / duration, 3)
    drops = max(attempted - sent, 0)
    errors = primary_metrics["send_errors"]
    bootstrap_times = primary_metrics["bootstrap_times_ms"] or receiver_metrics["bootstrap_times_ms"]
    rekey_times = primary_metrics["rekey_times_ms"]
    energy_proxy = compute_energy_proxy(
        cpu_time_s=cpu_time_s,
        bytes_sent=primary_metrics["bytes_ciphertext"],
        rekey_count=primary_metrics["rekey_count"],
        heavy_messages=primary_metrics["heavy_messages"],
        balanced_messages=primary_metrics["balanced_messages"],
        lightweight_messages=primary_metrics["lightweight_messages"],
    )
    modeled_crypto_cost_total_ms, modeled_crypto_cost_avg_ms = compute_modeled_crypto_cost_ms(
        rekey_count=primary_metrics["rekey_count"],
        heavy_messages=primary_metrics["heavy_messages"],
        balanced_messages=primary_metrics["balanced_messages"],
        lightweight_messages=primary_metrics["lightweight_messages"],
    )
    delivered_messages = max(receiver_metrics["messages_received"], 1)
    crypto_work = compute_crypto_work(
        message_size_bytes=scenario.message_size_bytes,
        delivered_messages=delivered_messages,
        heavy_messages=primary_metrics["heavy_messages"],
        balanced_messages=primary_metrics["balanced_messages"],
        lightweight_messages=primary_metrics["lightweight_messages"],
    )
    return RunSummary(
        scenario_name=scenario.name,
        source_run_dir="",
        mode=scenario.mode.value,
        cpu_limit_cores=scenario.resources.cpu_limit_cores,
        memory_limit_mb=scenario.resources.memory_limit_mb,
        message_size_bytes=scenario.message_size_bytes,
        message_rate_hz=scenario.message_rate_hz,
        attempted_rate_msgs_s=attempted_rate,
        peer_count=scenario.peer_count,
        p50_latency_ms=percentile(latencies, 0.50),
        p95_latency_ms=percentile(latencies, 0.95),
        p99_latency_ms=percentile(latencies, 0.99),
        throughput_msgs_s=throughput,
        drop_rate_pct=round((drops / attempted) * 100, 3) if attempted else 0.0,
        error_rate_pct=round((errors / attempted) * 100, 3) if attempted else 0.0,
        bootstrap_time_ms=round(mean(bootstrap_times), 3) if bootstrap_times else 0.0,
        rekey_time_ms=round(mean(rekey_times), 3) if rekey_times else 0.0,
        bytes_sent=primary_metrics["bytes_ciphertext"],
        crypto_overhead_bytes=primary_metrics["bytes_overhead"],
        cpu_pct_avg=round(cpu_pct_avg, 3),
        memory_mb_avg=round(memory_mb_avg, 3),
        energy_proxy=energy_proxy,
        energy_label=ENERGY_PROXY_LABEL,
        energy_proxy_per_delivered_message=round(energy_proxy / delivered_messages, 4),
        energy_per_message_label="Model-based energy proxy normalized by delivered messages.",
        modeled_crypto_cost_total_ms=modeled_crypto_cost_total_ms,
        modeled_crypto_cost_avg_ms=modeled_crypto_cost_avg_ms,
        modeled_crypto_cost_label=CRYPTO_COST_PROXY_LABEL,
        mode_switches=len(primary_metrics["mode_switches"]),
        messages_sent=sent,
        messages_attempted=attempted,
        messages_received=receiver_metrics["messages_received"],
        rekey_count=primary_metrics["rekey_count"],
        container_cpu_time_s=round(cpu_time_s, 6),
        container_cpu_ms_per_delivered_message=round((cpu_time_s * 1000) / delivered_messages, 4),
        heavy_messages=primary_metrics["heavy_messages"],
        balanced_messages=primary_metrics["balanced_messages"],
        lightweight_messages=primary_metrics["lightweight_messages"],
        crypto_work_bytes=crypto_work.crypto_work_bytes,
        crypto_work_mib_per_delivered_message=crypto_work.crypto_work_mib_per_delivered_message,
        crypto_primitive_calls=crypto_work.crypto_primitive_calls,
        crypto_work_label=CRYPTO_WORK_LABEL,
        duration_s=scenario.duration_s,
        repeat_index=1,
        matrix_group="default",
        network_label="custom",
        network_delay_ms=scenario.network.delay_ms,
        network_jitter_ms=scenario.network.jitter_ms,
        network_loss_pct=scenario.network.loss_pct,
        rekey_interval_s=scenario.rekey_interval_s,
    )


def write_summary(summary: RunSummary, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "summary.csv"
    json_path = output_dir / "summary.json"
    payload = asdict(summary)
    payload["source_run_dir"] = str(output_dir.resolve())

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(payload.keys()))
        writer.writeheader()
        writer.writerow(payload)

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return csv_path, json_path


def load_summary(path: str | Path) -> RunSummary:
    summary_path = Path(path)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if "source_run_dir" not in payload:
        payload["source_run_dir"] = str(summary_path.parent.resolve())
    if "attempted_rate_msgs_s" not in payload:
        throughput = payload.get("throughput_msgs_s", 0) or 0
        sent = payload.get("messages_sent", 0)
        duration_s = (sent / throughput) if throughput and sent else 10.0
        attempted = payload.get("messages_attempted", payload.get("messages_sent", 0))
        payload["attempted_rate_msgs_s"] = round(attempted / duration_s, 3)
    if "energy_proxy_per_delivered_message" not in payload:
        delivered_messages = max(payload.get("messages_received", 0), 1)
        payload["energy_proxy_per_delivered_message"] = round(payload["energy_proxy"] / delivered_messages, 4)
    if "energy_per_message_label" not in payload:
        payload["energy_per_message_label"] = "Model-based energy proxy normalized by delivered messages."
    payload.setdefault("duration_s", 0.0)
    payload.setdefault("repeat_index", 1)
    payload.setdefault("matrix_group", "default")
    payload.setdefault("network_label", "clean")
    payload.setdefault("network_delay_ms", 0.0)
    payload.setdefault("network_jitter_ms", 0.0)
    payload.setdefault("network_loss_pct", 0.0)
    payload.setdefault("rekey_interval_s", 0.0)
    payload.setdefault("container_cpu_time_s", 0.0)
    payload.setdefault("container_cpu_ms_per_delivered_message", 0.0)
    if any(
        key not in payload
        for key in (
            "heavy_messages",
            "balanced_messages",
            "lightweight_messages",
            "crypto_work_bytes",
            "crypto_work_mib_per_delivered_message",
            "crypto_primitive_calls",
            "crypto_work_label",
        )
    ):
        raw_metrics_path = summary_path.parent / "raw_metrics.json"
        raw_primary = {}
        if raw_metrics_path.exists():
            try:
                raw_payload = json.loads(raw_metrics_path.read_text(encoding="utf-8"))
                raw_primary = raw_payload.get("peer_a", {})
            except json.JSONDecodeError:
                raw_primary = {}
        payload.setdefault("heavy_messages", raw_primary.get("heavy_messages", 0))
        payload.setdefault("balanced_messages", raw_primary.get("balanced_messages", 0))
        payload.setdefault("lightweight_messages", raw_primary.get("lightweight_messages", 0))
        if not any(
            payload.get(key, 0)
            for key in ("heavy_messages", "balanced_messages", "lightweight_messages")
        ):
            sent = payload.get("messages_sent", 0)
            if payload.get("mode") == "static-heavy":
                payload["heavy_messages"] = sent
            elif payload.get("mode") == "static-lightweight":
                payload["lightweight_messages"] = sent
        crypto_work = compute_crypto_work(
            message_size_bytes=payload.get("message_size_bytes", 0),
            delivered_messages=max(payload.get("messages_received", 0), 1),
            heavy_messages=payload.get("heavy_messages", 0),
            balanced_messages=payload.get("balanced_messages", 0),
            lightweight_messages=payload.get("lightweight_messages", 0),
        )
        payload.setdefault("crypto_work_bytes", crypto_work.crypto_work_bytes)
        payload.setdefault(
            "crypto_work_mib_per_delivered_message",
            crypto_work.crypto_work_mib_per_delivered_message,
        )
        payload.setdefault("crypto_primitive_calls", crypto_work.crypto_primitive_calls)
        payload.setdefault("crypto_work_label", CRYPTO_WORK_LABEL)
    return RunSummary(**payload)


def collect_summaries(results_root: str | Path) -> list[RunSummary]:
    root = Path(results_root)
    summaries: list[RunSummary] = []
    for summary_path in sorted(root.glob("*/summary.json")):
        summaries.append(load_summary(summary_path))
    return summaries


def collect_summaries_from_run_dirs(run_dirs: list[str | Path]) -> list[RunSummary]:
    summaries: list[RunSummary] = []
    for run_dir in sorted(Path(path) for path in run_dirs):
        summary_path = run_dir / "summary.json"
        if not summary_path.exists():
            continue
        summaries.append(load_summary(summary_path))
    return summaries


def write_comparison(summaries: list[RunSummary], output_dir: str | Path) -> tuple[Path, Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "comparison.csv"
    json_path = target_dir / "comparison.json"
    rows = [asdict(summary) for summary in summaries]

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return csv_path, json_path
