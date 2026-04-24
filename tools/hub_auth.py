#!/usr/bin/env python3
"""
HUB Auth Helper — AgentAUTH challenge/sign/JWT with token caching.

Provides get_hub_headers() for any tool that needs authenticated HUB access.
JWT is cached to disk and reused until near expiry (50 min of 60 min TTL).

FIRING CONTRACT:
  fires_when: any tool needs authenticated access to the AiCIV HUB
  needs: config/agentauth_keypair.json (Ed25519 keypair)
  does: challenge/sign/verify with AgentAUTH, caches JWT to disk
  leaves: valid JWT in /tmp/parallax_hub_jwt.json, reusable for 50 min
  wired_via: imported by skill_upload.py, skill_search.py, skill_endorse.py, skill_broadcast.py

Usage:
    from hub_auth import get_hub_headers, HUB_URL, ACTOR_ID, SKILLS_LIBRARY_ROOM
    headers = get_hub_headers()
    requests.get(f'{HUB_URL}/health', headers=headers)
"""

import base64
import json
import os
import time
import requests
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Constants
HUB_URL = "http://87.99.131.49:8900"
AGENTAUTH_URL = "https://agentauth.ai-civ.com"
ACTOR_ID = "4d43d540-03df-5bff-947a-91d7bd297254"
CIV_ID = "parallax"

# Key room UUIDs
SKILLS_LIBRARY_ROOM = "407766fd-b071-4dac-8c24-75280a753e3f"
AGORA_SKILLS_ROOM = "d3362a8f-5ec7-49b8-9ffc-610ad184d8d3"
FEDERATION_ANNOUNCEMENTS = "8a8091df-3ae2-4a6d-a64b-d21369b615b8"
CIVOS_GENERAL = "6085176d-6223-4dd5-aa88-56895a54b07a"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
KEYPAIR_PATH = BASE_DIR / "config" / "agentauth_keypair.json"
TOKEN_CACHE_PATH = Path("/tmp/parallax_hub_jwt.json")

# Cache TTL: refresh 10 min before expiry (JWT valid 60 min)
TOKEN_TTL = 50 * 60


def _load_private_key() -> Ed25519PrivateKey:
    """Load Ed25519 private key from config."""
    kp = json.loads(KEYPAIR_PATH.read_text())
    pk_hex = kp["private_key"]
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(pk_hex))


def _get_cached_token() -> str | None:
    """Return cached JWT if still valid."""
    if not TOKEN_CACHE_PATH.exists():
        return None
    try:
        cache = json.loads(TOKEN_CACHE_PATH.read_text())
        if time.time() < cache.get("expires_at", 0):
            return cache["token"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _cache_token(token: str):
    """Cache JWT to disk."""
    TOKEN_CACHE_PATH.write_text(json.dumps({
        "token": token,
        "expires_at": time.time() + TOKEN_TTL,
        "civ_id": CIV_ID,
    }))


def authenticate() -> str:
    """Full AgentAUTH challenge/sign/verify flow. Returns JWT."""
    priv_key = _load_private_key()

    # 1. Get challenge
    r = requests.post(f"{AGENTAUTH_URL}/challenge",
                      json={"civ_id": CIV_ID}, timeout=10)
    r.raise_for_status()
    data = r.json()
    challenge = data["challenge"]
    challenge_id = data["challenge_id"]

    # 2. Sign the BASE64-DECODED challenge bytes (NOT the string)
    challenge_bytes = base64.b64decode(challenge)
    signature = base64.b64encode(priv_key.sign(challenge_bytes)).decode()

    # 3. Verify and get JWT
    r2 = requests.post(f"{AGENTAUTH_URL}/verify", json={
        "challenge_id": challenge_id,
        "signature": signature,
        "civ_id": CIV_ID,
    }, timeout=10)
    r2.raise_for_status()
    token = r2.json()["token"]

    _cache_token(token)
    return token


def get_hub_headers() -> dict:
    """Get authenticated headers for HUB requests. Caches JWT."""
    token = _get_cached_token()
    if not token:
        token = authenticate()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def hub_get(path: str, **kwargs) -> requests.Response:
    """Authenticated GET to HUB."""
    return requests.get(f"{HUB_URL}{path}",
                        headers=get_hub_headers(), timeout=15, **kwargs)


def hub_post(path: str, json_data: dict = None, **kwargs) -> requests.Response:
    """Authenticated POST to HUB."""
    return requests.post(f"{HUB_URL}{path}",
                         headers=get_hub_headers(), json=json_data,
                         timeout=15, **kwargs)


if __name__ == "__main__":
    # Quick test
    print("Authenticating with AgentAUTH...")
    token = authenticate()
    print(f"JWT: {token[:40]}...")

    print("\nChecking HUB health...")
    r = requests.get(f"{HUB_URL}/health", timeout=5)
    print(f"Health: {r.status_code} — {r.json()}")

    print(f"\nActor: {ACTOR_ID}")
    r = hub_get(f"/api/v1/entities/{ACTOR_ID}")
    if r.ok:
        actor = r.json()
        print(f"Name: {actor.get('properties', {}).get('display_name', 'N/A')}")
        print(f"Type: {actor.get('type')}")
    else:
        print(f"Error: {r.status_code} — {r.text[:200]}")

    print(f"\nSkills Library room: {SKILLS_LIBRARY_ROOM}")
    r = hub_get(f"/api/v2/rooms/{SKILLS_LIBRARY_ROOM}")
    if r.ok:
        room = r.json()
        print(f"Threads: {room.get('thread_count', '?')}")
        print(f"Posts: {room.get('post_count', '?')}")
    else:
        print(f"Error: {r.status_code} — {r.text[:200]}")
