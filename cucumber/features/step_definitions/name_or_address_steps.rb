Given(/^I visit the name or address page$/) do
  name_or_address_page.load_page
end

Then(/^I should see the search by name or address header$/) do
  expect(name_or_address_page.page_header.text)
    .to eq 'Search by name or address'
end

Then(/^I should see the hint for the form$/) do
  expect(name_or_address_page.form_block.form_hint.count).to eq 2
  expect(name_or_address_page.form_block.form_hint[0].text)
    .to eq 'Enter one of the following'
end

When(/^I search for '(.*?)'$/) do |search_term|
  name_or_address_page.form_block.address.set(search_term)
  name_or_address_page.continue_button.click
end

Then(/^I should see the result is '(.*?)'$/) do |result|
  expect(search_results_page.search_results.number_of_results.text).to eq '1'
  expect(search_results_page.search_results.court_results.header[0].text)
    .to eq result
end

Then(/^I should see the top result is Liverpool Civil and Family Court$/) do
  expect(search_results_page.search_results.number_of_results.text).to eq '10'
  expect(search_results_page.search_results.court_results.header[0].text)
    .to eq 'Liverpool Civil and Family Court'
end

Then(/^I should see '(.*?)' error message$/) do |error|
  expect(name_or_address_page.validation_error.text)
    .to have_content error
end
