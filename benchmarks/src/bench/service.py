from __future__ import annotations

import asyncio
import time
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

import grpc

from .config import BenchmarkMode, RuntimeProfile
from .crypto import (
    ProtectedPayload,
    derive_session_material,
    generate_private_key,
    protect_message,
    public_key_bytes,
    shared_secret_from_public,
    unprotect_message,
)
from .policy import select_runtime_profile, scheduled_value
from .proto import crypto_peer_pb2 as pb2
from .proto import crypto_peer_pb2_grpc as pb2_grpc
from .proto_helpers import MODE_FROM_PROTO, MODE_TO_PROTO, PROFILE_TO_PROTO, scenario_from_proto


@dataclass
class ModeSwitchRecord:
    at_s: float
    profile: RuntimeProfile
    reason: str


@dataclass
class RuntimeMetrics:
    peer_name: str
    configured_mode: BenchmarkMode = BenchmarkMode.STATIC_LIGHTWEIGHT
    active: bool = False
    active_profile: RuntimeProfile = RuntimeProfile.BALANCED
    messages_attempted: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    send_errors: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    mode_switches: list[ModeSwitchRecord] = field(default_factory=list)
    bytes_plaintext: int = 0
    bytes_ciphertext: int = 0
    bytes_overhead: int = 0
    rekey_count: int = 0
    bootstrap_times_ms: list[float] = field(default_factory=list)
    rekey_times_ms: list[float] = field(default_factory=list)
    started_at_epoch_s: float = 0.0
    ended_at_epoch_s: float = 0.0
    threat_value: float = 0.0
    energy_value: float = 1.0
    last_sequence: int = 0
    heavy_messages: int = 0
    balanced_messages: int = 0
    lightweight_messages: int = 0


@dataclass(frozen=True)
class SendAttemptResult:
    profile: RuntimeProfile
    latency_ms: float | None
    observed_overhead: int | None
    error: str | None = None


@dataclass
class PeerConnection:
    peer_name: str
    host: str
    port: int
    shared_secret: bytes
    epoch: int
    channel: grpc.aio.Channel | None = None
    stub: pb2_grpc.CryptoPeerStub | None = None
    materials: dict[tuple[int, RuntimeProfile], Any] = field(default_factory=dict)
    send_hash_token: bytes | None = None
    recv_hash_token: bytes | None = None
    received_sequences: set[int] = field(default_factory=set)

    def material_for(self, profile: RuntimeProfile):
        key = (self.epoch, profile)
        if key not in self.materials:
            self.materials[key] = derive_session_material(self.shared_secret, profile, self.epoch)
        return self.materials[key]

    async def close(self) -> None:
        if self.channel is not None:
            await self.channel.close()


