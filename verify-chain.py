#!/usr/bin/env python3
"""
Intent Integrity Chain Verifier (Gherkin edition)

Validates that the spec manifest and .feature files are consistent:
- Every intent in the manifest that has a file → file exists
- Every .feature file has @<intent-id> and @parent:<id> tags
- Tags in .feature files match what the manifest declares
- All parent references resolve and trace back to root
- No orphaned or circular references
- Every .feature file contains at least one Scenario

Usage:
  python3 verify-chain.py [path/to/peng.spec.yaml]
"""

import hashlib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)


TAG_PATTERN = re.compile(r"@([\w:.-]+)")
SCENARIO_PATTERN = re.compile(r"^\s*(Scenario|Scenario Outline):", re.MULTILINE)


def load_spec(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def parse_feature_tags(feature_path: Path) -> dict:
    """Extract tags and metadata from a .feature file."""
    text = feature_path.read_text()
    lines = text.strip().splitlines()

    # Tags are on lines before the Feature: keyword
    tag_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@"):
            tag_lines.append(stripped)
        elif stripped.startswith("Feature:"):
            break
        elif stripped == "":
            continue
        else:
            break

    all_tags = []
    for tl in tag_lines:
        all_tags.extend(TAG_PATTERN.findall(tl))

    intent_id = None
    parent_id = None
    status = None

    for tag in all_tags:
        if tag.startswith("parent:"):
            parent_id = tag.split(":", 1)[1]
        elif tag.startswith("status:"):
            status = tag.split(":", 1)[1]
        elif tag.startswith("intent-"):
            intent_id = tag

    scenario_count = len(SCENARIO_PATTERN.findall(text))

    # Extract Feature: line for title
    feature_title = None
    for line in lines:
        if line.strip().startswith("Feature:"):
            feature_title = line.strip().replace("Feature:", "").strip()
            break

    return {
        "intent_id": intent_id,
        "parent_id": parent_id,
        "status": status,
        "scenario_count": scenario_count,
        "feature_title": feature_title,
        "all_tags": all_tags,
    }


def verify_chain(spec: dict, spec_dir: Path) -> list[str]:
    errors = []
    intents = spec.get("intents", {})

    if not intents:
        errors.append("No intents defined in manifest")
        return errors

    # Find root(s): intents without a parent key
    roots = [iid for iid, data in intents.items() if "parent" not in data]
    if not roots:
        errors.append("No root intent found (an intent without 'parent')")

    # Validate each intent
    for iid, data in intents.items():
        parent = data.get("parent")

        # Check parent exists
        if parent and parent not in intents:
            errors.append(f"{iid}: parent '{parent}' not in manifest")

        # Check children exist
        for child in data.get("children", []):
            if child not in intents:
                errors.append(f"{iid}: child '{child}' not in manifest")
            elif intents[child].get("parent") != iid:
                errors.append(
                    f"{iid}: child '{child}' has parent "
                    f"'{intents[child].get('parent')}', expected '{iid}'"
                )

        # If intent has a file, validate it
        feature_file = data.get("file")
        if feature_file:
            fpath = spec_dir / feature_file
            if not fpath.exists():
                errors.append(f"{iid}: feature file not found: {feature_file}")
                continue

            tags = parse_feature_tags(fpath)

            # Intent ID tag must match
            if tags["intent_id"] != iid:
                errors.append(
                    f"{iid}: file {feature_file} has @{tags['intent_id']}, "
                    f"expected @{iid}"
                )

            # Parent tag must match
            if parent and tags["parent_id"] != parent:
                errors.append(
                    f"{iid}: file {feature_file} has @parent:{tags['parent_id']}, "
                    f"expected @parent:{parent}"
                )

            # Must have at least one scenario
            if tags["scenario_count"] == 0:
                errors.append(
                    f"{iid}: file {feature_file} has no Scenario definitions"
                )

    # Check for cycles – every non-root must trace to a root
    def trace_to_root(iid, visited=None):
        if visited is None:
            visited = set()
        if iid in visited:
            return False
        visited.add(iid)
        if iid not in intents:
            return False
        if "parent" not in intents[iid]:
            return True  # is a root
        return trace_to_root(intents[iid]["parent"], visited)

    for iid in intents:
        if "parent" in intents[iid]:
            if not trace_to_root(iid):
                errors.append(f"{iid}: cannot trace to root (cycle or broken chain)")

    return errors


def compute_chain_hash(spec_dir: Path, spec: dict) -> str:
    """Hash the manifest + all referenced feature files."""
    h = hashlib.sha256()
    # Include manifest
    manifest_path = spec_dir / "peng.spec.yaml"
    h.update(manifest_path.read_bytes())
    # Include all feature files in sorted order
    for iid in sorted(spec.get("intents", {})):
        fpath = spec.get("intents", {})[iid].get("file")
        if fpath:
            full = spec_dir / fpath
            if full.exists():
                h.update(full.read_bytes())
    return h.hexdigest()


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else "peng.spec.yaml"
    spec_dir = Path(spec_path).parent

    if not Path(spec_path).exists():
        print(f"Spec file not found: {spec_path}")
        sys.exit(1)

    spec = load_spec(spec_path)
    errors = verify_chain(spec, spec_dir)

    intents = spec.get("intents", {})
    feature_intents = [i for i, d in intents.items() if d.get("file")]
    chain_hash = compute_chain_hash(spec_dir, spec)
    stored_hash = spec.get("integrity", {}).get("chain_hash")

    print(f"Spec: {spec.get('spec_name', '?')} v{spec.get('version', '?')}")
    print(f"Intents: {len(intents)} ({len(feature_intents)} with feature files)")
    print(f"Chain hash: {chain_hash}")

    # List features
    for iid, data in intents.items():
        fpath = data.get("file")
        if fpath and (spec_dir / fpath).exists():
            tags = parse_feature_tags(spec_dir / fpath)
            status = tags.get("status", "?")
            scenarios = tags.get("scenario_count", 0)
            title = tags.get("feature_title", "?")
            print(f"  {iid}: {title} [{status}] ({scenarios} scenarios)")

    if stored_hash and stored_hash not in ("PENDING", chain_hash):
        print(f"\nWARNING: Stored hash mismatch (stored: {stored_hash})")
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
