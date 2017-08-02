Feature: Court details page

  Background: Navigating to the search results page
    Given I visit the court details page for Cannock Magistrates' Court

  Scenario: Displays header
    Then I should see Cannock Magistrates' Court

  Scenario: Displays visit us address
    Then I should see visit us address
    And I should see map and directions link

  Scenario: Displays write to us address
    Then I should see write to us address

  Scenario: Displays court location/tribunal no.
    Then I should see court location/tribunal no.

  Scenario: Displays opening hours
    Then I should see opening hours

  Scenario: Displays phone numbers
    Then I should see phone numbers:
    | phone            |
    | Enquiries:       |
    | Fine queries:    |
    | Witness service: |

  Scenario: Displays building facilities
    Then I should see building facilities:
    | facilities                                            |
    | This court has baby changing facilities.              |
    | Disabled access, toilet and parking facilities.       |
    | Guide Dogs are welcome at this court.                 |
    | This court has interview room facilities.             |
    | This court has hearing enhancement facilities.        |
    | There is free public parking at or nearby this court. |
    | A tea bar is available.                               |
    | Prison Video Link facility.                           |

  Scenario: Displays image of court or tribunal
    Then I should see image of court or tribunal

  Scenario: Displays cases heard at this venue
    Then I should see cases heard at this venue

  Scenario: Displays useful links
    Then I should see find a form
    And I should see make a complaint
