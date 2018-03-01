Feature: Manage users

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/users"

  Scenario: Add a new user
    When I press "add new user"
    And I fill in "username" with "testuser1"
    And I fill in "first_name" with "John"
    And I fill in "last_name" with "Smith"
    And I fill in "email" with "john@example.com"
    And I fill in "password1" with "letmein123"
    And I fill in "password2" with "letmein123"
    And I press "Add user"
    Then I should see "`testuser1` has been added"
    And I should see "testuser1 John Smith john@example.com"

  Scenario: Edit user
    When I click the link to "/staff/users/edit/editme"
    And I fill in "username" with "editme-changed"
    And I fill in "first_name" with "first-changed"
    And I fill in "last_name" with "last-changed"
    And I fill in "email" with "email.changed@example.com"
    And I check "is_superuser"
    And I press "Update"
    Then I should see "`editme-changed` has been updated"
    When I visit "/staff/users"
    And I should see "editme-changed first-changed last-changed email.changed@example.com"

  Scenario: Change user's password
    When I click the link to "/staff/users/edit/editpass"
    And I press "Change password"
    And I fill in "password1" with "letmein123"
    And I fill in "password2" with "letmein123"
    And I press "Change password"
    Then I should see "`editpass` password has been updated"
    When I press "log out"
    And I visit "staff/auth/login/"
    And I fill in "username" with "editpass"
    And I fill in "password" with "letmein123"
    And I press "Log in"
    Then the browser's URL should be "/staff/courts"

  Scenario: Delete user
    When I click the link to "/staff/users/edit/deleteme"
    And I fill "username" with "deleteme" in the form "delete-user"
    And I press "Delete user"
    Then I should see "`deleteme` has been deleted"
    And I should not see "deleteme test test test@example.com"
