from __future__ import annotations

from dataclasses import dataclass


CRYPTO_WORK_LABEL = (
    "Deterministic crypto work: bytes processed by encrypt/decrypt and authentication primitives."
)


@dataclass(frozen=True)
class CryptoWorkSummary:
    crypto_work_bytes: int
    crypto_work_mib_per_delivered_message: float
    crypto_primitive_calls: int


def compute_crypto_work(
    *,
    message_size_bytes: int,
    delivered_messages: int,
    heavy_messages: int,
    balanced_messages: int,
    lightweight_messages: int,
) -> CryptoWorkSummary:
    """Count deterministic cryptographic work without model weights.

    Heavy and balanced messages use AEAD plus an additional HMAC pass on
    send and verify. Lightweight messages use AEAD plus a small hash-token
    check. The metric intentionally counts bytes processed by primitives,
    not wall-clock time, because hardware acceleration and container
    scheduling can hide profile differences in latency measurements.
    """

    aead_bytes_per_message = 2 * message_size_bytes
    hmac_bytes_per_message = 2 * message_size_bytes
    hash_token_bytes_per_message = 2 * (32 + 8)

    authenticated_messages = heavy_messages + balanced_messages
    total_messages = authenticated_messages + lightweight_messages
    work_bytes = (
        total_messages * aead_bytes_per_message
        + authenticated_messages * hmac_bytes_per_message
        + lightweight_messages * hash_token_bytes_per_message
    )

    primitive_calls = (
        total_messages * 2
        + authenticated_messages * 2
        + lightweight_messages * 2
    )
    denominator = max(delivered_messages, 1)
    work_mib_per_message = work_bytes / denominator / (1024 * 1024)
    return CryptoWorkSummary(
        crypto_work_bytes=work_bytes,
        crypto_work_mib_per_delivered_message=round(work_mib_per_message, 4),
        crypto_primitive_calls=primitive_calls,
    )
