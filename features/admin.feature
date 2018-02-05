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

  Scenario: Edit basic information, update slug with name
    When I visit "/staff/court/597"
    And I fill in "name" with "Testing court name"
    And I fill in "alert" with "Testing urgent notice!"
    And I fill in "info" with "Testing additional information"
    And I press "Update"
    Then I should see "Editing - Testing court name"
    When I view court in the new window
    Then the browser's URL should be "/courts/testing-court-name"
    And I should see "Testing court name"
    And I should see "Testing urgent notice!"
    And I should see "Testing additional information"

  Scenario: Open court
    When I visit "/staff/court/203"
    And I check "displayed"
    And I press "Update"
    And I view court in the new window
    Then I should not see "This court or tribunal is no longer in service"

  Scenario: Close court
    When I visit "/staff/court/67"
    And I uncheck "displayed"
    And I press "Update"
    And I view court in the new window
    Then I should see "This court or tribunal is no longer in service"
