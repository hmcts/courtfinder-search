Feature: Edit home page emergency message

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I press "emergency message"

  Scenario: Edit and activate emergency message
    When I fill in rich editor "message" with "Testing emergency message!"
    And I check "show"
    And I press "Update"
    Then I should see "Emergency message updated"
    When I visit "/search"
    And I should see "Special notice:"
    And I should see "Testing emergency message!"

  Scenario: Deactivate emergency message
    When I uncheck "show"
    And I press "Update"
    Then I should see "The message is now *hidden*"
    When I visit "/search"
    And I should not see "Special notice:"
    And I should not see "Testing emergency message!"
