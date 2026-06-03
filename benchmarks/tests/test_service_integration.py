import asyncio
from contextlib import suppress

import grpc
import pytest

from bench.config import RuntimeProfile
from bench.crypto import derive_session_material, generate_private_key, protect_message, public_key_bytes, shared_secret_from_public
from bench.proto import crypto_peer_pb2 as pb2
from bench.proto import crypto_peer_pb2_grpc as pb2_grpc
from bench.proto_helpers import metrics_response_to_dict, scenario_to_proto
from bench.service import CryptoPeerService


async def start_peer(name: str) -> tuple[grpc.aio.Server, str, int]:
    server = grpc.aio.server()
    pb2_grpc.add_CryptoPeerServicer_to_server(CryptoPeerService(peer_name=name), server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    return server, f"127.0.0.1:{port}", port


async def wait_for_completion(stub: pb2_grpc.CryptoPeerStub, timeout_s: float = 10.0) -> dict:
    deadline = asyncio.get_running_loop().time() + timeout_s
    while asyncio.get_running_loop().time() < deadline:
        metrics = metrics_response_to_dict(await stub.GetMetrics(pb2.GetMetricsRequest()))
        if not metrics["active"] and metrics["messages_attempted"] > 0:
            return metrics
        await asyncio.sleep(0.1)
    raise TimeoutError("scenario did not finish in time")


@pytest.fixture
async def peer_pair():
    server_a, address_a, _ = await start_peer("peer-a")
    server_b, address_b, port_b = await start_peer("peer-b")
    yield (address_a, address_b, port_b)
    await server_a.stop(None)
    await server_b.stop(None)


@pytest.mark.parametrize(
    ("mode_name", "mode_value"),
    [("heavy", pb2.STATIC_HEAVY), ("light", pb2.STATIC_LIGHTWEIGHT)],
)
async def test_round_trip_static_modes(peer_pair, mode_name: str, mode_value: int) -> None:
    address_a, address_b, port_b = peer_pair
    channel_a = grpc.aio.insecure_channel(address_a)
    channel_b = grpc.aio.insecure_channel(address_b)
    await asyncio.gather(channel_a.channel_ready(), channel_b.channel_ready())
    stub_a = pb2_grpc.CryptoPeerStub(channel_a)
    stub_b = pb2_grpc.CryptoPeerStub(channel_b)

    await asyncio.gather(
        stub_a.ResetState(pb2.ResetStateRequest()),
        stub_b.ResetState(pb2.ResetStateRequest()),
    )
    await asyncio.gather(
        stub_a.Bootstrap(pb2.BootstrapRequest(peer_name="peer-a", mode=mode_value, rekey_interval_s=5)),
        stub_b.Bootstrap(pb2.BootstrapRequest(peer_name="peer-b", mode=mode_value, rekey_interval_s=5)),
    )
    connect_response = await stub_a.ConnectPeer(
        pb2.ConnectPeerRequest(remote_name="peer-b", remote_host="127.0.0.1", remote_port=port_b, mode=mode_value)
    )
    assert connect_response.ok

    scenario = pb2.ScenarioConfig(
        name=f"{mode_name}-integration",
        mode=mode_value,
        duration_s=1.5,
        message_rate_hz=5,
        message_size_bytes=128,
        peer_count=2,
        network=pb2.NetworkProfile(delay_ms=0, jitter_ms=0, loss_pct=0),
        threat_schedule=[pb2.ScheduledValue(at_s=0, value=0.1)],
        energy_schedule=[pb2.ScheduledValue(at_s=0, value=1.0)],
        rekey_interval_s=10,
        tags=["integration"],
    )
    start_response = await stub_a.StartScenario(
        pb2.StartScenarioRequest(
            scenario=scenario,
            target_name="peer-b",
            target_host="127.0.0.1",
            target_port=port_b,
        )
    )
    assert start_response.accepted
    primary_metrics = await wait_for_completion(stub_a)
    receiver_metrics = metrics_response_to_dict(await stub_b.GetMetrics(pb2.GetMetricsRequest()))
    assert primary_metrics["messages_sent"] > 0
    assert primary_metrics["send_errors"] == 0
    assert receiver_metrics["messages_received"] == primary_metrics["messages_sent"]
    await asyncio.gather(channel_a.close(), channel_b.close())


async def test_adaptive_mode_switches(peer_pair) -> None:
    address_a, address_b, port_b = peer_pair
    channel_a = grpc.aio.insecure_channel(address_a)
    channel_b = grpc.aio.insecure_channel(address_b)
    await asyncio.gather(channel_a.channel_ready(), channel_b.channel_ready())
    stub_a = pb2_grpc.CryptoPeerStub(channel_a)
    stub_b = pb2_grpc.CryptoPeerStub(channel_b)
    await asyncio.gather(
        stub_a.ResetState(pb2.ResetStateRequest()),
        stub_b.ResetState(pb2.ResetStateRequest()),
    )
    await asyncio.gather(
        stub_a.Bootstrap(pb2.BootstrapRequest(peer_name="peer-a", mode=pb2.ADAPTIVE, rekey_interval_s=2)),
        stub_b.Bootstrap(pb2.BootstrapRequest(peer_name="peer-b", mode=pb2.ADAPTIVE, rekey_interval_s=2)),
    )
    await stub_a.ConnectPeer(
        pb2.ConnectPeerRequest(remote_name="peer-b", remote_host="127.0.0.1", remote_port=port_b, mode=pb2.ADAPTIVE)
    )
    scenario = pb2.ScenarioConfig(
        name="adaptive-integration",
        mode=pb2.ADAPTIVE,
        duration_s=2.0,
        message_rate_hz=6,
        message_size_bytes=128,
        peer_count=2,
        network=pb2.NetworkProfile(delay_ms=0, jitter_ms=0, loss_pct=0),
        threat_schedule=[
            pb2.ScheduledValue(at_s=0, value=0.1),
            pb2.ScheduledValue(at_s=0.8, value=0.95),
        ],
        energy_schedule=[pb2.ScheduledValue(at_s=0, value=0.9)],
        rekey_interval_s=4,
        tags=["integration"],
    )
    await stub_a.StartScenario(
        pb2.StartScenarioRequest(
            scenario=scenario,
            target_name="peer-b",
            target_host="127.0.0.1",
            target_port=port_b,
        )
    )
    primary_metrics = await wait_for_completion(stub_a)
    assert primary_metrics["mode_switches"]
    assert primary_metrics["heavy_messages"] > 0
    assert primary_metrics["balanced_messages"] > 0
    await asyncio.gather(channel_a.close(), channel_b.close())


async def test_reset_clears_runtime_metrics(peer_pair) -> None:
    address_a, _, _ = peer_pair
    channel_a = grpc.aio.insecure_channel(address_a)
    await channel_a.channel_ready()
    stub_a = pb2_grpc.CryptoPeerStub(channel_a)
    await stub_a.ResetState(pb2.ResetStateRequest())
    metrics = metrics_response_to_dict(await stub_a.GetMetrics(pb2.GetMetricsRequest()))
    assert metrics["messages_attempted"] == 0
    assert metrics["messages_sent"] == 0
    await channel_a.close()


async def test_lightweight_profile_handles_concurrent_offered_load(peer_pair) -> None:
    address_a, address_b, port_b = peer_pair
    channel_a = grpc.aio.insecure_channel(address_a)
    channel_b = grpc.aio.insecure_channel(address_b)
    await asyncio.gather(channel_a.channel_ready(), channel_b.channel_ready())
    stub_a = pb2_grpc.CryptoPeerStub(channel_a)
    stub_b = pb2_grpc.CryptoPeerStub(channel_b)

    await asyncio.gather(
        stub_a.ResetState(pb2.ResetStateRequest()),
        stub_b.ResetState(pb2.ResetStateRequest()),
    )
    await asyncio.gather(
        stub_a.Bootstrap(pb2.BootstrapRequest(peer_name="peer-a", mode=pb2.STATIC_LIGHTWEIGHT, rekey_interval_s=5)),
        stub_b.Bootstrap(pb2.BootstrapRequest(peer_name="peer-b", mode=pb2.STATIC_LIGHTWEIGHT, rekey_interval_s=5)),
    )
    await stub_a.ConnectPeer(
        pb2.ConnectPeerRequest(remote_name="peer-b", remote_host="127.0.0.1", remote_port=port_b, mode=pb2.STATIC_LIGHTWEIGHT)
    )

    scenario = pb2.ScenarioConfig(
        name="lightweight-concurrent-integration",
        mode=pb2.STATIC_LIGHTWEIGHT,
        duration_s=1.0,
        message_rate_hz=200,
        message_size_bytes=256,
        peer_count=2,
        network=pb2.NetworkProfile(delay_ms=0, jitter_ms=0, loss_pct=0),
        threat_schedule=[pb2.ScheduledValue(at_s=0, value=0.1)],
        energy_schedule=[pb2.ScheduledValue(at_s=0, value=1.0)],
        rekey_interval_s=10,
        tags=["integration"],
    )
    await stub_a.StartScenario(
        pb2.StartScenarioRequest(
            scenario=scenario,
            target_name="peer-b",
            target_host="127.0.0.1",
            target_port=port_b,
        )
    )

    primary_metrics = await wait_for_completion(stub_a)
    receiver_metrics = metrics_response_to_dict(await stub_b.GetMetrics(pb2.GetMetricsRequest()))

    assert primary_metrics["messages_sent"] > 0
    assert primary_metrics["send_errors"] == 0
    assert receiver_metrics["messages_received"] == primary_metrics["messages_sent"]
    assert primary_metrics["lightweight_messages"] == primary_metrics["messages_sent"]
    await asyncio.gather(channel_a.close(), channel_b.close())


async def test_receiver_rejects_replayed_sequence_within_epoch() -> None:
    receiver = CryptoPeerService(peer_name="peer-b")
    sender_private_key = generate_private_key()
    session_reply = await receiver.ExchangeSession(
        pb2.SessionHello(
            from_peer="peer-a",
            public_key=public_key_bytes(sender_private_key),
            epoch=1,
        ),
        None,
    )
    shared_secret = shared_secret_from_public(sender_private_key, session_reply.public_key)
    material = derive_session_material(shared_secret, RuntimeProfile.LIGHTWEIGHT, 1)
    plaintext = b"replay-me"
    protected, _ = protect_message(
        material=material,
        sender="peer-a",
        recipient="peer-b",
        epoch=1,
        sequence=7,
        plaintext=plaintext,
    )
    request = pb2.ProtectedMessage(
        from_peer="peer-a",
        to_peer="peer-b",
        sequence=7,
        epoch=1,
        profile=pb2.LIGHTWEIGHT,
        nonce=protected.nonce,
        ciphertext=protected.ciphertext,
        auth_tag=protected.auth_tag,
        hash_token=protected.hash_token,
        plaintext_size=len(plaintext),
    )

    first_ack = await receiver.SendProtectedMessage(request, None)
    replay_ack = await receiver.SendProtectedMessage(request, None)
    metrics = metrics_response_to_dict(await receiver.GetMetrics(pb2.GetMetricsRequest(), None))

    assert first_ack.ok
    assert not replay_ack.ok
    assert replay_ack.message == "replayed sequence"
    assert metrics["messages_received"] == 1
