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
    And I should see "Please note that information provided for courts in England will not be available in Welsh."

  Scenario: Access Welsh court in Welsh language - no notice
    When I press "Cymraeg"
    And I visit "/courts/swansea-civil-and-family-justice-centre"
    Then I should see "Mae hwn yn wasanaeth newydd"
    And I should not see "Please note that information provided for courts in England will not be available in Welsh."

