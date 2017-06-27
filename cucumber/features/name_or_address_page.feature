Feature: Search by name or Address page

  Background: Navigating to the search by name or address page
    Given I visit the search by name or address page

  Scenario: Displays header
    Then I should see the search by name or address header

  Scenario: Displays form hint
    Then I should see the hint for the form

  Scenario: Search by court or tribunal name
    When I search for 'Manchester County Court'
    Then I should see the result is Manchester County Court

  Scenario: Search by building name
    When I search for 'Manchester Civil and Family Justice Centre'
    Then I should see the result is Manchester County Court

  Scenario: Search by street name
    When I search for '1 Bridge Street West'
    Then I should see the result is Manchester County Court

  # TODO: Need better test data so we have a list of courts for a city
  Scenario: Search by city
    When I search for 'Manchester'
    Then I should see the top result Manchester Civil and Family Justice Centre

  Scenario: Nothing is entered
    When I search for ''
    Then I should see 'You did not enter a search term' error message

  Scenario: Random text is entered
    When I search for 'sgava'
    Then I should see 'Sorry, there are no results for sgava.' error message
