Given(/^I visit the court details page for Cannock Magistrates' Court$/) do
  court_details_page.load_page
end

Then(/^I should see Cannock Magistrates' Court$/) do
  expect(court_details_page.h1.text).to eq 'Cannock Magistrates\' Court'
end

Then(/^I should see visit us address$/) do
  expect(court_details_page.addresses.visiting.h2.text).to eq 'Visit us:'
  expect(court_details_page.addresses.visiting.span.count).to eq 4
  expect(court_details_page.addresses.visiting.span[1].text).to eq 'Cannock'
end

Then(/^I should see map and directions link$/) do
  expect(court_details_page.addresses.visiting.map_link.text).to eq 'Maps and directions'
end

Then(/^I should see write to us address$/) do
  expect(court_details_page.addresses.postal.h2.text).to eq 'Write to us:'
  expect(court_details_page.addresses.postal.text).to have_content 'Staffordshire'
end

Then(/^I should see court location\/tribunal no\.$/) do
  expect(court_details_page.addresses.pros.text).to have_content 'Court location/tribunal no.'
end

Then(/^I should see opening hours$/) do
  expect(court_details_page.opening_times.h2.text).to eq 'Opening hours'
  expect(court_details_page.opening_times).to have_li
end

Then(/^I should see phone numbers:$/) do |phone_numbers|
  expect(court_details_page.contacts.h2.text).to eq 'Phone numbers'
  phone_numbers.rows.each_with_index do |phone_number, index|
    expect(court_details_page.contacts.label_pad[index].text).to eq phone_number[0]
    expect(court_details_page.contacts).to have_phone_number
  end
end

Then(/^I should see building facilities:$/) do |facilities|
  expect(court_details_page.facilities.h2.text).to eq 'Building facilities'
  expect(court_details_page.facilities).to have_p
  facilities.rows.each_with_index do |facility, index|
    expect(court_details_page.facilities.li[index].text).to eq facility[0]
    expect(court_details_page.facilities.li[index]).to have_icon
    expect(court_details_page.facilities.li[index]).to have_facility
  end
end

Then(/^I should see image of court or tribunal$/) do
  expect(court_details_page).to have_photo
end

Then(/^I should see cases heard at this venue$/) do
  expect(court_details_page.areas_of_law.h2.text).to eq 'Cases heard at this venue'
  expect(court_details_page.areas_of_law.li.text).to eq 'Crime'
end

Then(/^I should see find a form$/) do
  expect(court_details_page.useful_links.h2.text).to eq 'Useful links:'
  expect(court_details_page.useful_links.link[0].text).to eq 'Find a form'
  expect(court_details_page.useful_links.link[0]['href']).to end_with 'HMCTS/FormFinder.do'
end

Then(/^I should see make a complaint$/) do
  expect(court_details_page.useful_links.link[1].text).to eq 'Make a complaint'
  expect(court_details_page.useful_links.link[1]['href']).to end_with 'about/complaints-procedure'
end
