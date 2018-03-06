Feature: Edit areas of law

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/1/areas_of_law"

  Scenario: Add areas of law
    When I check box with label "Adoption"
    When I check box with label "Employment"
    And I press "Update"
    When I view court in the new window
    Then I should see "Adoption" in section "Cases heard at this venue"
    And I should see "Employment" in section "Cases heard at this venue"

  Scenario: Remove areas of law
    When I uncheck box with label "Crime"
    And I press "Update"
    When I view court in the new window
    Then I should not see "Crime" in section "Cases heard at this venue"

  Scenario: Hide areas of law
    When I check "hide_aols"
    And I press "Update"
    When I view court in the new window
    Then I should not see "Cases heard at this venue"

