Feature: Access the website in English and Welsh

  Background: Visit make a plea
    When I visit "/"

  Scenario: Switch between languages
    When I press "Cymraeg"
    Then I should see "Mae hwn yn wasanaeth newydd"
    When I press "English"
    Then I should see "This is a new service"

  Scenario: Access English court in Welsh language - show notice
    When I press "Cymraeg"
    And I visit "/courts/central-london-county-court"
    Then I should see "Mae hwn yn wasanaeth newydd"
   #And I should see "Please note that information provided for venues in England will not be available in Welsh."
    And I should see "Nodwch os gwelwch yn dda na fydd gwybodaeth am leoliadau yn Lloegr ar gael yn Gymraeg."

  Scenario: Access Welsh court in Welsh language - no notice
    When I press "Cymraeg"
    And I visit "/courts/swansea-civil-and-family-justice-centre"
    Then I should see "Mae hwn yn wasanaeth newydd"
   #And I should not see "Please note that information provided for venues in England will not be available in Welsh."
    And I should not see "Nodwch os gwelwch yn dda na fydd gwybodaeth am leoliadau yn Lloegr ar gael yn Gymraeg."

  Scenario: Link to Welsh content, check redirect and that the language switching still works
    When I visit "/search/results?aol=Adoption&postcode=s1+1aa"
    Then I should see "These are the 3 courts or tribunals nearest s1 1aa."
    When I visit "/cy/search/results?aol=Adoption&postcode=s1+1aa"
    Then I should see "Dyma'r 3 llys a thribiwnlys sydd agosaf at s1 1aa."
    And the browser's URL should be "/search/results?aol=Adoption&postcode=s1+1aa"
    When I press "English"
    Then I should see "These are the 3 courts or tribunals nearest s1 1aa."
