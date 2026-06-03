from __future__ import annotations

import argparse
import asyncio

import grpc

from .proto import crypto_peer_pb2_grpc as pb2_grpc
from .service import CryptoPeerService


async def serve(*, peer_name: str, port: int) -> None:
    server = grpc.aio.server()
    pb2_grpc.add_CryptoPeerServicer_to_server(
        CryptoPeerService(peer_name=peer_name),
        server,
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    await server.wait_for_termination()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a benchmark crypto peer service.")
    parser.add_argument("--name", required=True, help="Peer name advertised to other services.")
    parser.add_argument("--port", type=int, required=True, help="gRPC listen port.")
    args = parser.parse_args()
    asyncio.run(serve(peer_name=args.name, port=args.port))


if __name__ == "__main__":
    main()
