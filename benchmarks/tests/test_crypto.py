from bench.config import RuntimeProfile
from bench.crypto import ProtectedPayload, derive_session_material, protect_message, unprotect_message


def test_lightweight_token_is_sequence_bound_and_order_independent() -> None:
    shared_secret = b"x" * 32
    material = derive_session_material(shared_secret, RuntimeProfile.LIGHTWEIGHT, 1)
    plaintext = b"payload"

    protected_one, _ = protect_message(
        material=material,
        sender="peer-a",
        recipient="peer-b",
        epoch=1,
        sequence=1,
        plaintext=plaintext,
    )
    protected_three, _ = protect_message(
        material=material,
        sender="peer-a",
        recipient="peer-b",
        epoch=1,
        sequence=3,
        plaintext=plaintext,
    )

    recovered_three, _ = unprotect_message(
        material=material,
        sender="peer-a",
        recipient="peer-b",
        epoch=1,
        sequence=3,
        payload=ProtectedPayload(
            nonce=protected_three.nonce,
            ciphertext=protected_three.ciphertext,
            auth_tag=protected_three.auth_tag,
            hash_token=protected_three.hash_token,
            overhead_bytes=protected_three.overhead_bytes,
        ),
    )
    recovered_one, _ = unprotect_message(
        material=material,
        sender="peer-a",
        recipient="peer-b",
        epoch=1,
        sequence=1,
        payload=ProtectedPayload(
            nonce=protected_one.nonce,
            ciphertext=protected_one.ciphertext,
            auth_tag=protected_one.auth_tag,
            hash_token=protected_one.hash_token,
            overhead_bytes=protected_one.overhead_bytes,
        ),
    )

    assert recovered_three == plaintext
    assert recovered_one == plaintext
    assert protected_one.hash_token != protected_three.hash_token
