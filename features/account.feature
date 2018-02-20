Feature: Account

  Background:
    Given "tester" as the persona
    And I log in to the admin interface
    And I press "my account"

  Scenario: Change password
    When I fill in "old_password" with "$password"
    And I fill in "new_password1" with "newpass"
    And I fill in "new_password2" with "newpass"
    And I press "Change password"
    Then I should see "You need to log in again after changing your password."
    When I press "log in"
    And I fill in "username" with "$username"
    And I fill in "password" with "newpass"
    And I press "Log in"
    Then the browser's URL should be "/staff/courts"