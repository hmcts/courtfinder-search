Feature: Edit opening times for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/opening_times"

  Scenario: Update existing opening
    When I select "Counter open" from "id_form-0-type"
    And I fill in "form-0-hours" with "5am - 5pm"
    And I press "Update"
    And I view court in the new window
    Then I should see "Counter open: 5am - 5pm"

  Scenario: Add new opening
    When I select "Office open" from "id_form-1-type"
    And I fill in "form-1-hours" with "1pm onwards"
    And I press "Update"
    And I view court in the new window
    Then I should see "Office open: 1pm onwards"

  Scenario: Delete existing opening
    When I check "form-1-DELETE"
    And I press "Update"
    And I view court in the new window
    Then I should not see "Office open: 1pm onwards"