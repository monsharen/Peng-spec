@intent-feature-001 @parent:intent-root @status:draft
Feature: Example Feature 1

  Denna feature finns för att visa hur en Gherkin-spec skrivs
  i intent integrity chain-formatet. Ersätt denna text med en
  förklaring av VARFÖR featuren behövs – vilken nytta den ger
  användaren eller systemet.

  Varje scenario nedan specificerar ett konkret beteende som
  implementationen i Peng-repot måste uppfylla.

  Scenario: Basic happy path
    Given a precondition is met
    When the user performs an action
    Then the expected outcome occurs

  Scenario: Edge case handling
    Given a precondition is met
    And an unusual condition exists
    When the user performs an action
    Then the system handles it gracefully
    And an appropriate message is returned
