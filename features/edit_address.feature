Feature: Edit addresses for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/address"

  Scenario: Update primary address
    When I fill "town_name" with "Kendal" in the form "primary_address"
    And I press "Update" in the form "primary_address"
    And I view court in the new window
    Then I should see "Kendal"

  Scenario: Add new secondary address
    When I fill "address" with "London Magistrates Court" in the form "secondary_address"
    And I select "Postal" from "address_type" in the form "secondary_address"
    And I fill "postcode" with "sw1 3rd" in the form "secondary_address"
    And I fill "town_name" with "Aberdeen" in the form "secondary_address"
    And I press "Update" in the form "secondary_address"
    And I view court in the new window
    Then I should see "London Magistrates Court"
    And I should see "Write to us:"
    And I should see "Aberdeen"

  Scenario: Delete secondary address
    When I press "Delete" in the form "secondary_delete"
    And I view court in the new window
    Then I should not see "London Magistrates Court"
    And I should not see "Write to us:"
