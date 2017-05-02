Given(/^I visit the search page$/) do
  search_page.load_page
end

Then(/^I should see the search header$/) do
  expect(search_page.page_header.text).to eq 'Find the right court or tribunal'
end

Then(/^I should see area of law I am interested in is selected$/) do
  expect(search_page.main_option.option[0].label.text)
    .to eq 'The Area of Law I am interested in (recommended)'
  expect(search_page.main_option.option[0].label.input).to be_checked
end

Then(/^I should see an option to search by court name or address$/) do
  expect(search_page.main_option.option[1].text).to eq 'Court Name or Address'
end

Then(/^I should see an option to search by A\-Z list of all courts$/) do
  expect(search_page.main_option.option[2].text).to eq 'A-Z list of all courts'
end

Then(/^I should see an option to search by court location code$/) do
  expect(search_page.main_option.option[3].text).to eq 'Court location code'
end

Then(/^I should see the next button$/) do
  expect(search_page.form['action']).to end_with '/search/searchby'
end
