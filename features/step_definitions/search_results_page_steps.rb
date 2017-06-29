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
  expect(court_results.header[0].text).to eq 'Bow County Court and Family Court'
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
  expect(court_results.more_details_link[1].text).to eq 'More details about Barkingside Magistrates\' Court'
end

Then(/^I should not see a link for further information when it is not available$/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.court_aol[1].li[0].text).to eq 'Crime'
  expect(court_results.court_aol[1].li[0]).to have_no_link
end

Then(/^I should see a link for further information when available/) do
  court_results = search_results_page.search_results.court_results

  expect(court_results.court_aol[0].li[0].link.text).to have_content('Housing possession')
  expect(court_results.court_aol[0].li[0]).to have_screen_reader_hide
  expect(court_results.court_aol[0].li[0].link['href']).to end_with('/evicting-tenants')
end

Then(/^I should see document exchange$/) do
  expect(search_results_page.document_exchange_label.count).to eq 9
  expect(search_results_page.document_exchange_label[0].text).to eq 'DX:'
  expect(search_results_page.document_exchange_value.count).to eq 9
  expect(search_results_page.document_exchange_value[0].text).to eq '97490 Stratford (London) 2'
end

Then(/^I should see the court location code$/) do
  expect(search_results_page.court_location_code_label.count).to eq 6
  expect(search_results_page.court_location_code_label[0].text).to eq 'Court location code:'
  expect(search_results_page.court_location_code_value.count).to eq 6
  expect(search_results_page.court_location_code_value[0].text).to eq '140'
end
