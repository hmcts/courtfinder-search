Given(/^I visit the court location code page$/) do
  court_code_page.load_page
end

Then(/^I should see the search by court location code header$/) do
  header = court_code_page.search_index_page.page_header.text

  expect(header).to eq 'Search by Court location code'
end

Then(/^I should see the court location code hint$/) do
  form_block = court_code_page.search_index_page.form_block

  expect(form_block.form_hint[0].text).to eq 'Enter one of the following'
  expect(form_block.form_hint[1].text).to eq 'Court location code'
end

When(/^I search using a valid court location code$/) do
  court_code_page.search_index_page.form_block.courtcode.set('1725')
  court_code_page.search_index_page.continue_button.click
end

Then(/^I should see the results for that code$/) do
  results = search_results_page.search_results

  expect(results.number_of_results.text).to eq '1'
  expect(results.court_results.header[0].text).to eq 'Accrington Magistrates\' Court'
end

When(/^I search using an invalid court location code$/) do
  court_code_page.search_index_page.form_block.courtcode.set('London')
  court_code_page.search_index_page.continue_button.click
end

Then(/^I should see the court location code error message$/) do
  error = court_code_page.search_index_page.validation_error.text

  expect(error).to have_content 'Sorry, there are no results for London.'
  expect(error).to have_content 'Please check and try another court location code.'
end
