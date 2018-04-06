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
    When I select "Fine queries" from "id_form-5-name"
    And I fill in "form-5-number" with "077777"
    And I fill in "form-5-explanation" with "Testing explanation"
    And I press "Update"
    And I view court in the new window
    Then I should see "Fine queries"

  Scenario: Delete existing contact
    When I check "form-0-DELETE"
    And I press "Update"
    And I view court in the new window
    Then I should not see "Defendants"