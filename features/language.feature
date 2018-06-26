Feature: Access the website in English and Welsh

  Background: Visit make a plea
    When I visit "/"

  Scenario: Switch between languages
    When I press "Cymraeg"
    Then I should see "Mae hwn yn wasanaeth newydd"
    When I press "English"
    Then I should see "This is a new service"
