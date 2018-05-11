Feature: Edit facility types list

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/facility_types"

  Scenario: Add new facility type to list
    When I visit "/staff/edit_facility_type/"
    And I fill in "name" with "Phone charging"
    And I fill in "image_description" with "mobile phone icon"
    And I press "Add"
    Then I should see "Phone charging"
    When I visit "/staff/court/1/facility"
    And I select "Phone charging" from "id_form-1-name"
    And I fill in rich editor "form-1-description" with "Phone charging offered"
    And I press "Update"
    And I view court in the new window
    Then I should see "Phone charging offered"

  Scenario: Edit facility type
    When I visit "/staff/edit_facility_type/36"
    And I fill in "name" with "Car wash"
    And I fill in "image_description" with "car wash icon"
    And I press "Update"
    Then I should see "Car wash"

  Scenario: Delete facility type
    When I visit "/staff/edit_facility_type/36"
    And I press "Delete"
    Then I should not see "Car wash"

  Scenario: Attempt to add duplicate facility type
    When I visit "/staff/edit_facility_type/"
    And I fill in "name" with "First Aid"
    And I fill in "image_description" with "medical"
    And I press "Add"
    Then I should see "This type is already listed"