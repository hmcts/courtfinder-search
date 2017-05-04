Feature: Area of law page

  Background: Navigating to the area of law page
    Given I visit the area of law page

  Scenario: Displays header
    Then I should see about your issue header

  Scenario: Displays issues
    Then I should see issues:
    | issue name                     |
    | Bankruptcy:                    |
    | Children:                      |
    | Crime:                         |
    | Divorce:                       |
    | Employment:                    |
    | Immigration:                   |
    | Money claims:                  |
    | Social security:               |
    | None of the above or not sure: |
   And each issue should have a description
   And none of the above is selected by default

  Scenario: Continue button
    Then I should see the continue button

