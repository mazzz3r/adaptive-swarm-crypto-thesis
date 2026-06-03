from __future__ import annotations

import os
from hashlib import sha256
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .config import RuntimeProfile
@dataclass(frozen=True)
class SessionMaterial:
    profile: RuntimeProfile
    encryption_key: bytes
    auth_key: bytes
    chain_seed: bytes


@dataclass(frozen=True)
class ProtectedPayload:
    nonce: bytes
    ciphertext: bytes
    auth_tag: bytes
    hash_token: bytes
    overhead_bytes: int


def generate_private_key() -> X25519PrivateKey:
    return X25519PrivateKey.generate()


def public_key_bytes(private_key: X25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def shared_secret_from_public(private_key: X25519PrivateKey, public_key: bytes) -> bytes:
    peer_public = X25519PublicKey.from_public_bytes(public_key)
    return private_key.exchange(peer_public)


def derive_session_material(
    shared_secret: bytes,
    profile: RuntimeProfile,
    epoch: int,
) -> SessionMaterial:
    if profile == RuntimeProfile.HEAVY:
        encryption_key_len = 32
        auth_key_len = 32
    elif profile == RuntimeProfile.BALANCED:
        encryption_key_len = 24
        auth_key_len = 32
    else:
        encryption_key_len = 32
        auth_key_len = 0

    chain_seed_len = 32
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=encryption_key_len + auth_key_len + chain_seed_len,
        salt=epoch.to_bytes(8, "big", signed=False),
        info=f"bench:{profile.value}".encode("utf-8"),
    )
    material = hkdf.derive(shared_secret)
    enc_key = material[:encryption_key_len]
    auth_key = material[encryption_key_len : encryption_key_len + auth_key_len]
    chain_seed = material[-chain_seed_len:]
    return SessionMaterial(
        profile=profile,
        encryption_key=enc_key,
        auth_key=auth_key,
        chain_seed=chain_seed,
    )


def _associated_data(
    *,
    sender: str,
    recipient: str,
    epoch: int,
    sequence: int,
    profile: RuntimeProfile,
) -> bytes:
    return f"{sender}|{recipient}|{epoch}|{sequence}|{profile.value}".encode("utf-8")


def _sequence_hash_token(seed: bytes, sequence: int) -> bytes:
    return sha256(seed + sequence.to_bytes(8, "big", signed=False)).digest()


def protect_message(
    *,
    material: SessionMaterial,
    sender: str,
    recipient: str,
    epoch: int,
    sequence: int,
    plaintext: bytes,
    previous_hash_token: bytes | None = None,
) -> tuple[ProtectedPayload, bytes | None]:
    aad = _associated_data(
        sender=sender,
        recipient=recipient,
        epoch=epoch,
        sequence=sequence,
        profile=material.profile,
    )
    nonce = os.urandom(12)
    if material.profile in {RuntimeProfile.HEAVY, RuntimeProfile.BALANCED}:
        ciphertext = AESGCM(material.encryption_key).encrypt(nonce, plaintext, aad)
        signer = hmac.HMAC(material.auth_key, hashes.SHA256())
        signer.update(aad)
        signer.update(nonce)
        signer.update(ciphertext)
        auth_tag = signer.finalize()
        overhead = len(nonce) + (len(ciphertext) - len(plaintext)) + len(auth_tag)
        payload = ProtectedPayload(
            nonce=nonce,
            ciphertext=ciphertext,
            auth_tag=auth_tag,
            hash_token=b"",
            overhead_bytes=overhead,
        )
        return payload, None

    ciphertext = ChaCha20Poly1305(material.encryption_key).encrypt(nonce, plaintext, aad)
    current_token = _sequence_hash_token(material.chain_seed, sequence)
    overhead = len(nonce) + (len(ciphertext) - len(plaintext)) + len(current_token)
    payload = ProtectedPayload(
        nonce=nonce,
        ciphertext=ciphertext,
        auth_tag=b"",
        hash_token=current_token,
        overhead_bytes=overhead,
    )
    return payload, current_token


def unprotect_message(
    *,
    material: SessionMaterial,
    sender: str,
    recipient: str,
    epoch: int,
    sequence: int,
    payload: ProtectedPayload,
    previous_hash_token: bytes | None = None,
) -> tuple[bytes, bytes | None]:
    aad = _associated_data(
        sender=sender,
        recipient=recipient,
        epoch=epoch,
        sequence=sequence,
        profile=material.profile,
    )
    if material.profile in {RuntimeProfile.HEAVY, RuntimeProfile.BALANCED}:
        verifier = hmac.HMAC(material.auth_key, hashes.SHA256())
        verifier.update(aad)
        verifier.update(payload.nonce)
        verifier.update(payload.ciphertext)
        verifier.verify(payload.auth_tag)
        plaintext = AESGCM(material.encryption_key).decrypt(payload.nonce, payload.ciphertext, aad)
        return plaintext, None

    expected_token = _sequence_hash_token(material.chain_seed, sequence)
    if expected_token != payload.hash_token:
        raise InvalidSignature("hash-chain token mismatch")
    plaintext = ChaCha20Poly1305(material.encryption_key).decrypt(payload.nonce, payload.ciphertext, aad)
    return plaintext, payload.hash_token
