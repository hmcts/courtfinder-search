Given(/^I visit the all courts page$/) do
  all_courts_page.load_page
end

Then(/^I should see the courts and tribunals header$/) do
  expect(all_courts_page.search_index_page.page_header.text)
    .to eq 'Courts and Tribunals'
end

Then(/^I should see instructions$/) do
  expect(all_courts_page.search_index_page.p[0].text)
    .to eq 'Browse by name of court or tribunal'
  expect(all_courts_page.search_index_page.p[1].text)
    .to eq 'Select the first letter of the court\'s name'
end

When(/^I see the A\-Z navigation$/) do
  expect(all_courts_page.search_index_page.a_z_navigation.ul.link.count)
    .to eq 26
end

Then(/^I should see each letter goes to the corresponding page$/) do
  navigation_block = all_courts_page.search_index_page.a_z_navigation.ul
  ('A'..'Z').to_a.each_with_index do |val, index|
    expect(navigation_block.link[index]['href']).to end_with(val)
    expect(navigation_block.li[index].text).to eq(val)
  end
end
