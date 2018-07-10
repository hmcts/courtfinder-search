Feature: Enable welsh fields for court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/4"
    And I check "welsh_enabled"
    And I press "Update"

  Scenario: welsh fields show on edit basic info page
    When I visit "/staff/court/4"
    Then I should see "Urgent notice (Welsh)"
    And I should see "Additional information (Welsh)"

  Scenario: welsh fields show on edit location page
    When I visit "/staff/court/4/location"
    Then I should see "Local Information (Welsh)"

  Scenario: welsh fields show on edit contact page
    When I visit "/staff/court/4/contact"
    Then I should see "Explanation (Welsh)"

  Scenario: welsh fields show on add contact page
    When I visit "/staff/court/4/add_contact"
    Then I should see "Explanation (Welsh)"

  Scenario: welsh fields show on edit email page
    When I visit "/staff/court/4/email"
    Then I should see "Explanation (Welsh)"

  Scenario: welsh fields show on add email page
    When I visit "/staff/court/4/add_email"
    Then I should see "Explanation (Welsh)"

  Scenario: welsh fields show on edit facilities page
    When I visit "/staff/court/4/facility"
    Then I should see "Description (Welsh)"

  Scenario: welsh fields show on add facilities page
    When I visit "/staff/court/4/add_facility"
    Then I should see "Description (Welsh)"

  Scenario: welsh fields show on edit leaflets page
    When I visit "/staff/court/4/leaflets"
    Then I should see "Information leaflet (Welsh)"
    Then I should see "Defence witness leaflet (Welsh)"
    Then I should see "Prosecution witness leaflet (Welsh)"
