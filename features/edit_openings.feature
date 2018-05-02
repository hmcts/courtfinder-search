Feature: Edit opening times for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/opening_times"

  Scenario: Update existing opening
    When I select "Court counter closed" from "id_form-0-type"
    And I fill in "form-0-hours" with "5am - 5pm"
    And I press "Update"
    And I view court in the new window
    Then I should see "Court counter closed: 5am - 5pm"

  Scenario: Add new opening
    When I visit "/staff/court/1/add_opening_times"
    And I select "Office open" from "id_type"
    And I fill in "hours" with "1pm onwards"
    And I press "Save"
    And I view court in the new window
    Then I should see "Office open: 1pm onwards"

  Scenario: Delete existing opening
    When I remove the first form instance
    And I press "Update"
    And I view court in the new window
    Then I should not see "Counter open: 5am - 5pm"

  Scenario: No hours validation for existing opening
    When I clear field "form-0-hours"
    And I press "Update"
    Then I should see "This field is required"

  Scenario: No hours validation for new opening
    When I visit "/staff/court/1/add_opening_times"
    And I select "Fixed penalty office" from "id_type"
    And I press "Save"
    Then "hours" should be marked as required