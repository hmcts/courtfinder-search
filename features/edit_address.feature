Feature: Edit addresses for a given court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/address"

  Scenario: Update primary address
    When I select "72" from "town" in the form "primary_address"
    And I press "Update" in the form "primary_address"
    Then I should see "Kendal (Cumbria)"

  Scenario: Add new secondary address
    When I fill "address" with "London Magistrates Court" in the form "secondary_address"
    And I select "2" from "address_type" in the form "secondary_address"
    And I fill "postcode" with "sw1 3rd" in the form "secondary_address"
    And I select "57" from "town" in the form "secondary_address"
    And I press "Update" in the form "secondary_address"
    Then I should see "London Magistrates Court"
    And I should see "Postal"
    And I should see "Aberdeen (Aberdeenshire)"

  Scenario: Delete secondary address
    When I press "Delete" in the form "secondary_delete"
    Then I should not see "London Magistrates Court"