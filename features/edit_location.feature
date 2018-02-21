Feature: Editing court location

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/location"

  Scenario: Edit local information
    And I fill in "directions" with "Testing location information"
    And I press "Update"
    When I view court in the new window
    Then I should see "Testing location information"
