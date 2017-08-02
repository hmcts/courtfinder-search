Feature: Search page

  Background: Navigating to the search page
    Given I visit the search page

  Scenario: Displays header
    Then I should see the search header

  Scenario: Search by
    Then I should see area of law I am interested in is selected
    And I should see an option to search by court name or address
    And I should see an option to search by A-Z list of all courts
    And I should see an option to search by court location code

  Scenario: Next button
    Then I should see the next button
