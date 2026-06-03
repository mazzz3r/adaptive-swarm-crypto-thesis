from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .config import BenchmarkMode, RuntimeProfile, ScheduledValue


@dataclass(frozen=True)
class CryptoProfile:
    profile: RuntimeProfile
    cipher_name: str
    key_bits: int
    auth_name: str
    mode_weight: float


HEAVY_PROFILE = CryptoProfile(
    profile=RuntimeProfile.HEAVY,
    cipher_name="AES-GCM",
    key_bits=256,
    auth_name="HMAC-SHA256",
    mode_weight=1.4,
)

BALANCED_PROFILE = CryptoProfile(
    profile=RuntimeProfile.BALANCED,
    cipher_name="AES-GCM",
    key_bits=192,
    auth_name="HMAC-SHA256",
    mode_weight=1.0,
)

LIGHTWEIGHT_PROFILE = CryptoProfile(
    profile=RuntimeProfile.LIGHTWEIGHT,
    cipher_name="ChaCha20-Poly1305",
    key_bits=256,
    auth_name="HashChain",
    mode_weight=0.7,
)

PROFILES = {
    RuntimeProfile.HEAVY: HEAVY_PROFILE,
    RuntimeProfile.BALANCED: BALANCED_PROFILE,
    RuntimeProfile.LIGHTWEIGHT: LIGHTWEIGHT_PROFILE,
}

HIGH_THREAT_THRESHOLD = 0.8
LOW_ENERGY_THRESHOLD = 0.2


def scheduled_value(schedule: list[ScheduledValue], elapsed_s: float) -> float:
    current = schedule[0].value
    for item in schedule:
        if elapsed_s < item.at_s:
            break
        current = item.value
    return current


def select_runtime_profile(
    mode: BenchmarkMode,
    threat: float,
    energy: float,
) -> tuple[RuntimeProfile, str]:
    if mode == BenchmarkMode.STATIC_HEAVY:
        return RuntimeProfile.HEAVY, "static-heavy"
    if mode == BenchmarkMode.STATIC_BALANCED:
        return RuntimeProfile.BALANCED, "static-balanced"
    if mode == BenchmarkMode.STATIC_LIGHTWEIGHT:
        return RuntimeProfile.LIGHTWEIGHT, "static-lightweight"
    if threat >= HIGH_THREAT_THRESHOLD:
        return RuntimeProfile.HEAVY, "high-threat"
    if energy <= LOW_ENERGY_THRESHOLD:
        return RuntimeProfile.LIGHTWEIGHT, "low-energy"
    return RuntimeProfile.BALANCED, "balanced-default"


def next_hash_token(previous: bytes) -> bytes:
    return sha256(previous).digest()
