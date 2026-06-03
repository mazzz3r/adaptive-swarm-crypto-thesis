from __future__ import annotations

import asyncio
import contextlib
import json
import re
import subprocess
import time
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

import docker
import grpc

from .config import ResourceLimits, Scenario, load_scenario
from .plots import generate_plots
from .proto import crypto_peer_pb2 as pb2
from .proto import crypto_peer_pb2_grpc as pb2_grpc
from .proto_helpers import metrics_response_to_dict, scenario_to_proto
from .results import aggregate_run, write_summary


PRIMARY_PORTS = {"peer_a": 50051, "peer_b": 50052}


@dataclass(frozen=True)
class StatsSample:
    service: str
    cpu_pct: float
    memory_mb: float
    cpu_total_ns: int


class ComposeHarness:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.compose_file = repo_root / "docker-compose.yml"
        self.project_name = "diploma_bench"

    def _compose(self, *args: str) -> None:
        command = [
            "docker",
            "compose",
            "-p",
            self.project_name,
            "-f",
            str(self.compose_file),
            *args,
        ]
        subprocess.run(command, cwd=self.repo_root, check=True)

    def cleanup(self) -> None:
        client = docker.from_env()
        try:
            containers = client.containers.list(
                all=True,
                filters={"label": f"com.docker.compose.project={self.project_name}"},
            )
            for container in containers:
                with contextlib.suppress(Exception):
                    container.remove(force=True)
            networks = client.networks.list(filters={"label": f"com.docker.compose.project={self.project_name}"})
            for network in networks:
                with contextlib.suppress(Exception):
                    network.remove()
        finally:
            client.close()

    def up(self, *, extra_peer_count: int, build: bool = True) -> None:
        with contextlib.suppress(subprocess.CalledProcessError):
            self._compose("down", "--remove-orphans")
        self.cleanup()
        args = ["up", "-d", "--force-recreate", "--remove-orphans"]
        if build:
            args.append("--build")
        if extra_peer_count > 0:
            args += ["--scale", f"peer_extra={extra_peer_count}"]
        services = ["peer_a", "peer_b", "runner"]
        if extra_peer_count > 0:
            services.append("peer_extra")
        self._compose(*args, *services)

    def down(self) -> None:
        with contextlib.suppress(subprocess.CalledProcessError):
            self._compose("down", "--remove-orphans")
        self.cleanup()

    def find_container(self, client: docker.DockerClient, service: str):
        containers = client.containers.list(
            all=True,
            filters={
                "label": [
                    f"com.docker.compose.project={self.project_name}",
                    f"com.docker.compose.service={service}",
                ]
            },
        )
        if not containers:
            raise RuntimeError(f"container for service {service} not found")
        return containers[0]

    def list_containers(self, client: docker.DockerClient, service: str) -> list:
        return client.containers.list(
            all=True,
            filters={
                "label": [
                    f"com.docker.compose.project={self.project_name}",
                    f"com.docker.compose.service={service}",
                ]
            },
        )


def _netem_command(delay_ms: float, jitter_ms: float, loss_pct: float) -> str:
    if delay_ms == 0 and jitter_ms == 0 and loss_pct == 0:
        return "tc qdisc del dev eth0 root || true"
    parts = ["tc qdisc replace dev eth0 root netem"]
    if delay_ms > 0 or jitter_ms > 0:
        parts.append(f"delay {delay_ms}ms")
        if jitter_ms > 0:
            parts.append(f"{jitter_ms}ms")
            parts.append("distribution normal")
    if loss_pct > 0:
        parts.append(f"loss {loss_pct}%")
    return " ".join(parts)


def apply_netem(container, *, delay_ms: float, jitter_ms: float, loss_pct: float) -> None:
    command = _netem_command(delay_ms, jitter_ms, loss_pct)
    result = container.exec_run(["sh", "-lc", command])
    if result.exit_code != 0:
        raise RuntimeError(f"failed to apply netem on {container.name}: {result.output.decode('utf-8', errors='ignore')}")


def build_resource_update_kwargs(resources: ResourceLimits) -> dict[str, int]:
    update_kwargs: dict[str, int] = {}
    if resources.cpu_limit_cores is not None:
        update_kwargs["cpu_period"] = 100_000
        update_kwargs["cpu_quota"] = max(1_000, int(resources.cpu_limit_cores * 100_000))
    if resources.memory_limit_mb is not None:
        mem_bytes = resources.memory_limit_mb * 1024 * 1024
        update_kwargs["mem_limit"] = mem_bytes
        update_kwargs["memswap_limit"] = mem_bytes
    return update_kwargs


