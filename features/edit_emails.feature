Feature: Edit emails for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/email"

  Scenario: Update existing email
    When I select "Defendants" from "id_form-0-description"
    And I fill in "form-0-address" with "Testing address"
    And I press "Update"
    And I view court in the new window
    Then I should see "Defendants"
    And I should see "Testing address"

  Scenario: Add new email
    When I select "Fine queries" from "id_form-1-description"
    And I fill in "form-1-address" with "Testing address"
    And I press "Update"
    And I view court in the new window
    Then I should see "Fine queries"

  Scenario: Delete existing email
    When I remove the first form instance
    And I press "Update"
    And I view court in the new window
    Then I should not see "Defendants"