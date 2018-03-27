Feature: Edit facilities for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/facility"

  Scenario: Update existing facility
    When I select "Security arch" from "id_form-6-name"
    And I fill in rich editor "form-6-description" with "Test fac description"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test fac description"

  Scenario: Add new facility
    When I select "Disabled toilet" from "id_form-7-name"
    And I fill in rich editor "form-7-description" with "Test new fac description"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test new fac description"

  Scenario: Delete existing facility
    When I check "form-7-DELETE"
    And I press "Update"
    And I view court in the new window
    Then I should not see "Test new fac description"