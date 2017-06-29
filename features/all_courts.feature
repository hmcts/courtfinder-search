Feature: All courts page

  Background: Navigating to the all courts page
    Given I visit the all courts page

  Scenario: Displays header
    Then I should see the courts and tribunals header

  Scenario: Displays instructions
    Then I should see instructions

  Scenario: Displays A-Z navigation
    When I see the A-Z navigation
    Then I should see each letter goes to the corresponding page
