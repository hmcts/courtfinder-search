Feature: Edit aol type

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/edit_aol/2"

  Scenario: Edit aol type
    When I fill in "external_link" with "https://www.gov.uk/child-adoptions"
    And I press "Update"
    And I visit "/courts/aylesbury-magistrates-court-and-family-court"
    And I click the link with text "Adoption"
    Then the browser's URL should be "https://www.gov.uk/child-adoptions"