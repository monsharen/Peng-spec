# Peng Spec – Intent Integrity Chain (Gherkin)

Specifikationsrepo för **Peng**. Specs skrivs i Gherkin-format, organiserade
per feature. En intent integrity chain kopplar ihop allt från syfte ner till
testbara scenarios – och en agent implementerar automatiskt ändringarna i
[Peng](https://github.com/monsharen/Peng)-repot.

## Pipeline

```
 peng-spec (detta repo)                    peng (implementation)
 ──────────────────────                    ─────────────────────
 1. Du ändrar .feature-filer
 2. Push till main
 3. CI validerar intent chain
 4. CI dispatchar spec-changed ──────────► 5. Agent väcks
                                           6. Analyserar spec-diff
                                           7. Implementerar ändringar
                                           8. Kör Gherkin-tester ◄── features/
                                           9. Skapar PR om tester passerar
```

## Struktur

```
peng.spec.yaml                    ← Manifest: intent-träd + build-config
features/
  feature-001-example.feature     ← Gherkin: taggar + förklaring + scenarios
  feature-002-example.feature
agent/
  AGENT.md                        ← Instruktioner som agenten följer
  analyze-diff.py                 ← Analyserar vilka features som ändrats
schema/
  intent-chain.schema.json        ← JSON Schema för manifestet
verify-chain.py                   ← Lokal verifiering av kedjan
peng-repo-template/               ← Filer att kopiera till peng-repot
  .github/workflows/
    on-spec-dispatch.yml          ← Tar emot dispatch, kör agent + tester
  CLAUDE.md                       ← Agent-kontext för peng-repot
  behave.ini                      ← Testrunnerkonfig
  tests/steps/                    ← Step definitions (Given/When/Then → kod)
```

## Hur en feature-fil ser ut

```gherkin
@intent-feature-001 @parent:intent-root @status:draft
Feature: Kortfattat namn

  Här skrivs VARFÖR denna feature finns. Vilken nytta
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
4. **Push till main** → CI validerar → dispatchar till peng → agent implementerar

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
4. Kör `python3 verify-chain.py`
5. Pusha – agenten tar över

## Setup – peng-repo

1. Skapa repot `monsharen/Peng`
2. Kopiera innehållet i `peng-repo-template/` till repot
3. Lägg till secrets i **peng-repot**:
   - `ANTHROPIC_API_KEY` – för Claude Code-agenten
4. Lägg till secrets i **peng-spec-repot**:
   - `PENG_REPO_TOKEN` – GitHub PAT med `repo` scope

## Lokal verifiering

```bash
pip install pyyaml
python3 verify-chain.py
```

## Lokal testning (i peng-repot)

```bash
pip install behave
behave ../peng-spec/features/
```
