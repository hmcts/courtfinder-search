Given(/^I visit the area of law page$/) do
  area_of_law_page.load_page
end

Then(/^I should see about your issue header$/) do
  expect(area_of_law_page.page_header.text).to eq 'About your issue'
end

Then(/^I should see issues:$/) do |issues|
  issues.rows.each_with_index do |issue, index|
    expect(area_of_law_page.form.aol_name[index].text).to eq issue[0]
    expect(area_of_law_page.form.block_label[index]['type']).to eq 'radio'
  end
end

Then(/^each issue should have a description$/) do
  expect(area_of_law_page.form.aol_name.count).to eq 10
  expect(area_of_law_page.form.aol_description.count).to eq 10
end

Then(/^none of the above is selected by default$/) do
  expect(area_of_law_page.form.block_label[9]).to be_checked
end

# TODO: check where this url is going
Then(/^I should see the continue button$/) do
  expect(area_of_law_page.continue_button.text).to eq 'Continue'
end
