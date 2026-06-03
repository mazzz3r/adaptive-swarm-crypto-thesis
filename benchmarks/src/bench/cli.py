from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from pathlib import Path

from .config import BenchmarkMode, NetworkConfig, load_scenario
from .orchestrator import run_benchmark, run_benchmark_for_scenario
from .plots import (
    generate_comparison_plot,
    generate_policy_tradeoff_plot,
    generate_sensitivity_plot,
    generate_sweep_plot,
)
from .results import collect_summaries, collect_summaries_from_run_dirs, write_comparison
from .reporting import write_thesis_report


def parse_rates(value: str) -> list[float]:
    rates = [float(item.strip()) for item in value.split(",") if item.strip()]
    if not rates:
        raise argparse.ArgumentTypeError("at least one rate is required")
    if any(rate <= 0 for rate in rates):
        raise argparse.ArgumentTypeError("rates must be positive")
    return rates


def parse_float_list(value: str) -> list[float]:
    values = [float(item.strip()) for item in value.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one value is required")
    if any(item <= 0 for item in values):
        raise argparse.ArgumentTypeError("values must be positive")
    return values


@dataclass(frozen=True)
class NetworkProfileSpec:
    label: str
    delay_ms: float
    jitter_ms: float
    loss_pct: float


def parse_network_profiles(value: str) -> list[NetworkProfileSpec]:
    profiles: list[NetworkProfileSpec] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise argparse.ArgumentTypeError("network profiles must use label=delay/jitter/loss")
        label, raw_values = item.split("=", 1)
        parts = [float(part.strip().rstrip("%")) for part in raw_values.split("/")]
        if len(parts) != 3:
            raise argparse.ArgumentTypeError("network profiles must use label=delay/jitter/loss")
        delay_ms, jitter_ms, loss_pct = parts
        if delay_ms < 0 or jitter_ms < 0 or not (0 <= loss_pct <= 100):
            raise argparse.ArgumentTypeError("invalid network profile values")
        profiles.append(NetworkProfileSpec(label=label.strip(), delay_ms=delay_ms, jitter_ms=jitter_ms, loss_pct=loss_pct))
    if not profiles:
        raise argparse.ArgumentTypeError("at least one network profile is required")
    return profiles


def parse_modes(value: str) -> list[BenchmarkMode]:
    modes = [BenchmarkMode(item.strip()) for item in value.split(",") if item.strip()]
    if not modes:
        raise argparse.ArgumentTypeError("at least one mode is required")
    return modes


def run_sweep_matrix(
    *,
    scenario_path: str | Path,
    rates: list[float],
    modes: list[BenchmarkMode],
    output_dir: str | Path,
    cpu_limit_cores: float | None,
    memory_limit_mb: int | None,
    duration_s: float | None = None,
    rekey_interval_s: float | None = None,
    repeats: int = 1,
    matrix_group: str = "sweep",
    network_profiles: list[NetworkProfileSpec] | None = None,
    build_images: bool = True,
    resume_existing: bool = False,
) -> tuple[Path, Path, list]:
    base_scenario = load_scenario(scenario_path)
    output_root = Path(output_dir)
    run_dirs: list[Path] = []
    profiles = network_profiles or [NetworkProfileSpec(label="clean", delay_ms=0, jitter_ms=0, loss_pct=0)]
    for rate in rates:
        for mode in modes:
            for profile in profiles:
                for repeat_index in range(1, repeats + 1):
                    scenario = base_scenario.model_copy(deep=True)
                    scenario.mode = mode
                    scenario.message_rate_hz = rate
                    if duration_s is not None:
                        scenario.duration_s = duration_s
                    if rekey_interval_s is not None:
                        scenario.rekey_interval_s = rekey_interval_s
                    scenario.network = NetworkConfig(
                        delay_ms=profile.delay_ms,
                        jitter_ms=profile.jitter_ms,
                        loss_pct=profile.loss_pct,
                    )
                    cpu_label = str(cpu_limit_cores).replace(".", "p") if cpu_limit_cores is not None else "default"
                    rekey_label = str(scenario.rekey_interval_s).replace(".", "p")
                    scenario.name = (
                        f"{base_scenario.name}-{matrix_group}-{mode.value}-{int(rate)}hz-"
                        f"cpu{cpu_label}-rekey{rekey_label}-{profile.label}-r{repeat_index}"
                    )
                    if resume_existing:
                        existing_dirs = sorted(output_root.glob(f"*-{scenario.name}"))
                        completed_dirs = [path for path in existing_dirs if (path / "summary.json").exists()]
                        if completed_dirs:
                            run_dirs.append(completed_dirs[-1])
                            continue
                    run_dir = asyncio.run(
                        run_benchmark_for_scenario(
                            scenario=scenario,
                            output_root=output_root,
                            cpu_limit_cores=cpu_limit_cores,
                            memory_limit_mb=memory_limit_mb,
                            matrix_group=matrix_group,
                            repeat_index=repeat_index,
                            network_label=profile.label,
                            output_name=scenario.name,
                            build_images=build_images,
                        )
                    )
                    run_dirs.append(run_dir)
    summaries = collect_summaries_from_run_dirs(run_dirs)
    comparison_dir = output_root / "comparison"
    write_comparison(summaries, comparison_dir)
    generate_sweep_plot(output_dir=comparison_dir, summaries=summaries)
    return output_root, comparison_dir, summaries


def run_final_thesis_matrix(
    *,
    scenario_path: str | Path,
    rates: list[float],
    output_dir: str | Path,
    duration_s: float,
    repeats: int,
    cpu_limits: list[float],
    rekey_intervals: list[float],
    network_profiles: list[NetworkProfileSpec],
    memory_limit_mb: int,
    build_images: bool = True,
    resume_existing: bool = False,
) -> tuple[Path, Path, list]:
    output_root = Path(output_dir)
    all_summaries = []
    modes = [
        BenchmarkMode.STATIC_HEAVY,
        BenchmarkMode.STATIC_BALANCED,
        BenchmarkMode.STATIC_LIGHTWEIGHT,
        BenchmarkMode.ADAPTIVE,
    ]

    _, _, summaries = run_sweep_matrix(
        scenario_path=scenario_path,
        rates=rates,
        modes=modes,
        output_dir=output_root,
        cpu_limit_cores=0.05,
        memory_limit_mb=memory_limit_mb,
        duration_s=duration_s,
        rekey_interval_s=2.0,
        repeats=repeats,
        matrix_group="main-stability",
        network_profiles=[NetworkProfileSpec(label="clean", delay_ms=0, jitter_ms=0, loss_pct=0)],
        build_images=build_images,
        resume_existing=resume_existing,
    )
    all_summaries.extend(summaries)

    for cpu_limit in cpu_limits:
        _, _, summaries = run_sweep_matrix(
            scenario_path=scenario_path,
            rates=[100.0, 200.0],
            modes=modes,
            output_dir=output_root,
            cpu_limit_cores=cpu_limit,
            memory_limit_mb=memory_limit_mb,
            duration_s=duration_s,
            rekey_interval_s=2.0,
            repeats=repeats,
            matrix_group="cpu-sensitivity",
            network_profiles=[NetworkProfileSpec(label="clean", delay_ms=0, jitter_ms=0, loss_pct=0)],
            build_images=build_images,
            resume_existing=resume_existing,
        )
        all_summaries.extend(summaries)

    for rekey_interval in rekey_intervals:
        _, _, summaries = run_sweep_matrix(
            scenario_path=scenario_path,
            rates=[100.0],
            modes=modes,
            output_dir=output_root,
            cpu_limit_cores=0.05,
            memory_limit_mb=memory_limit_mb,
            duration_s=duration_s,
            rekey_interval_s=rekey_interval,
            repeats=repeats,
            matrix_group="rekey-sensitivity",
            network_profiles=[NetworkProfileSpec(label="clean", delay_ms=0, jitter_ms=0, loss_pct=0)],
            build_images=build_images,
            resume_existing=resume_existing,
        )
        all_summaries.extend(summaries)

    _, _, summaries = run_sweep_matrix(
        scenario_path=scenario_path,
        rates=[100.0],
        modes=modes,
        output_dir=output_root,
        cpu_limit_cores=0.05,
        memory_limit_mb=memory_limit_mb,
        duration_s=duration_s,
        rekey_interval_s=2.0,
        repeats=repeats,
        matrix_group="network-impairment",
        network_profiles=network_profiles,
        build_images=build_images,
        resume_existing=resume_existing,
    )
    all_summaries.extend(summaries)

    comparison_dir = output_root / "comparison"
    write_comparison(all_summaries, comparison_dir)
    generate_comparison_plot(output_dir=comparison_dir, summaries=all_summaries)
    generate_sweep_plot(output_dir=comparison_dir, summaries=[item for item in all_summaries if item.matrix_group == "main-stability"])
    generate_sensitivity_plot(
        output_dir=comparison_dir,
        summaries=all_summaries,
        matrix_group="cpu-sensitivity",
        x_field="cpu_limit_cores",
        x_label="CPU cap (cores)",
        filename="cpu_sensitivity.svg",
    )
    generate_sensitivity_plot(
        output_dir=comparison_dir,
        summaries=all_summaries,
        matrix_group="rekey-sensitivity",
        x_field="rekey_interval_s",
        x_label="Rekey interval (s)",
        filename="rekey_sensitivity.svg",
    )
    generate_sensitivity_plot(
        output_dir=comparison_dir,
        summaries=all_summaries,
        matrix_group="network-impairment",
        x_field="network_label",
        x_label="Network profile (delay/jitter/loss)",
        filename="network_impairment.svg",
    )
    return output_root, comparison_dir, all_summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark containerized adaptive crypto peers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a benchmark scenario.")
    run_parser.add_argument("--scenario", required=True, help="Path to the YAML scenario file.")
    run_parser.add_argument("--output-dir", default="results", help="Directory for benchmark outputs.")
    run_parser.add_argument("--cpu-limit-cores", type=float, help="Optional per-peer CPU cap in cores.")
    run_parser.add_argument("--memory-limit-mb", type=int, help="Optional per-peer memory cap in MiB.")
    run_parser.add_argument("--keep-up", action="store_true", help="Keep the compose stack running after completion.")

    compare_parser = subparsers.add_parser("compare", help="Generate comparison artifacts from existing run outputs.")
    compare_parser.add_argument("--results-root", required=True, help="Directory containing run subdirectories with summary.json files.")
    compare_parser.add_argument("--output-dir", help="Directory for comparison CSV/JSON/plots. Defaults to <results-root>/comparison.")

    policy_parser = subparsers.add_parser("policy-tradeoff", help="Generate the long-run policy trade-off figure.")
    policy_parser.add_argument("--scenario", default="scenarios/saturation-adaptive-long.yaml", help="Base scenario YAML file.")
    policy_parser.add_argument("--output-dir", default="comparison", help="Directory for the generated figure.")
    policy_parser.add_argument("--filename", default="policy_tradeoff.png", help="Output PNG filename.")

    sweep_parser = subparsers.add_parser("sweep", help="Run a rate sweep and generate comparison artifacts.")
    sweep_parser.add_argument("--scenario", required=True, help="Base scenario YAML file.")
    sweep_parser.add_argument("--rates", required=True, type=parse_rates, help="Comma-separated offered message rates in Hz.")
    sweep_parser.add_argument(
        "--modes",
        type=parse_modes,
        default=[
            BenchmarkMode.STATIC_HEAVY,
            BenchmarkMode.STATIC_BALANCED,
            BenchmarkMode.STATIC_LIGHTWEIGHT,
            BenchmarkMode.ADAPTIVE,
        ],
        help="Comma-separated modes. Defaults to static-heavy,static-balanced,static-lightweight,adaptive.",
    )
    sweep_parser.add_argument("--output-dir", default="sweep-results", help="Directory for sweep outputs.")
    sweep_parser.add_argument("--cpu-limit-cores", type=float, help="Optional per-peer CPU cap in cores.")
    sweep_parser.add_argument("--memory-limit-mb", type=int, help="Optional per-peer memory cap in MiB.")
    sweep_parser.add_argument("--no-build", action="store_true", help="Reuse existing Docker images instead of rebuilding for every run.")
    sweep_parser.add_argument("--resume", action="store_true", help="Skip matrix cells that already have a summary.json in the output directory.")

    thesis_parser = subparsers.add_parser("thesis-report", help="Run the default thesis matrix and generate a ready report.")
    thesis_parser.add_argument("--scenario", default="scenarios/saturation-adaptive-long.yaml", help="Base scenario YAML file.")
    thesis_parser.add_argument("--rates", type=parse_rates, default=[25.0, 50.0, 75.0, 100.0, 150.0, 200.0, 300.0], help="Comma-separated offered message rates in Hz.")
    thesis_parser.add_argument("--output-dir", default="thesis-report", help="Directory for thesis report outputs.")
    thesis_parser.add_argument("--duration-s", type=float, default=60.0, help="Duration for each run in seconds.")
    thesis_parser.add_argument("--repeats", type=int, default=3, help="Number of repeats per matrix cell.")
    thesis_parser.add_argument("--cpu-limits", type=parse_float_list, default=[0.05, 0.10, 0.25], help="Comma-separated CPU caps for the sensitivity matrix.")
    thesis_parser.add_argument("--rekey-intervals", type=parse_float_list, default=[2.0, 5.0, 10.0], help="Comma-separated rekey intervals for the sensitivity matrix.")
    thesis_parser.add_argument(
        "--network-profiles",
        type=parse_network_profiles,
        default=[
            NetworkProfileSpec(label="clean", delay_ms=0, jitter_ms=0, loss_pct=0),
            NetworkProfileSpec(label="mild", delay_ms=20, jitter_ms=5, loss_pct=2),
            NetworkProfileSpec(label="lossy", delay_ms=50, jitter_ms=15, loss_pct=5),
        ],
        help="Comma-separated network profiles as label=delay_ms/jitter_ms/loss_pct.",
    )
    thesis_parser.add_argument("--memory-limit-mb", type=int, default=128, help="Per-peer memory cap in MiB.")
    thesis_parser.add_argument("--no-build", action="store_true", help="Reuse existing Docker images instead of rebuilding for every run.")
    thesis_parser.add_argument("--resume", action="store_true", help="Skip matrix cells that already have a summary.json in the output directory.")

    args = parser.parse_args()
    if args.command == "run":
        output_dir = asyncio.run(
            run_benchmark(
                scenario_path=args.scenario,
                output_root=args.output_dir,
                cpu_limit_cores=args.cpu_limit_cores,
                memory_limit_mb=args.memory_limit_mb,
                keep_up=args.keep_up,
            )
        )
        print(output_dir)
    elif args.command == "compare":
        summaries = collect_summaries(args.results_root)
        if not summaries:
            raise SystemExit(f"no summary.json files found under {args.results_root}")
        output_dir = Path(args.output_dir) if args.output_dir else Path(args.results_root) / "comparison"
        write_comparison(summaries, output_dir)
        generate_comparison_plot(output_dir=output_dir, summaries=summaries)
        if len({summary.message_rate_hz for summary in summaries}) > 1:
            generate_sweep_plot(output_dir=output_dir, summaries=summaries)
        print(output_dir)
    elif args.command == "policy-tradeoff":
        scenario = load_scenario(args.scenario)
        plot_path = generate_policy_tradeoff_plot(
            output_dir=Path(args.output_dir),
            scenario=scenario,
            filename=args.filename,
        )
        print(plot_path)
    elif args.command == "sweep":
        _, comparison_dir, _ = run_sweep_matrix(
            scenario_path=args.scenario,
            rates=args.rates,
            modes=args.modes,
            output_dir=args.output_dir,
            cpu_limit_cores=args.cpu_limit_cores,
            memory_limit_mb=args.memory_limit_mb,
            build_images=not args.no_build,
            resume_existing=args.resume,
        )
        print(comparison_dir)
    elif args.command == "thesis-report":
        output_root, comparison_dir, summaries = run_final_thesis_matrix(
            scenario_path=args.scenario,
            rates=args.rates,
            output_dir=args.output_dir,
            duration_s=args.duration_s,
            repeats=args.repeats,
            cpu_limits=args.cpu_limits,
            rekey_intervals=args.rekey_intervals,
            network_profiles=args.network_profiles,
            memory_limit_mb=args.memory_limit_mb,
            build_images=not args.no_build,
            resume_existing=args.resume,
        )
        report_path = write_thesis_report(
            results_root=output_root,
            comparison_dir=comparison_dir,
            summaries=summaries,
        )
        print(report_path)


if __name__ == "__main__":
    main()
