#!/usr/bin/env bash
set -euo pipefail

# Creates the monsharen/Peng repo on GitHub and populates it
# with the template files from peng-repo-template/.
#
# Prerequisites:
#   - gh CLI installed and authenticated (gh auth login)
#   - Run from the root of the peng-spec repo
#
# Usage:
#   ./setup-peng-repo.sh

OWNER="monsharen"
REPO="Peng"
FULL="${OWNER}/${REPO}"

echo "=== Setting up ${FULL} ==="

# 1. Create repo on GitHub
if gh repo view "${FULL}" &>/dev/null; then
  echo "Repo ${FULL} already exists, skipping creation"
else
  echo "Creating ${FULL} on GitHub..."
  gh repo create "${FULL}" --public \
    --description "Peng – spec-driven implementation (see ${OWNER}/Peng-spec)"
fi

# 2. Clone and populate
TMPDIR=$(mktemp -d)
echo "Cloning into ${TMPDIR}..."
gh repo clone "${FULL}" "${TMPDIR}/${REPO}"
cd "${TMPDIR}/${REPO}"

# Copy template files
cp -r "${OLDPWD}/peng-repo-template/." .

# Commit and push
git add -A
git commit -m "Initial setup: spec-driven agent pipeline

- GitHub Actions workflow receiving spec-changed dispatch from peng-spec
- Claude Code agent analyzes spec diff, implements, runs Gherkin tests
- behave.ini configured to read features from sibling peng-spec checkout
- tests/steps/ ready for step definitions"

git push origin main
echo ""
echo "=== ${FULL} created and populated ==="
echo ""

# 3. Set up secrets
echo "=== Secrets setup ==="
echo ""
echo "Now set the required secrets:"
echo ""
echo "  1. ANTHROPIC_API_KEY in ${FULL} (for the Claude Code agent):"
echo "     gh secret set ANTHROPIC_API_KEY --repo ${FULL}"
echo ""
echo "  2. PENG_REPO_TOKEN in ${OWNER}/Peng-spec (PAT with repo scope):"
echo "     gh secret set PENG_REPO_TOKEN --repo ${OWNER}/Peng-spec"
echo ""

cd "${OLDPWD}"
rm -rf "${TMPDIR}"

echo "Done! The pipeline is ready."
echo "Push a .feature change to peng-spec main to trigger the agent."
