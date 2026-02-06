# Peng Spec – Intent Integrity Chain (Gherkin)

Specifikationsrepo för **Peng**. Specs skrivs i Gherkin-format, organiserade
per feature. En intent integrity chain kopplar ihop allt från syfte ner till
testbara scenarios – och triggar automatiskt rebuild av Peng-repot vid ändringar.

## Struktur

```
peng.spec.yaml                    ← Manifest: intent-träd + build-config
features/
  feature-001-example.feature     ← Gherkin-spec med förklaring + scenarios
  feature-002-example.feature
schema/
  intent-chain.schema.json        ← JSON Schema för manifestet
verify-chain.py                   ← Lokal verifiering av kedjan
.github/workflows/
  on-spec-change.yml              ← CI: validera + dispatcha rebuild
```

## Hur en feature-fil ser ut

```gherkin
@intent-feature-001 @parent:intent-root @status:draft
Feature: Kortfattat namn

  Här skriver du VARFÖR denna feature finns. Vilken nytta
  ger den? Vilket problem löser den? Denna text är kärnan
  i intent integrity chain – den förklarar avsikten.

  Scenario: Happy path
    Given a precondition
    When the user does something
    Then the expected thing happens

  Scenario: Edge case
    Given an unusual state
    When the user does something
    Then the system handles it gracefully
```

**Taggar** (rad 1) kopplar filen till manifestet:
- `@intent-feature-NNN` – intent-ID (måste matcha `peng.spec.yaml`)
- `@parent:intent-root` – vilken parent i kedjan
- `@status:draft` – `draft` → `proposed` → `accepted` → `implemented` → `verified`

## Workflow

1. **Skapa/ändra** en `.feature`-fil under `features/`
2. **Registrera** den i `peng.spec.yaml` under `intents:`
3. **Verifiera** lokalt: `python3 verify-chain.py`
4. **Push till main** → CI validerar + dispatchar `spec-changed` till Peng-repot

## Lokal verifiering

```bash
pip install pyyaml
python3 verify-chain.py
```

## Lägga till en ny feature

1. Skapa `features/feature-NNN-namn.feature` med taggar + Gherkin
2. Lägg till i `peng.spec.yaml`:
   ```yaml
   intents:
     intent-feature-NNN:
       file: features/feature-NNN-namn.feature
       parent: intent-root
       children: []
   ```
3. Lägg till `intent-feature-NNN` i parentens `children`-lista
4. Kör `python3 verify-chain.py` för att säkerställa att kedjan hänger ihop

## Agent-setup (Peng-repo)

Lägg till denna workflow i Peng-repot för att fånga dispatch-eventet:

```yaml
# .github/workflows/on-spec-dispatch.yml
name: "Build from spec"
on:
  repository_dispatch:
    types: [spec-changed]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Spec changed – hash ${{ github.event.client_payload.chain_hash }}"
      - run: npm install && npm run build && npm test
```

## Secrets

Skapa en GitHub Personal Access Token med `repo`-scope och lägg till som
`PENG_REPO_TOKEN` i peng-spec-repots secrets (Settings → Secrets → Actions).
