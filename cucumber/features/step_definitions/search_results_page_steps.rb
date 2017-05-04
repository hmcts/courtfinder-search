Given(/^I visit the search results page$/) do
  search_results_page.load_page
end

Then(/^I should see the search results header$/) do
  expect(search_results_page.page_header.text).to eq 'Search results'
end

Then(/^I should see the number of results in that area$/) do
  expect(search_results_page.search_results).to have_p
end

Then(/^I should see court header$/) do
  expect(search_results_page.search_results.court_results.header.count).to eq 10
  expect(search_results_page.search_results.court_results.header[0].text)
    .to eq 'Tameside Magistrates\' Court'
end

Then(/^I should see court address$/) do
  expect(search_results_page.search_results.court_results.court_address.count)
    .to eq 10
  expect(search_results_page.search_results.court_results.court_town.count)
    .to eq 10
  expect(search_results_page.search_results.court_results.court_postcode.count)
    .to eq 10
end

Then(/^I should see the cases heard at this venue$/) do
  expect(search_results_page.search_results.court_results.court_aol.count)
    .to eq 10
  expect(search_results_page.search_results.court_results.court_aol[0]
     .court_result_heading.text).to eq 'Cases heard at this venue'
end

Then(/^I should see a link for more details about the court$/) do
  expect(search_results_page.search_results.court_results.more_details_link
    .count).to eq 10
  expect(search_results_page.search_results.court_results.more_details_link[1]
    .text).to eq 'More details about Accrington Magistrates\' Court'
end

Then(/^I should see a links to further information$/) do
  expect(search_results_page.search_results.court_results.court_aol[1].li[3]
    .text).to eq 'Divorce'
  # TypeError: no implicit conversion of String into Integer
  # expect(search_results_page.search_results.court_results.court_aol[0].li[1]
  #  .link['href']).to end_with('/divorce')
end
