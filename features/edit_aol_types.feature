Feature: Edit aol type

  Background:
    Given "admin" as the persona
    And I log in to the admin interface

  Scenario: Edit aol type
    When I visit "/staff/edit_aol/2"
    And I fill in "external_link" with "https://www.gov.uk/child-adoptions"
    And I press "Update"
    And I visit "/courts/aylesbury-magistrates-court-and-family-court"
    Then I should see "Adoption"

  Scenario: Set alternative aol name
    When I visit "/staff/edit_aol/4"
    And I fill in "alt_name" with "Alternative AOL name"
    And I press "Update"
    And I visit "/courts/aylesbury-magistrates-court-and-family-court"
    Then I should see "Alternative AOL name"
    Then I should not see "Divorce"
