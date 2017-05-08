Feature: Name or Address page

  Background: Navigating to the name or address page
    Given I visit the name or address page

  Scenario: Displays header
    Then I should see the search by name or address header

  Scenario: Displays form hint
    Then I should see the hint for the form

  Scenario: Search by court or tribunal name
    When I search for 'East London Family Court'
    Then I should see the result is 'East London Family Court'

  Scenario: Search by building name
    When I search for 'Gloucester House'
    Then I should see the result is 'West London Family Court'

  Scenario: Search by street name
    When I search for 'Westferry Circus'
    Then I should see the result is 'East London Family Court'

  Scenario: Search by city
    When I search for 'Liverpool'
    Then I should see the top result is Liverpool Civil and Family Court

  Scenario: Nothing is entered
    When I search for ''
    Then I should see 'You did not enter a search term' error message

  Scenario: Random text is entered
    When I search for 'sgava'
    Then I should see 'Sorry, there are no results for sgava.' error message
