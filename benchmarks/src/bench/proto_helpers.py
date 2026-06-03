from __future__ import annotations

from .config import BenchmarkMode, RuntimeProfile, Scenario, ScheduledValue
from .proto import crypto_peer_pb2 as pb2


MODE_TO_PROTO = {
    BenchmarkMode.STATIC_HEAVY: pb2.STATIC_HEAVY,
    BenchmarkMode.STATIC_BALANCED: pb2.STATIC_BALANCED,
    BenchmarkMode.STATIC_LIGHTWEIGHT: pb2.STATIC_LIGHTWEIGHT,
    BenchmarkMode.ADAPTIVE: pb2.ADAPTIVE,
}

MODE_FROM_PROTO = {value: key for key, value in MODE_TO_PROTO.items()}

PROFILE_TO_PROTO = {
    RuntimeProfile.HEAVY: pb2.HEAVY,
    RuntimeProfile.BALANCED: pb2.BALANCED,
    RuntimeProfile.LIGHTWEIGHT: pb2.LIGHTWEIGHT,
}

PROFILE_FROM_PROTO = {value: key for key, value in PROFILE_TO_PROTO.items()}


def scenario_to_proto(scenario: Scenario) -> pb2.ScenarioConfig:
    return pb2.ScenarioConfig(
        name=scenario.name,
        mode=MODE_TO_PROTO[scenario.mode],
        duration_s=scenario.duration_s,
        message_rate_hz=scenario.message_rate_hz,
        message_size_bytes=scenario.message_size_bytes,
        peer_count=scenario.peer_count,
        network=pb2.NetworkProfile(
            delay_ms=scenario.network.delay_ms,
            jitter_ms=scenario.network.jitter_ms,
            loss_pct=scenario.network.loss_pct,
        ),
        threat_schedule=[
            pb2.ScheduledValue(at_s=item.at_s, value=item.value) for item in scenario.threat_schedule
        ],
        energy_schedule=[
            pb2.ScheduledValue(at_s=item.at_s, value=item.value) for item in scenario.energy_schedule
        ],
        rekey_interval_s=scenario.rekey_interval_s,
        tags=scenario.tags,
    )


def scenario_from_proto(message: pb2.ScenarioConfig) -> Scenario:
    return Scenario(
        name=message.name,
        mode=MODE_FROM_PROTO[message.mode],
        duration_s=message.duration_s,
        message_rate_hz=message.message_rate_hz,
        message_size_bytes=message.message_size_bytes,
        peer_count=message.peer_count,
        network={
            "delay_ms": message.network.delay_ms,
            "jitter_ms": message.network.jitter_ms,
            "loss_pct": message.network.loss_pct,
        },
        threat_schedule=[ScheduledValue(at_s=item.at_s, value=item.value) for item in message.threat_schedule],
        energy_schedule=[ScheduledValue(at_s=item.at_s, value=item.value) for item in message.energy_schedule],
        rekey_interval_s=message.rekey_interval_s,
        tags=list(message.tags),
    )


def metrics_response_to_dict(message: pb2.MetricsResponse) -> dict:
    return {
        "active": message.active,
        "peer_name": message.peer_name,
        "messages_attempted": message.messages_attempted,
        "messages_sent": message.messages_sent,
        "messages_received": message.messages_received,
        "send_errors": message.send_errors,
        "latencies_ms": list(message.latencies_ms),
        "mode_switches": [
            {"at_s": item.at_s, "profile": PROFILE_FROM_PROTO[item.profile].value, "reason": item.reason}
            for item in message.mode_switches
        ],
        "bytes_plaintext": message.bytes_plaintext,
        "bytes_ciphertext": message.bytes_ciphertext,
        "bytes_overhead": message.bytes_overhead,
        "rekey_count": message.rekey_count,
        "bootstrap_times_ms": list(message.bootstrap_times_ms),
        "rekey_times_ms": list(message.rekey_times_ms),
        "started_at_epoch_s": message.started_at_epoch_s,
        "ended_at_epoch_s": message.ended_at_epoch_s,
        "threat_value": message.threat_value,
        "energy_value": message.energy_value,
        "configured_mode": MODE_FROM_PROTO[message.configured_mode].value,
        "active_profile": PROFILE_FROM_PROTO[message.active_profile].value
        if message.active_profile in PROFILE_FROM_PROTO
        else RuntimeProfile.BALANCED.value,
        "last_sequence": message.last_sequence,
        "heavy_messages": message.heavy_messages,
        "balanced_messages": message.balanced_messages,
        "lightweight_messages": message.lightweight_messages,
    }
