Feature: User access

  Background:
    Given "admin" as the persona

  Scenario: Log in
    When I visit "staff/"
    And I fill in "username" with "$username"
    And I fill in "password" with "$password"
    And I press "Log in"
    Then the browser's URL should be "staff/courts"
    And I should see "Log out"