@search_results

Feature: Search results page

  Background: Navigating to the search results page
    Given I visit the search results page

  Scenario: Displays header
    Then I should see the search results header

  Scenario: Displays number of results in that area
    Then I should see the number of results in that area

  Scenario: Displays search results content
    Then I should see court header
    And I should see court address
    And I should see document exchange
    And I should see the court location code
    And I should see a link for more details about the court
    And I should see the cases heard at this venue

  Scenario: Cases heard at this venue
    Then I should see a link for further information on Bankruptcy
    But I should not see a link for further information on Divorce



