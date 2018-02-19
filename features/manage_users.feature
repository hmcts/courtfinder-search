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
    And I fill in "password1" with "letmein"
    And I fill in "password2" with "letmein"
    And I press "Add user"
    Then I should see "`testuser1` has been added"
    And I should see "John Smith testuser1 john@example.com"
