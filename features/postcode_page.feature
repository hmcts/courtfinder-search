

Feature: Postcode page

  Background: Navigating to the postcode page
    Given I visit the postcode page

  Scenario: Displays header
    Then I should see the enter postcode header

  Scenario: An invalid postcode
    When I enter an invalid postcode
    Then I should see postcode error message

  Scenario: A full valid postcode
    When I enter a full valid postcode
    Then I should see results for that postcode

  Scenario: The first half of a valid postcode
    When I enter a first half of a valid postcode
    Then I should see results for the first half of the postcode
