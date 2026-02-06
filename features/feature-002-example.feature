@intent-feature-002 @parent:intent-root @status:draft
Feature: Example Feature 2

  Denna feature finns för att visa att specifikationen kan
  innehålla flera feature-filer som alla kopplas tillbaka
  till root-intentet via sin @parent-tagg.

  Ersätt denna text med en förklaring av varför just denna
  feature behövs och vad den löser.

  Background:
    Given the system is initialized

  Scenario: Standard operation
    When the user triggers the feature
    Then the system responds correctly

  Scenario Outline: Parameterized behavior
    When the user provides <input>
    Then the system returns <output>

    Examples:
      | input   | output   |
      | value-a | result-a |
      | value-b | result-b |