class CryptoPeerService(pb2_grpc.CryptoPeerServicer):
    MAX_INFLIGHT_SENDS = 32

    def __init__(self, *, peer_name: str) -> None:
        self._peer_name = peer_name
        self._configured_mode = BenchmarkMode.STATIC_LIGHTWEIGHT
        self._rekey_interval_s = 10.0
        self._connections: dict[str, PeerConnection] = {}
        self._metrics = RuntimeMetrics(peer_name=peer_name)
        self._lock = asyncio.Lock()
        self._scenario_task: asyncio.Task[None] | None = None
        self._stop_requested = asyncio.Event()

    async def Bootstrap(self, request: pb2.BootstrapRequest, context: grpc.aio.ServicerContext) -> pb2.BootstrapResponse:
        async with self._lock:
            self._peer_name = request.peer_name or self._peer_name
            self._configured_mode = MODE_FROM_PROTO.get(request.mode, BenchmarkMode.STATIC_LIGHTWEIGHT)
            self._rekey_interval_s = request.rekey_interval_s or self._rekey_interval_s
            self._metrics.peer_name = self._peer_name
            self._metrics.configured_mode = self._configured_mode
        return pb2.BootstrapResponse(ok=True, message="bootstrap configured", peer_name=self._peer_name)

    async def ConnectPeer(
        self,
        request: pb2.ConnectPeerRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ConnectPeerResponse:
        remote_mode = MODE_FROM_PROTO.get(request.mode, self._configured_mode)
        async with self._lock:
            self._configured_mode = remote_mode
            self._metrics.configured_mode = remote_mode
        handshake_ms = await self._perform_handshake(
            remote_name=request.remote_name,
            remote_host=request.remote_host,
            remote_port=request.remote_port,
            epoch=1,
            record_as_rekey=False,
        )
        return pb2.ConnectPeerResponse(ok=True, message="peer connected", bootstrap_ms=handshake_ms)

    async def StartScenario(
        self,
        request: pb2.StartScenarioRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.StartScenarioResponse:
        if self._scenario_task and not self._scenario_task.done():
            return pb2.StartScenarioResponse(accepted=False, message="scenario already running")
        scenario = scenario_from_proto(request.scenario)
        async with self._lock:
            self._stop_requested.clear()
        if request.target_name not in self._connections:
            await self._perform_handshake(
                remote_name=request.target_name,
                remote_host=request.target_host,
                remote_port=request.target_port,
                epoch=1,
                record_as_rekey=False,
            )
        self._scenario_task = asyncio.create_task(
            self._run_scenario(
                scenario=scenario,
                target_name=request.target_name,
                target_host=request.target_host,
                target_port=request.target_port,
            )
        )
        return pb2.StartScenarioResponse(accepted=True, message="scenario started")

    async def StopScenario(
        self,
        request: pb2.StopScenarioRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.StopScenarioResponse:
        self._stop_requested.set()
        if self._scenario_task is not None:
            with suppress(asyncio.CancelledError):
                await self._scenario_task
        return pb2.StopScenarioResponse(stopped=True, message="scenario stopped")

    async def GetMetrics(
        self,
        request: pb2.GetMetricsRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.MetricsResponse:
        async with self._lock:
            metrics = self._metrics
            mode_switches = [
                pb2.ModeSwitch(
                    at_s=item.at_s,
                    profile=PROFILE_TO_PROTO[item.profile],
                    reason=item.reason,
                )
                for item in metrics.mode_switches
            ]
            return pb2.MetricsResponse(
                active=metrics.active,
                peer_name=metrics.peer_name,
                messages_attempted=metrics.messages_attempted,
                messages_sent=metrics.messages_sent,
                messages_received=metrics.messages_received,
                send_errors=metrics.send_errors,
                latencies_ms=metrics.latencies_ms,
                mode_switches=mode_switches,
                bytes_plaintext=metrics.bytes_plaintext,
                bytes_ciphertext=metrics.bytes_ciphertext,
                bytes_overhead=metrics.bytes_overhead,
                rekey_count=metrics.rekey_count,
                bootstrap_times_ms=metrics.bootstrap_times_ms,
                rekey_times_ms=metrics.rekey_times_ms,
                started_at_epoch_s=metrics.started_at_epoch_s,
                ended_at_epoch_s=metrics.ended_at_epoch_s,
                threat_value=metrics.threat_value,
                energy_value=metrics.energy_value,
                configured_mode=MODE_TO_PROTO[metrics.configured_mode],
                active_profile=PROFILE_TO_PROTO[metrics.active_profile],
                last_sequence=metrics.last_sequence,
                heavy_messages=metrics.heavy_messages,
                balanced_messages=metrics.balanced_messages,
                lightweight_messages=metrics.lightweight_messages,
            )

    async def ResetState(
        self,
        request: pb2.ResetStateRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ResetStateResponse:
        self._stop_requested.set()
        if self._scenario_task is not None:
            self._scenario_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._scenario_task
        async with self._lock:
            for connection in self._connections.values():
                await connection.close()
            self._connections.clear()
            self._metrics = RuntimeMetrics(
                peer_name=self._peer_name,
                configured_mode=self._configured_mode,
            )
            self._stop_requested = asyncio.Event()
            self._scenario_task = None
        return pb2.ResetStateResponse(ok=True, message="state reset")

    async def ExchangeSession(
        self,
        request: pb2.SessionHello,
        context: grpc.aio.ServicerContext,
    ) -> pb2.SessionReply:
        start = time.perf_counter()
        local_private_key = generate_private_key()
        shared_secret = shared_secret_from_public(local_private_key, request.public_key)
        handshake_ms = (time.perf_counter() - start) * 1000
        async with self._lock:
            existing = self._connections.get(request.from_peer)
            connection = PeerConnection(
                peer_name=request.from_peer,
                host=existing.host if existing else "",
                port=existing.port if existing else 0,
                shared_secret=shared_secret,
                epoch=int(request.epoch),
            )
            self._connections[request.from_peer] = connection
            self._metrics.bootstrap_times_ms.append(round(handshake_ms, 3))
        return pb2.SessionReply(
            ok=True,
            public_key=public_key_bytes(local_private_key),
            message="session established",
            handshake_ms=round(handshake_ms, 3),
        )

    async def SendProtectedMessage(
        self,
        request: pb2.ProtectedMessage,
        context: grpc.aio.ServicerContext,
    ) -> pb2.ProtectedAck:
        async with self._lock:
            connection = self._connections.get(request.from_peer)
            if connection is None:
                return pb2.ProtectedAck(ok=False, message="unknown peer", sequence=request.sequence)
            if connection.epoch != request.epoch:
                return pb2.ProtectedAck(ok=False, message="epoch mismatch", sequence=request.sequence)
            if request.sequence in connection.received_sequences:
                return pb2.ProtectedAck(ok=False, message="replayed sequence", sequence=request.sequence)
            profile = pb2.RuntimeProfile.Name(request.profile).lower()
            runtime_profile = {
                "heavy": RuntimeProfile.HEAVY,
                "balanced": RuntimeProfile.BALANCED,
                "lightweight": RuntimeProfile.LIGHTWEIGHT,
            }[profile]
            material = connection.material_for(runtime_profile)
            try:
                plaintext, next_token = unprotect_message(
                    material=material,
                    sender=request.from_peer,
                    recipient=request.to_peer,
                    epoch=request.epoch,
                    sequence=request.sequence,
                    payload=ProtectedPayload(
                        nonce=request.nonce,
                        ciphertext=request.ciphertext,
                        auth_tag=request.auth_tag,
                        hash_token=request.hash_token,
                        overhead_bytes=len(request.nonce)
                        + len(request.auth_tag)
                        + len(request.hash_token)
                        + max(len(request.ciphertext) - request.plaintext_size, 0),
                    ),
                    previous_hash_token=connection.recv_hash_token,
                )
            except Exception as exc:  # noqa: BLE001
                return pb2.ProtectedAck(ok=False, message=str(exc), sequence=request.sequence)
            connection.recv_hash_token = next_token or connection.recv_hash_token
            connection.received_sequences.add(request.sequence)
            self._metrics.messages_received += 1
            self._metrics.bytes_plaintext += len(plaintext)
            self._metrics.bytes_ciphertext += len(request.nonce) + len(request.ciphertext)
            self._metrics.bytes_overhead += len(request.auth_tag) + len(request.hash_token)
            self._metrics.last_sequence = max(self._metrics.last_sequence, request.sequence)
        return pb2.ProtectedAck(
            ok=True,
            message="accepted",
            sequence=request.sequence,
            observed_overhead=len(request.nonce)
            + len(request.auth_tag)
            + len(request.hash_token)
            + max(len(request.ciphertext) - request.plaintext_size, 0),
        )

    async def _perform_handshake(
        self,
        *,
        remote_name: str,
        remote_host: str,
        remote_port: int,
        epoch: int,
        record_as_rekey: bool,
    ) -> float:
        channel = grpc.aio.insecure_channel(f"{remote_host}:{remote_port}")
        await channel.channel_ready()
        stub = pb2_grpc.CryptoPeerStub(channel)
        local_private_key = generate_private_key()
        start = time.perf_counter()
        reply = await stub.ExchangeSession(
            pb2.SessionHello(
                from_peer=self._peer_name,
                public_key=public_key_bytes(local_private_key),
                epoch=epoch,
            ),
            timeout=5.0,
        )
        handshake_ms = round((time.perf_counter() - start) * 1000, 3)
        shared_secret = shared_secret_from_public(local_private_key, reply.public_key)
        async with self._lock:
            existing = self._connections.get(remote_name)
            if existing is not None:
                await existing.close()
            self._connections[remote_name] = PeerConnection(
                peer_name=remote_name,
                host=remote_host,
                port=remote_port,
                shared_secret=shared_secret,
                epoch=epoch,
                channel=channel,
                stub=stub,
            )
            if record_as_rekey:
                self._metrics.rekey_count += 1
                self._metrics.rekey_times_ms.append(handshake_ms)
            else:
                self._metrics.bootstrap_times_ms.append(handshake_ms)
        return handshake_ms

    async def _run_scenario(
        self,
        *,
        scenario,
        target_name: str,
        target_host: str,
        target_port: int,
    ) -> None:
        async with self._lock:
            bootstrap_times = list(self._metrics.bootstrap_times_ms)
            self._metrics = RuntimeMetrics(
                peer_name=self._peer_name,
                configured_mode=scenario.mode,
                bootstrap_times_ms=bootstrap_times,
            )
            self._metrics.active = True
            self._metrics.started_at_epoch_s = time.time()
        start_monotonic = time.monotonic()
        next_tick = start_monotonic
        sequence = 1
        current_profile: RuntimeProfile | None = None
        last_rekey_at = start_monotonic
        pending_sends: set[asyncio.Task[SendAttemptResult]] = set()
        while not self._stop_requested.is_set():
            await self._harvest_send_tasks(pending_sends)
            now = time.monotonic()
            elapsed = now - start_monotonic
            if elapsed >= scenario.duration_s:
                break
            threat = scheduled_value(scenario.threat_schedule, elapsed)
            energy = scheduled_value(scenario.energy_schedule, elapsed)
            profile, reason = select_runtime_profile(scenario.mode, threat, energy)
            async with self._lock:
                self._metrics.threat_value = threat
                self._metrics.energy_value = energy
                self._metrics.active_profile = profile
                if current_profile is not None and current_profile != profile:
                    self._metrics.mode_switches.append(
                        ModeSwitchRecord(at_s=round(elapsed, 3), profile=profile, reason=reason)
                    )
            if current_profile is None:
                current_profile = profile
            elif current_profile != profile:
                current_profile = profile

            if now - last_rekey_at >= scenario.rekey_interval_s:
                await self._harvest_send_tasks(pending_sends, wait_for_all=True)
                connection = self._connections[target_name]
                await self._perform_handshake(
                    remote_name=target_name,
                    remote_host=target_host,
                    remote_port=target_port,
                    epoch=connection.epoch + 1,
                    record_as_rekey=True,
                )
                last_rekey_at = time.monotonic()

            async with self._lock:
                self._metrics.messages_attempted += 1
            if len(pending_sends) < self.MAX_INFLIGHT_SENDS:
                payload = self._make_payload(sequence=sequence, size=scenario.message_size_bytes)
                pending_sends.add(
                    asyncio.create_task(
                        self._send_and_measure(
                            target_name=target_name,
                            profile=profile,
                            sequence=sequence,
                            plaintext=payload,
                        )
                    )
                )
            sequence += 1
            next_tick += 1.0 / scenario.message_rate_hz
            await asyncio.sleep(max(0.0, next_tick - time.monotonic()))

        await self._harvest_send_tasks(pending_sends, wait_for_all=True)
        async with self._lock:
            self._metrics.active = False
            self._metrics.ended_at_epoch_s = time.time()

    async def _harvest_send_tasks(
        self,
        pending_sends: set[asyncio.Task[SendAttemptResult]],
        *,
        wait_for_all: bool = False,
    ) -> None:
        if not pending_sends:
            return
        if wait_for_all:
            done, still_pending = await asyncio.wait(pending_sends)
        else:
            done = {task for task in pending_sends if task.done()}
            still_pending = pending_sends - done
        pending_sends.clear()
        pending_sends.update(still_pending)
        for task in done:
            try:
                result = task.result()
            except Exception:  # noqa: BLE001
                async with self._lock:
                    self._metrics.send_errors += 1
                continue
            if result.error is not None or result.latency_ms is None or result.observed_overhead is None:
                async with self._lock:
                    self._metrics.send_errors += 1
                continue
            async with self._lock:
                self._metrics.messages_sent += 1
                self._metrics.latencies_ms.append(result.latency_ms)
                if result.profile == RuntimeProfile.HEAVY:
                    self._metrics.heavy_messages += 1
                elif result.profile == RuntimeProfile.BALANCED:
                    self._metrics.balanced_messages += 1
                else:
                    self._metrics.lightweight_messages += 1

    async def _send_and_measure(
        self,
        *,
        target_name: str,
        profile: RuntimeProfile,
        sequence: int,
        plaintext: bytes,
    ) -> SendAttemptResult:
        send_started = time.perf_counter()
        try:
            observed_overhead = await self._send_payload(
                target_name=target_name,
                profile=profile,
                sequence=sequence,
                plaintext=plaintext,
            )
        except Exception as exc:  # noqa: BLE001
            return SendAttemptResult(
                profile=profile,
                latency_ms=None,
                observed_overhead=None,
                error=str(exc),
            )
        latency_ms = round((time.perf_counter() - send_started) * 1000, 3)
        async with self._lock:
            self._metrics.bytes_plaintext += len(plaintext)
            self._metrics.bytes_ciphertext += len(plaintext) + observed_overhead
            self._metrics.bytes_overhead += observed_overhead
            self._metrics.last_sequence = max(self._metrics.last_sequence, sequence)
        return SendAttemptResult(
            profile=profile,
            latency_ms=latency_ms,
            observed_overhead=observed_overhead,
        )

    async def _send_payload(
        self,
        *,
        target_name: str,
        profile: RuntimeProfile,
        sequence: int,
        plaintext: bytes,
    ) -> int:
        connection = self._connections[target_name]
        material = connection.material_for(profile)
        protected, next_token = protect_message(
            material=material,
            sender=self._peer_name,
            recipient=target_name,
            epoch=connection.epoch,
            sequence=sequence,
            plaintext=plaintext,
            previous_hash_token=connection.send_hash_token,
        )
        reply = await connection.stub.SendProtectedMessage(
            pb2.ProtectedMessage(
                from_peer=self._peer_name,
                to_peer=target_name,
                sequence=sequence,
                epoch=connection.epoch,
                profile=PROFILE_TO_PROTO[profile],
                nonce=protected.nonce,
                ciphertext=protected.ciphertext,
                auth_tag=protected.auth_tag,
                hash_token=protected.hash_token,
                plaintext_size=len(plaintext),
            ),
            timeout=10.0,
        )
        if not reply.ok:
            raise RuntimeError(reply.message)
        connection.send_hash_token = next_token or connection.send_hash_token
        return reply.observed_overhead

    def _make_payload(self, *, sequence: int, size: int) -> bytes:
        prefix = f"{self._peer_name}:{sequence}:".encode("utf-8")
        repetitions = (size // len(prefix)) + 1
        return (prefix * repetitions)[:size]
