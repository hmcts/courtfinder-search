Feature: List of courts

  Background:
    Given "admin" as the persona
    And I log in to the admin interface

  Scenario: View court in new tab
    When I visit "staff/courts"
    Then I should see "Aberystwyth Justice Centre"
    When I click the link to "/courts/aberystwyth-justice-centre"
    And I switch to the new window
    Then I should see "Opening hours"
    And I should see "Building facilities"

  Scenario: Find court to edit
    When I visit "staff/courts"
    Then I should see "Aberystwyth Justice Centre"
    When I click the link to "/staff/court/608"
    Then I should see "Editing - Aberystwyth Justice Centre"

