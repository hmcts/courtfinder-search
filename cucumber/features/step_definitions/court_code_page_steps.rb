Given(/^I visit the court location code page$/) do
  court_code_page.load_page
end

Then(/^I should see the search by court location code header$/) do
  expect(court_code_page.search_index_page.page_header.text)
    .to eq 'Search by Court location code'
end

Then(/^I should see the court location code hint$/) do
  expect(court_code_page.search_index_page.form_block.form_hint[0].text)
    .to eq 'Enter one of the following'
  expect(court_code_page.search_index_page.form_block.form_hint[1].text)
    .to eq 'Court location code'
end

When(/^I search using a valid court location code$/) do
  court_code_page.search_index_page.form_block.courtcode.set('1725')
  court_code_page.search_index_page.continue_button.click
end

Then(/^I should see the results for that code$/) do
  expect(search_results_page.search_results.number_of_results.text).to eq '1'
  expect(search_results_page.search_results.court_results.header[0].text)
    .to eq 'Accrington Magistrates\' Court'
end

When(/^I search using an invalid court location code$/) do
  court_code_page.search_index_page.form_block.courtcode.set('London')
  court_code_page.search_index_page.continue_button.click
end

Then(/^I should see the court location code error message$/) do
  expect(court_code_page.search_index_page.validation_error.text)
    .to have_content 'Sorry, there are no results for .'
  expect(court_code_page.search_index_page.validation_error.text)
    .to have_content 'Please check and try another name or address.'
end
