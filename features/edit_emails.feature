Feature: Edit emails for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/email"

  Scenario: Update existing email
    When I fill in "form-0-description" with "Test email"
    And I fill in "form-0-address" with "Testing address"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test email"
    And I should see "Testing address"

  Scenario: Add new email
    When I fill in "form-1-description" with "Test new email"
    And I fill in "form-1-address" with "Testing address"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test new email"

  Scenario: Delete existing email
    When I check "form-0-DELETE"
    And I press "Update"
    And I view court in the new window
    Then I should not see "Test email"