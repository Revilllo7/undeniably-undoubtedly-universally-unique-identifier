import os
import time
import random
import hashlib
import threading
from typing import Dict
from flask import Flask, jsonify, request


class UUUUIDGenerator:
    """
    Undeniably, Undoubtedly, Universally Unique Identifier (UUUUID)
    Generator with recursive global registry checking.
    This is a mock distributed system: the registry is shared in-memory.
    Output size is 8192 bits (1024 bytes).
    """

    _lock = threading.Lock()
    _counter = 0

    # 8192-bit (1024-byte) history seed
    _OUTPUT_BYTES = 1024
    _history_hash = b"\x00" * _OUTPUT_BYTES

    # Simulated global registry (shared across instances)
    GLOBAL_REGISTRY: Dict[str, str] = {}
    REGISTRY_LOCK = threading.Lock()

    def __init__(self):
        pass

    def _generate_candidate(self) -> bytes:
        """
        Generate a raw candidate UUUUID (before checking).
        Uses SHAKE256 to produce an arbitrary-length digest (1024 bytes).
        Includes randomized ordering of entropy components.
        """

        with UUUUIDGenerator._lock:
            UUUUIDGenerator._counter += 1
            counter_bytes = UUUUIDGenerator._counter.to_bytes(16, "big")

        timestamp = time.time_ns().to_bytes(16, "big")
        machine_fp = hashlib.sha256(
            (os.uname().nodename + os.uname().machine).encode()
        ).digest()
        rand1 = os.urandom(32)
        rand2 = os.urandom(32)
        parts = [rand1, rand2, timestamp, machine_fp, counter_bytes, UUUUIDGenerator._history_hash]
        random.shuffle(parts)
        payload = b"".join(parts)

        # Use SHAKE256 to produce a 1024-byte candidate (8192 bits)
        candidate = hashlib.shake_256(payload).digest(UUUUIDGenerator._OUTPUT_BYTES)

        # Update history with same XOF to keep history the same size
        UUUUIDGenerator._history_hash = hashlib.shake_256(UUUUIDGenerator._history_hash + candidate).digest(
            UUUUIDGenerator._OUTPUT_BYTES
        )
        return candidate

    def generate_uuuuid(self) -> str:
        """
        Public method: generate and register UUUUID with iterative checking.

        If the environment variable `REGISTRY_API_URL` is set, the generator will
        attempt to register candidates against that API (`POST /registry/register`).
        If no API is configured, it will fall back to the in-memory
        `GLOBAL_REGISTRY` protected by `REGISTRY_LOCK`.
        """

        registry_api = os.environ.get("REGISTRY_API_URL")

        while True:
            candidate_hex = self._generate_candidate().hex()

            # Try API-based registration first if configured
            if registry_api:
                try:
                    if self._register_via_api(candidate_hex, registry_api):
                        return candidate_hex
                except Exception:
                    # If API check fails, fall through and try again or local fallback
                    pass
                continue

            # Fallback: local in-memory reservation
            with UUUUIDGenerator.REGISTRY_LOCK:
                if candidate_hex in UUUUIDGenerator.GLOBAL_REGISTRY:
                    # collision detected — generate again
                    continue
                UUUUIDGenerator.GLOBAL_REGISTRY[candidate_hex] = "no_collision"
                return candidate_hex

    def _register_via_api(self, hex_id: str, base_url: str) -> bool:
        """
        Attempt to register `hex_id` at the registry API.

        POST {base_url.rstrip('/')}/registry/register with JSON {"id": hex_id}.
        Returns True if the API reserved the id (registered == True).
        Uses `requests` if available, otherwise falls back to `urllib`.
        """
        import json
        import urllib.request
        from urllib.error import URLError, HTTPError

        url = base_url.rstrip("/") + "/registry/register"

        # Prefer requests if installed
        try:
            import requests
            resp = requests.post(url, json={"id": hex_id}, timeout=5)
            if resp.status_code != 200:
                return False
            data = resp.json()
            return bool(data.get("registered"))
        except Exception:
            # Fallback to stdlib
            try:
                payload = json.dumps({"id": hex_id}).encode()
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    resp = json.load(r)
                    return bool(resp.get("registered"))
            except (URLError, HTTPError, Exception):
                return False



"""
API
"""

app = Flask(__name__)

gen = UUUUIDGenerator()

@app.route('/uuuuid', methods=['GET'])
def get_uuuuid():
    return jsonify({"uuuuid": gen.generate_uuuuid()})

@app.route('/registry/register', methods=['POST'])
def registry_register():
    data = request.get_json(silent=True) or {}
    hex_id = data.get('id')
    if not hex_id:
        return jsonify({"registered": False, "reason": "missing id"}), 400

    with UUUUIDGenerator.REGISTRY_LOCK:
        if hex_id in UUUUIDGenerator.GLOBAL_REGISTRY:
            return jsonify({"registered": False, "reason": "exists"}), 200
        UUUUIDGenerator.GLOBAL_REGISTRY[hex_id] = "registered_via_api"
        return jsonify({"registered": True}), 200


@app.route('/registry/<hex_id>', methods=['GET'])
def registry_check(hex_id):
    return jsonify({"exists": hex_id in UUUUIDGenerator.GLOBAL_REGISTRY})

@app.route('/registry', methods=['GET'])
def registry_status():
    return jsonify({
        "entries": len(UUUUIDGenerator.GLOBAL_REGISTRY)
    })



"""
Run
"""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UUUUID generator / server")
    parser.add_argument("--serve", action="store_true", help="Run HTTP API server (Flask)")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the server")
    parser.add_argument("--port", type=int, default=5000, help="Port for the server")
    parser.add_argument("--count", type=int, default=1, help="How many uuids to generate when not serving")
    args = parser.parse_args()

    if args.serve:
        # Run the Flask server so other instances can call the API
        app.run(host=args.host, port=args.port)
    else:
        gen = UUUUIDGenerator()
        for _ in range(max(1, args.count)):
            print(gen.generate_uuuuid())
        print("")
        print("number of bits:", UUUUIDGenerator._OUTPUT_BYTES * 8)



"""
Congratulations! Your odds of collision are now
10^-2466 (based on the birthday problem approximation).

But sadly, not undeniably, undoubtedly, universally zero.
"""