Feature: Edit contacts for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/contact"

  Scenario: Update existing contact
    When I fill in "form-0-name" with "Test contact"
    And I fill in "form-0-number" with "077777"
    And I fill in "form-0-explanation" with "Testing explanation"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test contact"
    And I should see "077777"
    And I should see "Testing explanation"

  Scenario: Add new contact
    When I fill in "form-5-name" with "Test new contact"
    And I fill in "form-5-number" with "077777"
    And I fill in "form-5-explanation" with "Testing explanation"
    And I press "Update"
    And I view court in the new window
    Then I should see "Test new contact"

  Scenario: Delete existing contact
    When I check "form-0-DELETE"
    And I press "Update"
    And I view court in the new window
    Then I should not see "Test contact"