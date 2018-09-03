Feature: Enable welsh fields for court

  Background:
    Given "admin" as the persona
    And I log in to the admin interface
    And I visit "/staff/court/2"
    And I check "welsh_enabled"
    And I press "Update"

  Scenario: welsh fields show on edit basic info page
    When I visit "/staff/court/2"
    And I fill in "name_cy" with "welsh court name"
    And I fill in "alert" with "english alert"
    And I fill in "alert_cy" with "Welsh alert"
    And I fill in rich editor "info" with "english info"
    And I fill in rich editor "info_cy" with "Welsh info"
    And I press "Update"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "welsh court name"
    Then I should see "Welsh alert"
    And I should see "Welsh info"

  Scenario: welsh name should show on welsh court search results
    When I visit "/staff/court/2"
    And I fill in "name_cy" with "cymcourtname"
    And I press "Update"
    And I visit "search/results?q=cymcourtname"
    And I press "Cymraeg"
    Then I should see "cymcourtname"

  Scenario: welsh name should show bracketed in list results
    When I visit "/staff/court/2"
    And I fill in "name_cy" with "cymcourtname"
    And I press "Update"
    And I visit "/courts/A"
    And I press "Cymraeg"
    Then I should see "Aylesbury Magistrates' Court and Family Court (cymcourtname)"

  Scenario: welsh fields show on edit location page
    When I visit "/staff/court/2/location"
    And I fill in "directions" with "English directions"
    And I fill in "directions_cy" with "Welsh directions"
    And I press "Update"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "Welsh directions"

  Scenario: welsh contact explanation should show on welsh court page
    When I visit "/staff/court/2/contact"
    And I fill in "form-0-explanation_cy" with "Welsh explanation"
    And I press "Update"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "Welsh explanation"

  Scenario: welsh fields show on add contact page
    When I visit "/staff/court/2/add_contact"
    Then I should see "Explanation (Welsh)"

  Scenario: welsh email explanation should show on welsh court page
    When I visit "/staff/court/2/email"
    And I fill in "form-0-explanation_cy" with "Welsh email exp"
    And I press "Update"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "Welsh email exp"

  Scenario: welsh fields show on add email page
    When I visit "/staff/court/2/add_email"
    Then I should see "Explanation (Welsh)"

  Scenario: welsh facility description should show on welsh court page
    When I visit "/staff/court/2/facility"
    And I fill in rich editor "form-0-description_cy" with "Welsh fac exp"
    And I press "Update"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "Welsh fac exp"

  Scenario: welsh address should show on welsh court page
    When I visit "/staff/court/2/address"
    And I fill "address_cy" with "Welsh address" in the form "primary_address"
    And I fill "town_name_cy" with "cymtown" in the form "primary_address"
    And I press "Update" in the form "primary_address"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "cymtown"
    And I should see "Welsh address"

  Scenario: welsh address should show on welsh court search results
    When I visit "/staff/court/2/address"
    And I fill "address_cy" with "Welsh address" in the form "secondary_address"
    And I fill "town_name_cy" with "cymtown" in the form "secondary_address"
    And I press "Update" in the form "secondary_address"
    And I visit "search/results?q=cymtown"
    And I press "Cymraeg"
    Then I should see "cymtown"
    And I should see "Welsh address"

  Scenario: welsh fields show on add facilities page
    When I visit "/staff/court/2/add_facility"
    Then I should see "Description (Welsh)"

  Scenario: welsh fields show on edit leaflets page
    When I visit "/staff/court/2/leaflets"
    Then I should see "Information leaflet (Welsh)"
    Then I should see "Defence witness leaflet (Welsh)"
    Then I should see "Prosecution witness leaflet (Welsh)"

  Scenario: welsh contact types show on welsh court page
    When I visit "/staff/edit_contact_type/22"
    And I fill in "name_cy" with "Welsh enquiries"
    And I press "Update"
    And I visit "/staff/court/2"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "Welsh enquiries"

  Scenario: welsh opening types show on welsh court page
    When I visit "/staff/edit_opening_type/1"
    And I fill in "name_cy" with "welsh building open"
    And I press "Update"
    And I visit "/staff/court/2"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see "welsh building open"

  Scenario: welsh facility types show on welsh court page
    When I visit "/staff/edit_facility_type/35"
    And I fill in "image_description_cy" with "welsh babies"
    And I press "Update"
    And I visit "/staff/court/2"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see an image with text "welsh babies"

  Scenario: welsh aols show on welsh court page
    When I visit "/staff/edit_aol/2"
    And I fill in "external_link_desc_cy" with "adopting welsh"
    And I fill in "external_link_cy" with "http://www.visitwales.com/"
    And I press "Update"
    And I visit "/staff/court/2"
    And I view court in the new window
    And I press "Cymraeg"
    Then I should see a link with title "adopting welsh"
    Then I should see a link with href "http://www.visitwales.com/"

  Scenario: welsh aols show on court search in welsh
    When I visit "/staff/edit_aol/2"
    And I fill in "external_link_desc_cy" with "adopting welsh"
    And I fill in "external_link_cy" with "http://www.visitwales.com/"
    And I press "Update"
    And I visit "search/results?q=aylesbury"
    And I press "Cymraeg"
    Then I should see a link with title "adopting welsh"
    Then I should see a link with href "http://www.visitwales.com/"

  Scenario: welsh aols dont show on english court page
    When I visit "/staff/edit_aol/2"
    And I fill in "external_link_desc_cy" with "adopting welsh"
    And I fill in "external_link_cy" with "http://www.visitwales.com/"
    And I press "Update"
    And I visit "/staff/court/2"
    And I view court in the new window
    Then I should not see a link with title "adopting welsh"
    Then I should not see a link with href "http://www.visitwales.com/"

  Scenario: welsh aols dont show on court search in english
    When I visit "/staff/edit_aol/2"
    And I fill in "external_link_desc_cy" with "adopting welsh"
    And I fill in "external_link_cy" with "http://www.visitwales.com/"
    And I press "Update"
    And I visit "search/results?q=aylesbury"
    Then I should not see a link with title "adopting welsh"
    Then I should not see a link with href "http://www.visitwales.com/"
