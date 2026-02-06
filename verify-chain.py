#!/usr/bin/env python3
"""
Intent Integrity Chain Verifier

Validates that the spec is internally consistent:
- All parent/child references resolve
- No orphaned intents (except root)
- No circular references
- Every non-root intent traces back to the root

Usage:
  python3 verify-chain.py [path/to/peng.spec.yaml]
"""

import hashlib
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)


def load_spec(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def verify_chain(spec: dict) -> list[str]:
    errors = []
    chain = spec.get("chain", [])
    by_id = {i["id"]: i for i in chain}
    ids = set(by_id.keys())

    # Check uniqueness
    if len(ids) != len(chain):
        seen = set()
        for i in chain:
            if i["id"] in seen:
                errors.append(f"Duplicate intent ID: {i['id']}")
            seen.add(i["id"])

    # Find roots
    roots = [i for i in chain if i.get("level") == 0]
    if not roots:
        errors.append("No root intent (level 0) found")

    for intent in chain:
        iid = intent["id"]

        # Validate parent references
        parent = intent.get("parent")
        if parent and parent not in ids:
            errors.append(f"{iid}: parent '{parent}' does not exist")

        # Validate child references
        for child in intent.get("children", []):
            if child not in ids:
                errors.append(f"{iid}: child '{child}' does not exist")
            elif by_id[child].get("parent") != iid:
                errors.append(
                    f"{iid}: child '{child}' does not reference back as parent"
                )

        # Validate contract references
        for contract in intent.get("contracts", []):
            if contract not in ids:
                errors.append(f"{iid}: contract '{contract}' does not exist")

        # Check non-root has parent
        if intent.get("level", 0) > 0 and not parent:
            errors.append(f"{iid}: non-root intent missing parent")

    # Check for circular references
    def trace_to_root(iid, visited=None):
        if visited is None:
            visited = set()
        if iid in visited:
            return False  # cycle
        visited.add(iid)
        intent = by_id.get(iid)
        if not intent:
            return False
        if intent.get("level") == 0:
            return True
        parent = intent.get("parent")
        if not parent:
            return False
        return trace_to_root(parent, visited)

    for intent in chain:
        if intent.get("level", 0) > 0:
            if not trace_to_root(intent["id"]):
                errors.append(
                    f"{intent['id']}: cannot trace back to root (cycle or broken chain)"
                )

    return errors


def compute_chain_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else "peng.spec.yaml"

    if not Path(spec_path).exists():
        print(f"Spec file not found: {spec_path}")
        sys.exit(1)

    spec = load_spec(spec_path)
    errors = verify_chain(spec)

    chain_hash = compute_chain_hash(spec_path)
    stored_hash = spec.get("integrity", {}).get("chain_hash")

    print(f"Spec: {spec.get('spec_name', '?')} v{spec.get('version', '?')}")
    print(f"Intents: {len(spec.get('chain', []))}")
    print(f"Chain hash: {chain_hash}")

    if stored_hash and stored_hash != "PENDING" and stored_hash != chain_hash:
        print(f"WARNING: Stored hash mismatch (stored: {stored_hash})")
        print("  → Spec has changed since last verification")

    if errors:
        print(f"\nFAILED – {len(errors)} error(s):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("\nIntent chain integrity: OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
