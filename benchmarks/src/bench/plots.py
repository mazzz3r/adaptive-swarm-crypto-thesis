from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .config import Scenario
from .policy_tradeoff import PROFILE_LABEL, PROFILE_TIER, compute_strategy_tradeoffs, policy_segments
from .results import RunSummary


def _set_readable_theme() -> None:
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.18)


def generate_plots(
    *,
    output_dir: Path,
    summary: RunSummary,
    latencies_ms: list[float],
    mode_switches: list[dict],
) -> list[Path]:
    _set_readable_theme()
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    latency_png = plots_dir / "latency_histogram.png"
    plt.figure(figsize=(8, 4.5))
    sns.histplot(latencies_ms or [0.0], bins=min(max(len(latencies_ms) // 5, 5), 40), kde=False)
    plt.title(f"Latency distribution: {summary.scenario_name}")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(latency_png, dpi=150)
    generated.append(latency_png)
    plt.close()

    summary_svg = plots_dir / "summary_metrics.svg"
    plt.figure(figsize=(9, 5))
    metric_names = ["p50", "p95", "p99", "throughput", "drop%", "energy"]
    metric_values = [
        summary.p50_latency_ms,
        summary.p95_latency_ms,
        summary.p99_latency_ms,
        summary.throughput_msgs_s,
        summary.drop_rate_pct,
        summary.energy_proxy,
    ]
    sns.barplot(x=metric_names, y=metric_values, hue=metric_names, palette="crest", legend=False)
    plt.title(f"Benchmark summary: {summary.scenario_name}\nEnergy is a modeled proxy, not a physical measurement")
    plt.tight_layout()
    plt.savefig(summary_svg)
    generated.append(summary_svg)
    plt.close()

    if mode_switches:
        switch_png = plots_dir / "adaptive_switches.png"
        profile_order = {"lightweight": 1, "balanced": 2, "heavy": 3}
        profile_labels = {1: "Lightweight", 2: "Balanced", 3: "Heavy"}
        duration_s = summary.duration_s or max(item["at_s"] for item in mode_switches) + 1.0
        x = [0.0, *[item["at_s"] for item in mode_switches], duration_s]
        y = [profile_order["balanced"], *[profile_order[item["profile"]] for item in mode_switches]]
        y.append(y[-1])
        plt.figure(figsize=(10, 4.8))
        plt.step(x, y, where="post", linewidth=2.4)
        for item in mode_switches:
            y_pos = profile_order[item["profile"]]
            plt.axvline(item["at_s"], color="0.65", linestyle="--", linewidth=0.9)
            plt.text(
                item["at_s"] + 0.35,
                y_pos + 0.04,
                f"{item['profile']}\n{item['reason']}",
                fontsize=9,
                ha="left",
                va="bottom",
            )
        plt.title("Adaptive profile over the representative 100 Hz run")
        plt.xlabel("Elapsed time (s)")
        plt.ylabel("Active profile")
        plt.yticks([1, 2, 3], [profile_labels[index] for index in [1, 2, 3]])
        plt.ylim(0.7, 3.35)
        plt.xlim(0, duration_s)
        plt.tight_layout()
        plt.savefig(switch_png, dpi=150)
        generated.append(switch_png)
        plt.close()

    return generated


def generate_comparison_plot(
    *,
    output_dir: Path,
    summaries: list[RunSummary],
) -> list[Path]:
    if not summaries:
        return []

    _set_readable_theme()
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "comparison_metrics.svg"
    data = pd.DataFrame(
        [
            {
                "scenario_name": summary.scenario_name,
                "mode": summary.mode,
                "p50_latency_ms": summary.p50_latency_ms,
                "throughput_msgs_s": summary.throughput_msgs_s,
                "energy_proxy_per_delivered_message": summary.energy_proxy_per_delivered_message,
                "modeled_crypto_cost_avg_ms": summary.modeled_crypto_cost_avg_ms,
                "crypto_work_mib_per_delivered_message": summary.crypto_work_mib_per_delivered_message,
            }
            for summary in summaries
        ]
    )

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    metrics = [
        ("p50_latency_ms", "P50 latency (ms)"),
        ("throughput_msgs_s", "Throughput (msg/s)"),
        ("crypto_work_mib_per_delivered_message", "Crypto work (MiB/msg)"),
    ]

    for axis, (column, title) in zip(axes, metrics, strict=True):
        sns.barplot(data=data, x="scenario_name", y=column, hue="mode", dodge=False, ax=axis)
        axis.set_title(title)
        axis.set_xlabel("")
        axis.tick_params(axis="x", rotation=20)
        if axis is not axes[0]:
            axis.get_legend().remove()

    axes[0].legend(title="Mode")
    fig.suptitle("Benchmark comparison\nCrypto work counts bytes processed by primitives.")
    fig.tight_layout()
    fig.savefig(plot_path)
    fig.savefig(plot_path.with_suffix(".png"), dpi=180)
    plt.close(fig)
    return [plot_path]


def generate_sweep_plot(
    *,
    output_dir: Path,
    summaries: list[RunSummary],
) -> list[Path]:
    if not summaries:
        return []

    _set_readable_theme()
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / "sweep_metrics.svg"
    data = pd.DataFrame(
        [
            {
                "mode": summary.mode,
                "message_rate_hz": summary.message_rate_hz,
                "delivery_ratio_pct": (
                    summary.throughput_msgs_s / summary.message_rate_hz * 100
                    if summary.message_rate_hz
                    else 0.0
                ),
                "drop_rate_pct": summary.drop_rate_pct,
                "p50_latency_ms": summary.p50_latency_ms,
                "throughput_msgs_s": summary.throughput_msgs_s,
                "energy_proxy_per_delivered_message": summary.energy_proxy_per_delivered_message,
                "modeled_crypto_cost_avg_ms": summary.modeled_crypto_cost_avg_ms,
                "crypto_work_mib_per_delivered_message": summary.crypto_work_mib_per_delivered_message,
            }
            for summary in summaries
        ]
    ).sort_values(["mode", "message_rate_hz"])

    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    metrics = [
        ("delivery_ratio_pct", "Delivered / offered (%)"),
        ("drop_rate_pct", "Drop rate (%)"),
        ("p50_latency_ms", "P50 latency (ms)"),
        ("crypto_work_mib_per_delivered_message", "Crypto work (MiB/msg)"),
    ]

    flat_axes = list(axes.flat)
    legend_handles = legend_labels = None
    for axis, (column, title) in zip(flat_axes, metrics, strict=True):
        sns.lineplot(
            data=data,
            x="message_rate_hz",
            y=column,
            hue="mode",
            style="mode",
            markers=True,
            dashes=False,
            ax=axis,
        )
        axis.set_title(title)
        axis.set_xlabel("Offered rate (msg/s)")
        axis.set_ylabel(title)
        legend = axis.get_legend()
        if legend is not None:
            if legend_handles is None:
                legend_handles, legend_labels = axis.get_legend_handles_labels()
            legend.remove()

    if legend_handles is not None:
        fig.legend(legend_handles, legend_labels, title="Mode", loc="upper center", ncols=4, bbox_to_anchor=(0.5, 0.91))
    fig.suptitle("Sweep comparison\nCrypto work counts bytes processed by primitives.")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(plot_path)
    fig.savefig(plot_path.with_suffix(".png"), dpi=180)
    plt.close(fig)
    return [plot_path]


def generate_sensitivity_plot(
    *,
    output_dir: Path,
    summaries: list[RunSummary],
    matrix_group: str,
    x_field: str,
    x_label: str,
    filename: str,
) -> list[Path]:
    selected = [summary for summary in summaries if summary.matrix_group == matrix_group]
    if not selected:
        return []
    rates = {summary.message_rate_hz for summary in selected}
    if len(rates) > 1:
        stressed_rate = max(rates)
        selected = [summary for summary in selected if summary.message_rate_hz == stressed_rate]

    _set_readable_theme()
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / filename
    data = pd.DataFrame(
        [
            {
                "mode": summary.mode,
                x_label: (
                    f"{summary.network_label}\n"
                    f"{summary.network_delay_ms:g}/{summary.network_jitter_ms:g}/{summary.network_loss_pct:g}"
                    if matrix_group == "network-impairment"
                    else getattr(summary, x_field)
                ),
                "throughput_msgs_s": summary.throughput_msgs_s,
                "drop_rate_pct": summary.drop_rate_pct,
                "energy_proxy_per_delivered_message": summary.energy_proxy_per_delivered_message,
                "modeled_crypto_cost_avg_ms": summary.modeled_crypto_cost_avg_ms,
                "crypto_work_mib_per_delivered_message": summary.crypto_work_mib_per_delivered_message,
            }
            for summary in selected
        ]
    )

    fig, axes = plt.subplots(3, 1, figsize=(9.8, 10.8))
    metrics = [
        ("throughput_msgs_s", "Throughput (msg/s)"),
        ("drop_rate_pct", "Drop rate (%)"),
        ("crypto_work_mib_per_delivered_message", "Crypto work (MiB/msg)"),
    ]

    legend_handles = legend_labels = None
    for axis, (column, title) in zip(axes, metrics, strict=True):
        sns.barplot(
            data=data,
            x=x_label,
            y=column,
            hue="mode",
            errorbar=None,
            ax=axis,
        )
        axis.set_title(title)
        axis.set_xlabel(x_label)
        axis.set_ylabel(title)
        legend = axis.get_legend()
        if legend is not None:
            if legend_handles is None:
                legend_handles, legend_labels = axis.get_legend_handles_labels()
            legend.remove()
        axis.tick_params(axis="x", rotation=0)

    if legend_handles is not None:
        fig.legend(legend_handles, legend_labels, title="Mode", loc="upper center", ncols=4, bbox_to_anchor=(0.5, 0.94))
    fig.suptitle(
        f"{matrix_group.replace('-', ' ').title()}\nCrypto work counts bytes processed by primitives."
    )
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(plot_path)
    fig.savefig(plot_path.with_suffix(".png"), dpi=180)
    plt.close(fig)
    return [plot_path]


def generate_policy_tradeoff_plot(
    *,
    output_dir: Path,
    scenario: Scenario,
    filename: str = "policy_tradeoff.png",
) -> Path:
    _set_readable_theme()
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / filename

    segments = policy_segments(scenario)
    tradeoffs = compute_strategy_tradeoffs(scenario)
    profile_colors = {
        "Lightweight": "#5ab4ac",
        "Balanced": "#fdb863",
        "Heavy": "#d95f02",
    }
    outcome_colors = {
        "Matched": "#2ca25f",
        "Overprotected": "#756bb1",
        "Underprotected": "#de2d26",
    }

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(11, 9),
        gridspec_kw={"height_ratios": [1.0, 1.45, 1.2]},
    )

    timeline_axis = axes[0]
    for segment in segments:
        label = PROFILE_LABEL[segment.required_profile]
        timeline_axis.axvspan(
            segment.start_s,
            segment.end_s,
            color=profile_colors[label],
            alpha=0.38,
        )
        timeline_axis.text(
            (segment.start_s + segment.end_s) / 2,
            PROFILE_TIER[segment.required_profile],
            label,
            ha="center",
            va="center",
            fontsize=9,
        )
    timeline_axis.set_xlim(0, scenario.duration_s)
    timeline_axis.set_ylim(0.5, 3.5)
    timeline_axis.set_yticks([1, 2, 3], ["Lightweight", "Balanced", "Heavy"])
    timeline_axis.set_title("Adaptive policy requirement over the 60-second long run")
    timeline_axis.set_xlabel("")
    timeline_axis.set_ylabel("Required profile")

    work_axis = axes[1]
    for tradeoff in tradeoffs:
        x_values = [point[0] for point in tradeoff.cumulative_points]
        y_values = [point[1] / 1000 for point in tradeoff.cumulative_points]
        work_axis.plot(x_values, y_values, label=tradeoff.label, linewidth=2)
    work_axis.set_xlim(0, scenario.duration_s)
    work_axis.set_title("Cumulative protection-tier work")
    work_axis.set_ylabel("Tier-message units (thousands)")
    work_axis.legend(ncols=2, fontsize=8)

    outcome_axis = axes[2]
    labels = [tradeoff.label for tradeoff in tradeoffs]
    matched = [tradeoff.matched_share_pct for tradeoff in tradeoffs]
    overprotected = [tradeoff.overprotected_share_pct for tradeoff in tradeoffs]
    underprotected = [tradeoff.underprotected_share_pct for tradeoff in tradeoffs]
    outcome_axis.barh(labels, matched, color=outcome_colors["Matched"], label="Matched")
    outcome_axis.barh(labels, overprotected, left=matched, color=outcome_colors["Overprotected"], label="Overprotected")
    left = [match + over for match, over in zip(matched, overprotected, strict=True)]
    outcome_axis.barh(
        labels,
        underprotected,
        left=left,
        color=outcome_colors["Underprotected"],
        label="Underprotected",
    )
    outcome_axis.set_xlim(0, 100)
    outcome_axis.set_xlabel("Message-time share (%)")
    outcome_axis.set_title("Policy fit against the same threat and energy schedule")
    outcome_axis.legend(ncols=3, fontsize=8, loc="lower right")

    fig.suptitle(
        "Long-run adaptive trade-off: cost is reduced by switching, not by hiding transport latency",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(plot_path, dpi=180)
    plt.close(fig)
    return plot_path
