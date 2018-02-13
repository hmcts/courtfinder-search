Feature: User access

  Background:
    Given "admin" as the persona

  Scenario: Log in & out
    When I visit "staff/"
    And I fill in "username" with "$username"
    And I fill in "password" with "$password"
    And I press "Log in"
    Then the browser's URL should be "staff/courts"
    When I press "log out"
    Then I should see "You have been logged out, click here to log back in."

  Scenario: Redirect protected url to login
    When I visit "staff/courts"
    Then the browser's URL should be "staff/auth/login/"
    And I should see "Login to continue"
