Feature: Edit opening times for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/opening_times"

  Scenario: Update existing opening
    When I fill in "form-0-description" with "Test opening"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test opening"

  Scenario: Add new opening
    When I fill in "form-1-description" with "Test new opening"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test new opening"

  Scenario: Delete existing opening
    When I check "form-1-DELETE"
    And I press "Update"
    And I view court in the new window
    Then I should not see "Test new opening"