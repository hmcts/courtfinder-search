Given(/^I visit the postcode page$/) do
  postcode_page.load_page
end

When(/^I enter an invalid postcode$/) do
  postcode_page.postcode.set('faoan')
  postcode_page.continue_button.click
end

Then(/^I should see the enter postcode header$/) do
  expect(postcode_page.page_header.text).to eq 'Enter postcode'
end

Then(/^I should see postcode error message$/) do
  expect(postcode_page.validation_error.text)
    .to eq 'Error You did not enter a valid postcode. Please try again.'
end

When(/^I enter a full valid postcode$/) do
  postcode_page.postcode.set('ig12bn')
  postcode_page.continue_button.click
end

Then(/^I should see results for that postcode$/) do
  expect(postcode_page.search_results.text)
    .to eq 'These are the 10 courts or tribunals nearest ig12bn.'
  expect(postcode_page.court_results.result.count).to eq 10
end

When(/^I enter a first half of a valid postcode$/) do
  postcode_page.postcode.set('ig1')
  postcode_page.continue_button.click
end

Then(/^I should see results for the first half of the postcode$/) do
  expect(postcode_page.search_results.text)
    .to eq 'These are the 10 courts or tribunals nearest ig1.'
  expect(postcode_page.court_results.result.count).to eq 10
end
