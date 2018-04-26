Feature: Edit contacts for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/contact"

  Scenario: Update existing contact
    When I select "Defendants" from "id_form-0-name"
    And I fill in "form-0-number" with "077777"
    And I fill in "form-0-explanation" with "Testing explanation"
    And I press "Update"
    And I view court in the new window
    Then I should see "Defendants"
    And I should see "077777"
    And I should see "Testing explanation"

  Scenario: Add new contact
    When I visit "/staff/court/1/add_contact"
    And I select "Fine queries" from "id_name"
    And I fill in "number" with "077777"
    And I fill in "explanation" with "Testing explanation"
    And I press "Save"
    And I view court in the new window
    Then I should see "Fine queries"

  Scenario: Delete existing contact
    When I remove the first form instance
    And I press "Update"
    And I view court in the new window
    Then I should not see "Defendants"

  Scenario: Attempt duplicate contact
    When I visit "/staff/court/1/add_contact"
    And I select "Fine queries" from "id_name"
    And I fill in "number" with "01234"
    And I press "Save"
    Then I should see "Court already has this contact type listed"

  Scenario: No number validation for existing contact
    When I clear field "form-0-number"
    And I press "Update"
    Then I should see "This field is required"

  Scenario: No number validation for new contact
    When I visit "/staff/court/1/add_contact"
    And I select "Fine queries" from "id_name"
    And I press "Save"
    Then "number" should be marked as required