#!/usr/bin/env python3
"""
Analyze what changed in peng-spec between two commits.

Produces a structured spec-diff.md that the agent reads to understand
what needs to be implemented or updated in the peng repo.

Usage:
  python3 analyze-diff.py <before-sha> <after-sha> [spec-dir]

Output:
  Writes spec-diff.md to current directory.
"""

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml")
    sys.exit(1)


def git_diff_names(before: str, after: str, cwd: str) -> list[str]:
    """Get list of changed files between two commits."""
    result = subprocess.run(
        ["git", "diff", "--name-only", before, after],
        capture_output=True, text=True, cwd=cwd,
    )
    return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]


def git_diff_content(before: str, after: str, filepath: str, cwd: str) -> str:
    """Get unified diff for a specific file."""
    result = subprocess.run(
        ["git", "diff", before, after, "--", filepath],
        capture_output=True, text=True, cwd=cwd,
    )
    return result.stdout


def parse_feature_file(path: Path) -> dict:
    """Extract metadata from a .feature file."""
    if not path.exists():
        return {"exists": False}

    text = path.read_text()
    tags = re.findall(r"@([\w:.-]+)", text.split("\n")[0] if text else "")

    intent_id = None
    status = None
    for tag in tags:
        if tag.startswith("intent-"):
            intent_id = tag
        elif tag.startswith("status:"):
            status = tag.split(":", 1)[1]

    title = None
    for line in text.splitlines():
        if line.strip().startswith("Feature:"):
            title = line.strip().replace("Feature:", "").strip()
            break

    scenarios = re.findall(
        r"^\s*(?:Scenario|Scenario Outline):\s*(.+)$", text, re.MULTILINE
    )

    # Extract the description (text between Feature: line and first Scenario/Background)
    description = ""
    in_desc = False
    for line in text.splitlines():
        if line.strip().startswith("Feature:"):
            in_desc = True
            continue
        if in_desc:
            if re.match(r"^\s*(Scenario|Scenario Outline|Background):", line):
                break
            description += line + "\n"
    description = description.strip()

    return {
        "exists": True,
        "intent_id": intent_id,
        "status": status,
        "title": title,
        "scenarios": scenarios,
        "description": description,
    }


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <before-sha> <after-sha> [spec-dir]")
        sys.exit(1)

    before = sys.argv[1]
    after = sys.argv[2]
    spec_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    changed_files = git_diff_names(before, after, spec_dir)

    changed_features = [f for f in changed_files if f.endswith(".feature")]
    manifest_changed = "peng.spec.yaml" in changed_files

    # Load current manifest
    manifest_path = Path(spec_dir) / "peng.spec.yaml"
    spec = yaml.safe_load(manifest_path.read_text()) if manifest_path.exists() else {}
    intents = spec.get("intents", {})

    lines = []
    lines.append("# Spec Diff Analysis")
    lines.append("")
    lines.append(f"**Before:** `{before[:8]}`")
    lines.append(f"**After:** `{after[:8]}`")
    lines.append(f"**Changed files:** {len(changed_files)}")
    lines.append(f"**Changed features:** {len(changed_features)}")
    lines.append(f"**Manifest changed:** {'yes' if manifest_changed else 'no'}")
    lines.append("")

    if manifest_changed:
        lines.append("## Manifest changes")
        lines.append("")
        lines.append("The intent tree (`peng.spec.yaml`) was modified.")
        lines.append("Check for new, removed, or re-parented intents.")
        lines.append("")
        diff = git_diff_content(before, after, "peng.spec.yaml", spec_dir)
        lines.append("```diff")
        lines.append(diff)
        lines.append("```")
        lines.append("")

    if changed_features:
        lines.append("## Changed features")
        lines.append("")

        for fpath in changed_features:
            full_path = Path(spec_dir) / fpath
            meta = parse_feature_file(full_path)

            intent_id = meta.get("intent_id", "unknown")
            title = meta.get("title", fpath)
            status = meta.get("status", "?")

            lines.append(f"### {intent_id}: {title}")
            lines.append(f"- **File:** `{fpath}`")
            lines.append(f"- **Status:** {status}")

            if meta.get("description"):
                lines.append(f"- **Intent (why):**")
                for desc_line in meta["description"].splitlines():
                    lines.append(f"  {desc_line}")

            if meta.get("scenarios"):
                lines.append(f"- **Scenarios ({len(meta['scenarios'])}):**")
                for s in meta["scenarios"]:
                    lines.append(f"  - {s}")

            lines.append("")

            diff = git_diff_content(before, after, fpath, spec_dir)
            if diff:
                lines.append("**Diff:**")
                lines.append("```diff")
                lines.append(diff)
                lines.append("```")
                lines.append("")

    if not changed_features and not manifest_changed:
        lines.append("## No spec changes detected")
        lines.append("")
        lines.append("Only non-spec files were modified (docs, scripts, etc.).")
        lines.append("No implementation changes needed.")

    # Action summary
    lines.append("## Action required")
    lines.append("")
    if changed_features:
        lines.append("The agent should:")
        for fpath in changed_features:
            meta = parse_feature_file(Path(spec_dir) / fpath)
            iid = meta.get("intent_id", "?")
            for s in meta.get("scenarios", []):
                lines.append(f"- Implement/update: **{s}** ({iid})")
        lines.append("")
        lines.append(
            "After implementation, run the Gherkin tests to verify all scenarios pass."
        )
    else:
        lines.append("No implementation changes needed.")

    output = "\n".join(lines)
    out_path = Path("spec-diff.md")
    out_path.write_text(output)
    print(f"Wrote {out_path} ({len(lines)} lines)")
    print(output)


if __name__ == "__main__":
    main()
