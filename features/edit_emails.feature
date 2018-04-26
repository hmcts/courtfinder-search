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
    When I visit "/staff/court/1/add_email"
    When I select "Fine queries" from "id_description"
    And I fill in "address" with "Testing address"
    And I press "Save"
    And I view court in the new window
    Then I should see "Fine queries"

  Scenario: Delete existing email
    When I remove the first form instance
    And I press "Update"
    And I view court in the new window
    Then I should not see "Defendants"

  Scenario: Attempt duplicate email
    When I visit "/staff/court/1/add_email"
    And I select "Fine queries" from "id_description"
    And I fill in "address" with "Testing address"
    And I press "Save"
    Then I should see "Court already has this contact type listed"

  Scenario: No address validation for existing email
    When I clear field "form-0-address"
    And I press "Update"
    Then I should see "This field is required"

  Scenario: No address validation for new email
    When I visit "/staff/court/1/add_email"
    And I select "Fine queries" from "id_description"
    And I press "Save"
    Then "address" should be marked as required