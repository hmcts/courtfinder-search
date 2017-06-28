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
  court_results = search_results_page.search_results.court_results
  expect(court_results.header.count).to eq 10
  expect(court_results.header[0].text).to eq 'Tameside Magistrates\' Court'
end

Then(/^I should see court address$/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.court_address.count).to eq 10
  expect(court_results.court_town.count).to eq 10
  expect(court_results.court_postcode.count).to eq 10
end

Then(/^I should see the cases heard at this venue$/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.court_aol.count).to eq 10
  expect(court_results.court_aol[0].court_result_heading.text).to eq 'Cases heard at this venue'
end

Then(/^I should see a link for more details about the court$/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.more_details_link.count).to eq 10
  expect(court_results.more_details_link[1].text).to eq 'More details about Accrington Magistrates\' Court'
end

Then(/^I should not see a link for further information on Divorce$/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.court_aol[1].li[3].text).to eq 'Divorce'
  expect(court_results.court_aol[1].li[3]).to have_no_link
end

Then(/^I should see a link for further information on Bankruptcy$/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.court_aol[4].li[0].link['href']).to end_with('/bankruptcy')
end

Then(/^I should see document exchange$/) do
  expect(search_results_page.document_exchange_label.text).to eq 'DX:'
  expect(search_results_page.document_exchange_value.text).to eq '702625 Ashton-under-Lyne 2'
end

Then(/^I should see the court location code$/) do
  expect(search_results_page.court_location_code_label.text).to eq 'Court location code:'
  expect(search_results_page.court_location_code_value.text).to eq '1748'
end