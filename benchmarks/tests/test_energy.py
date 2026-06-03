from bench.crypto_work import compute_crypto_work
from bench.energy import EnergyCoefficients, compute_energy_proxy


def test_energy_proxy_increases_with_activity() -> None:
    low = compute_energy_proxy(
        cpu_time_s=1.0,
        bytes_sent=1024,
        rekey_count=1,
        heavy_messages=0,
        balanced_messages=10,
        lightweight_messages=50,
        coefficients=EnergyCoefficients(),
    )
    high = compute_energy_proxy(
        cpu_time_s=4.0,
        bytes_sent=8192,
        rekey_count=5,
        heavy_messages=100,
        balanced_messages=0,
        lightweight_messages=0,
        coefficients=EnergyCoefficients(),
    )
    assert high > low


def test_crypto_work_counts_authenticated_bytes() -> None:
    heavy = compute_crypto_work(
        message_size_bytes=1024,
        delivered_messages=10,
        heavy_messages=10,
        balanced_messages=0,
        lightweight_messages=0,
    )
    lightweight = compute_crypto_work(
        message_size_bytes=1024,
        delivered_messages=10,
        heavy_messages=0,
        balanced_messages=0,
        lightweight_messages=10,
    )

    assert heavy.crypto_work_bytes > lightweight.crypto_work_bytes
    assert heavy.crypto_work_mib_per_delivered_message > lightweight.crypto_work_mib_per_delivered_message