def apply_resource_limits(container, resources: ResourceLimits) -> None:
    update_kwargs = build_resource_update_kwargs(resources)
    if not update_kwargs:
        return
    container.update(**update_kwargs)
    container.reload()


def fetch_stats(container) -> StatsSample:
    stats = container.stats(stream=False)
    cpu_total = stats["cpu_stats"]["cpu_usage"]["total_usage"]
    precpu_total = stats.get("precpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
    system_total = stats["cpu_stats"].get("system_cpu_usage", 0)
    presystem_total = stats.get("precpu_stats", {}).get("system_cpu_usage", 0)
    cpu_delta = cpu_total - precpu_total
    system_delta = system_total - presystem_total
    online_cpus = stats["cpu_stats"].get("online_cpus") or len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", []) or [1])
    cpu_pct = (cpu_delta / system_delta) * online_cpus * 100 if cpu_delta > 0 and system_delta > 0 else 0.0
    memory_mb = stats["memory_stats"].get("usage", 0) / (1024 * 1024)
    service = container.labels.get("com.docker.compose.service", container.name)
    return StatsSample(service=service, cpu_pct=cpu_pct, memory_mb=memory_mb, cpu_total_ns=cpu_total)


async def wait_for_peer(port: int) -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
        try:
            await asyncio.wait_for(channel.channel_ready(), timeout=1.0)
            await channel.close()
            return
        except Exception:  # noqa: BLE001
            await channel.close()
            await asyncio.sleep(0.5)
    raise TimeoutError(f"peer on port {port} did not become ready")


async def collect_container_stats(containers: dict[str, any], stop_event: asyncio.Event) -> list[StatsSample]:
    samples: list[StatsSample] = []
    while not stop_event.is_set():
        for container in containers.values():
            sample = await asyncio.to_thread(fetch_stats, container)
            samples.append(sample)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
    return samples


def summarize_stats(samples: list[StatsSample]) -> tuple[float, float, float]:
    if not samples:
        return 0.0, 0.0, 0.0
    cpu_avg = sum(sample.cpu_pct for sample in samples) / len(samples)
    memory_avg = sum(sample.memory_mb for sample in samples) / len(samples)
    cpu_by_service: dict[str, list[int]] = {}
    for sample in samples:
        cpu_by_service.setdefault(sample.service, []).append(sample.cpu_total_ns)
    cpu_time_s = 0.0
    for values in cpu_by_service.values():
        if len(values) > 1:
            cpu_time_s += max(values[-1] - values[0], 0) / 1_000_000_000
    return cpu_avg, memory_avg, cpu_time_s


def prepare_output_root(output_root: str | Path) -> Path:
    root = Path(output_root)
    try:
        root.mkdir(parents=True, exist_ok=True)
        return root
    except (FileExistsError, NotADirectoryError, PermissionError):
        fallback_name = "benchmark-results" if root.name == "results" else f"{root.name}-artifacts"
        fallback = root.parent / fallback_name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return slug.strip("-") or "run"


async def run_benchmark(
    *,
    scenario_path: str | Path,
    output_root: str | Path = "results",
    cpu_limit_cores: float | None = None,
    memory_limit_mb: int | None = None,
    keep_up: bool = False,
) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    scenario = load_scenario(scenario_path)
    return await run_benchmark_for_scenario(
        scenario=scenario,
        output_root=output_root,
        cpu_limit_cores=cpu_limit_cores,
        memory_limit_mb=memory_limit_mb,
        keep_up=keep_up,
    )


async def run_benchmark_for_scenario(
    *,
    scenario: Scenario,
    output_root: str | Path = "results",
    cpu_limit_cores: float | None = None,
    memory_limit_mb: int | None = None,
    keep_up: bool = False,
    matrix_group: str = "default",
    repeat_index: int = 1,
    network_label: str = "custom",
    output_name: str | None = None,
    build_images: bool = True,
) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if cpu_limit_cores is not None:
        scenario.resources.cpu_limit_cores = cpu_limit_cores
    if memory_limit_mb is not None:
        scenario.resources.memory_limit_mb = memory_limit_mb
    output_root_path = prepare_output_root(output_root)
    run_name = output_name or scenario.name
    output_dir = output_root_path / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(run_name)}"
    output_dir.mkdir(parents=True, exist_ok=True)

    harness = ComposeHarness(repo_root)
    client = docker.from_env()
    stop_stats = asyncio.Event()

    try:
        harness.up(extra_peer_count=max(scenario.peer_count - 2, 0), build=build_images)
        for service in ("peer_a", "peer_b", "peer_extra"):
            for container in harness.list_containers(client, service):
                apply_resource_limits(container, scenario.resources)
        await asyncio.gather(*(wait_for_peer(port) for port in PRIMARY_PORTS.values()))
        containers = {service: harness.find_container(client, service) for service in PRIMARY_PORTS}

        channel_a = grpc.aio.insecure_channel("127.0.0.1:50051")
        channel_b = grpc.aio.insecure_channel("127.0.0.1:50052")
        await asyncio.gather(channel_a.channel_ready(), channel_b.channel_ready())
        stub_a = pb2_grpc.CryptoPeerStub(channel_a)
        stub_b = pb2_grpc.CryptoPeerStub(channel_b)

        await asyncio.gather(
            stub_a.ResetState(pb2.ResetStateRequest()),
            stub_b.ResetState(pb2.ResetStateRequest()),
        )
        await asyncio.gather(
            stub_a.Bootstrap(
                pb2.BootstrapRequest(peer_name="peer-a", mode=scenario_to_proto(scenario).mode, rekey_interval_s=scenario.rekey_interval_s)
            ),
            stub_b.Bootstrap(
                pb2.BootstrapRequest(peer_name="peer-b", mode=scenario_to_proto(scenario).mode, rekey_interval_s=scenario.rekey_interval_s)
            ),
        )
        await stub_a.ConnectPeer(
            pb2.ConnectPeerRequest(
                remote_name="peer-b",
                remote_host="peer_b",
                remote_port=50052,
                mode=scenario_to_proto(scenario).mode,
            )
        )

        apply_netem(
            containers["peer_a"],
            delay_ms=scenario.network.delay_ms,
            jitter_ms=scenario.network.jitter_ms,
            loss_pct=scenario.network.loss_pct,
        )
        apply_netem(
            containers["peer_b"],
            delay_ms=scenario.network.delay_ms,
            jitter_ms=scenario.network.jitter_ms,
            loss_pct=scenario.network.loss_pct,
        )

        stats_task = asyncio.create_task(collect_container_stats(containers, stop_stats))
        await stub_a.StartScenario(
            pb2.StartScenarioRequest(
                scenario=scenario_to_proto(scenario),
                target_name="peer-b",
                target_host="peer_b",
                target_port=50052,
            )
        )

        timeout_deadline = time.time() + scenario.duration_s + max(30, scenario.duration_s)
        primary_response = None
        while time.time() < timeout_deadline:
            primary_response = await stub_a.GetMetrics(pb2.GetMetricsRequest())
            if not primary_response.active and primary_response.messages_attempted > 0:
                break
            await asyncio.sleep(0.5)

        stop_stats.set()
        stats_samples = await stats_task
        receiver_response = await stub_b.GetMetrics(pb2.GetMetricsRequest())
        primary_metrics = metrics_response_to_dict(primary_response or await stub_a.GetMetrics(pb2.GetMetricsRequest()))
        receiver_metrics = metrics_response_to_dict(receiver_response)
        cpu_avg, memory_avg, cpu_time_s = summarize_stats(stats_samples)
        summary = aggregate_run(
            scenario=scenario,
            primary_metrics=primary_metrics,
            receiver_metrics=receiver_metrics,
            cpu_pct_avg=cpu_avg,
            memory_mb_avg=memory_avg,
            cpu_time_s=cpu_time_s,
        )
        summary = replace(
            summary,
            repeat_index=repeat_index,
            matrix_group=matrix_group,
            network_label=network_label,
            network_delay_ms=scenario.network.delay_ms,
            network_jitter_ms=scenario.network.jitter_ms,
            network_loss_pct=scenario.network.loss_pct,
            rekey_interval_s=scenario.rekey_interval_s,
            duration_s=scenario.duration_s,
        )
        write_summary(summary, output_dir)
        (output_dir / "raw_metrics.json").write_text(
            json.dumps({"peer_a": primary_metrics, "peer_b": receiver_metrics}, indent=2),
            encoding="utf-8",
        )
        generate_plots(
            output_dir=output_dir,
            summary=summary,
            latencies_ms=primary_metrics["latencies_ms"],
            mode_switches=primary_metrics["mode_switches"],
        )
        await asyncio.gather(channel_a.close(), channel_b.close())
        return output_dir
    finally:
        with contextlib.suppress(Exception):
            containers = {service: harness.find_container(client, service) for service in PRIMARY_PORTS}
            for container in containers.values():
                apply_netem(container, delay_ms=0, jitter_ms=0, loss_pct=0)
        if not keep_up:
            harness.down()
