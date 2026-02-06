# Peng Agent – Spec → Implementation

Du är en agent som implementerar ändringar i **Peng**-repot baserat på
specifikationen i **Peng-spec**-repot.

## Din uppgift

1. **Analysera spec-diff** – Läs `spec-diff.md` (genererad av CI) för att
   förstå exakt vilka features/scenarios som ändrats eller lagts till.
2. **Läs gällande features** – Läs `.feature`-filerna under `peng-spec/features/`
   för att förstå den fullständiga intentionen, inte bara diffen.
3. **Implementera i peng** – Gör de ändringar i `peng/`-repot som krävs
   för att uppfylla specen.
4. **Kör Gherkin-tester** – Kör `behave` (eller det testramverk som konfigurerats)
   med feature-filerna från peng-spec mot implementationen i peng.
5. **Skapa PR** – Om testerna passerar, committa och skapa en pull request.

## Regler

- Ändra ALDRIG filer i `peng-spec/`. Specen är din sanning.
- Läs hela feature-filen, inte bara scenario-titlarna. Texten under
  `Feature:` förklarar VARFÖR – den styr designbeslut.
- Om ett scenario är otydligt, implementera det mest rimliga beteendet
  och skriv en kommentar i koden som förklarar ditt antagande.
- Bryt inte existerande tester. Om en ändring kräver refaktorering,
  se till att alla befintliga scenarios fortfarande passerar.
- Varje commit ska referera till det intent-ID som ändrades,
  t.ex. `feat(intent-feature-003): add user login flow`.

## Filstruktur du arbetar med

```
peng-spec/                     ← READONLY – specifikationsrepot (checkout)
  peng.spec.yaml               ← Manifest med intent-träd
  features/                    ← Gherkin feature-filer
    feature-NNN-namn.feature
  agent/
    AGENT.md                   ← Denna fil
    analyze-diff.py            ← Genererar spec-diff.md

peng/                          ← DIN WORKSPACE – implementationsrepot
  src/                         ← Källkod
  tests/
    steps/                     ← Behave step definitions
      step_*.py                ← Maps Given/When/Then → implementation
  behave.ini                   ← Behave config (pekar på peng-spec/features)
```

## Testning

Gherkin-testerna i `peng-spec/features/` körs mot `peng/tests/steps/`.
Step definitions i peng mappar varje Given/When/Then till faktisk kod:

```python
# peng/tests/steps/step_example.py
from behave import given, when, then

@given('a precondition is met')
def step_precondition(context):
    context.state = setup_precondition()

@when('the user performs an action')
def step_action(context):
    context.result = perform_action(context.state)

@then('the expected outcome occurs')
def step_verify(context):
    assert context.result == expected_value
```

## Commit-format

```
feat(intent-feature-NNN): kort beskrivning

Implementerar scenarios från feature-NNN-namn.feature.
Chain hash: <hash från dispatch payload>
```
