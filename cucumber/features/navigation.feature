Feature: Navigation

  Background: Navigating to the search results page
    Given I visit the search results page

  Scenario: Use header to navigate to gov.uk
    Then I see I can navigate to gov.uk

  Scenario: Use header to navigate to court and tribunal finder
    Then I see I can navigate to court and tribunal finder

  Scenario: Breadcrumb navigation
    Then I see I can use breadcrumbs to navigate to home
    And to find a court or tribunal
    And to about your issue
    And to search by postcode

  Scenario: BETA
    Then I see I can find out more about BETA

  Scenario: Your feedback
    Then I see I can give feedback