Feature: Area of law page

  Background: Navigating to the area of law page
    Given I visit the area of law page

  Scenario: Displays header
    Then I should see about your issue header

  Scenario: Displays issues
    Then I should see issues:
    | issue name                     |
    | Adoption:                      |
    | Bankruptcy:                    |
    | Children:                      |
    | Civil partnership:             |
    | Crime:                         |
    | Divorce:                       |
    | Domestic violence:             |
    | Employment:                    |
    | Forced marriage and FGM:       |
    | High Court District Registry:  |
    | Housing possession:            |
    | Immigration:                   |
    | Money claims:                  |
    | Probate:                       |
    | Social security:               |
    | None of the above or not sure: |
   And each issue should have a description
   And none of the above is selected by default

  Scenario: Continue button
    Then I should see the continue button

