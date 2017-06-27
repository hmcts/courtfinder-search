Feature: Court location code page

  Background: Navigating to the court location code page
    Given I visit the court location code page

  Scenario: Displays header
    Then I should see the search by court location code header

  Scenario: Displays the court location code hint
    Then I should see the court location code hint

  Scenario: Search using a valid court location code
    When I search using a valid court location code
    Then I should see the results for that code

  Scenario: Search using an invalid court location code
    When I search using an invalid court location code
    Then I should see the court location code error message
