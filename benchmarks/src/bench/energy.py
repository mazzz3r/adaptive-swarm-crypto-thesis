from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnergyCoefficients:
    cpu_second: float = 2.5
    transmitted_byte: float = 0.0002
    rekey_event: float = 8.0
    heavy_message: float = 0.35
    balanced_message: float = 0.18
    lightweight_message: float = 0.08


ENERGY_PROXY_LABEL = "Model-based energy proxy, not a physical power measurement."
CRYPTO_COST_PROXY_LABEL = "Model-based crypto processing cost, reported separately from measured latency."


@dataclass(frozen=True)
class CryptoCostCoefficients:
    heavy_message_ms: float = 15.0
    balanced_message_ms: float = 6.5
    lightweight_message_ms: float = 1.8
    rekey_event_ms: float = 12.0


def compute_energy_proxy(
    *,
    cpu_time_s: float,
    bytes_sent: int,
    rekey_count: int,
    heavy_messages: int,
    balanced_messages: int,
    lightweight_messages: int,
    coefficients: EnergyCoefficients | None = None,
) -> float:
    coeffs = coefficients or EnergyCoefficients()
    return round(
        cpu_time_s * coeffs.cpu_second
        + bytes_sent * coeffs.transmitted_byte
        + rekey_count * coeffs.rekey_event
        + heavy_messages * coeffs.heavy_message
        + balanced_messages * coeffs.balanced_message
        + lightweight_messages * coeffs.lightweight_message,
        4,
    )


def compute_modeled_crypto_cost_ms(
    *,
    rekey_count: int,
    heavy_messages: int,
    balanced_messages: int,
    lightweight_messages: int,
    coefficients: CryptoCostCoefficients | None = None,
) -> tuple[float, float]:
    coeffs = coefficients or CryptoCostCoefficients()
    total = (
        rekey_count * coeffs.rekey_event_ms
        + heavy_messages * coeffs.heavy_message_ms
        + balanced_messages * coeffs.balanced_message_ms
        + lightweight_messages * coeffs.lightweight_message_ms
    )
    message_count = heavy_messages + balanced_messages + lightweight_messages
    average = total / message_count if message_count else 0.0
    return round(total, 4), round(average, 4)
