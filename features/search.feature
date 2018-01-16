Feature: Search courts

  Background:
    When I visit "search/"

  Scenario: Area of law
    When I choose to search by "The Area of Law I am interested in (recommended)"
    And I choose "Bankrupcy" as Area of Law
    And I fill in "postcode" with "SW1A 0AA"
    And I press "Continue"
    Then I should see "These are the 10 courts or tribunals nearest SW1A 0AA."
    And I should see "Bankruptcy Court (Central London)"

  Scenario: A-Z list
    When I choose to search by "A-Z list of all courts"
    And I press "B"
    Then I should see "Names starting with B"
    And I should see "Banbury County Court"

