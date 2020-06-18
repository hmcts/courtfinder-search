Feature: Edit basic court information

  Background:
    Given "admin" as the persona
    And I log in to the admin interface

  Scenario: Edit basic information
    When I visit "/staff/court/1"
    And I fill in "name" with "Testing court name"
    And I fill in "alert" with "Testing urgent notice!"
    And I fill in rich editor "info" with "Testing additional information"
    And I press "Update"
    Then I should see "Editing - Testing court name"
    When I view court in the new window
    Then the browser's URL should be "/courts/gotham-crown-court"
    And I should see "Testing court name"
    And I should see "Testing urgent notice!"
    And I should see "Testing additional information"

  Scenario: Open court
    When I visit "/staff/court/2"
    And I check "displayed"
    And I press "Update"
    And I view court in the new window
    Then I should not see "This court or tribunal is no longer in service"

  Scenario: Close court
    When I visit "/staff/court/3"
    And I uncheck "displayed"
    And I press "Update"
    And I view court in the new window
    Then I should see "This court or tribunal is no longer in service"

  Scenario: Delete court
    When I visit "/staff/court/7"
    And I fill "name" with "Mayor's and City of London Court" in the form "delete-court"
    And I press "Delete court"
    Then I should see "`Mayor's and City of London Court` has been deleted"
    And I should not see an element with xpath "/table/tr/td[text()='Mayor\'s and City of London Court']"
