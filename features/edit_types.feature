Feature: Edit court types

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/types"

  Scenario: Edit court codes
    When I fill in "number" with "123"
    And I fill in "cci_code" with "456"
    And I fill in "magistrate_code" with "789"
    And I press "Update"
    When I view court in the new window
    Then I should see "Crown Court location code: 123" in element "addresses"
    And  I should see "County Court location code: 456" in element "addresses"
    And I should see "Magistrates' Court location code: 789" in element "addresses"
