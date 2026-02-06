# Peng Spec – Intent Integrity Chain

Specifikationsrepo för **Peng**. Använder en *intent integrity chain* för att
säkerställa spårbarhet från syfte → features → beteende → kontrakt → verifiering.

## Struktur

```
peng.spec.yaml          ← Huvudspec med hela intent-kedjan
schema/                  ← JSON Schema för validering
  intent-chain.schema.json
intents/                 ← (Valfritt) Separata intent-filer för större specs
verify-chain.py          ← Lokalt verifieringsskript
.github/workflows/
  on-spec-change.yml     ← CI: validerar + dispatchar rebuild till Peng-repo
```

## Intent-nivåer

| Nivå | Typ        | Fråga                         |
|------|------------|-------------------------------|
| 0    | Root       | VARFÖR finns Peng?            |
| 1    | Feature    | VAD ska Peng kunna?           |
| 2    | Behavior   | HUR ska det bete sig?         |
| 3    | Contract   | VILKA gränssnitt exponeras?   |

## Workflow

1. **Ändra spec** – Redigera `peng.spec.yaml` (lägg till/ändra intents)
2. **Verifiera lokalt** – `python3 verify-chain.py`
3. **Pusha** – CI validerar kedjan och beräknar chain hash
4. **Rebuild** – CI dispatchar `spec-changed` event till `monsharen/Peng`

## Lokal verifiering

```bash
pip install pyyaml
python3 verify-chain.py
```

## Agent-setup (Peng-repo)

I Peng-repot behövs en workflow som lyssnar på dispatch-eventet:

```yaml
# .github/workflows/on-spec-dispatch.yml (i Peng-repot)
name: "Build from spec"
on:
  repository_dispatch:
    types: [spec-changed]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Spec changed at ${{ github.event.client_payload.spec_sha }}"
      - run: npm install && npm run build && npm test
```

## Secrets

Skapa en GitHub Personal Access Token med `repo` scope och lägg till som
`PENG_REPO_TOKEN` i detta repos secrets (Settings → Secrets → Actions).
