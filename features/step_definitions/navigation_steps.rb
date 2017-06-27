Then(/^I see I can navigate to gov\.uk$/) do
  logo = navigation_page.global_header.header_logo

  expect(logo.link.text).to eq 'GOV.UK'
  expect(logo.link['title']).to eq 'Go to the GOV.UK homepage'
  expect(logo.link['href']).to eq 'https://www.gov.uk/'
end

Then(/^I see I can navigate to court and tribunal finder$/) do
  header = navigation_page.global_header.header_proposition

  expect(header.link.text).to eq 'Court and tribunal finder'
  expect(header.link['href']).to end_with '/'
end

Then(/^I see I can use breadcrumbs to navigate to home$/) do
  breadcrumb = navigation_page.global_breadcrumb.li[0]

  expect(breadcrumb.link.text).to eq 'Home'
  expect(breadcrumb.link['href']).to end_with '/'
end

And(/^to find a court or tribunal$/) do
  global_breadcrumb = navigation_page.global_breadcrumb.li[1]

  expect(global_breadcrumb.link.text).to eq 'Find a court or tribunal'
  expect(global_breadcrumb.link['href']).to end_with '/search/'
end

And(/^to about your issue$/) do
  global_breadcrumb = navigation_page.global_breadcrumb.li[2]

  expect(global_breadcrumb.link.text).to eq 'About your issue'
  expect(global_breadcrumb.link['href']).to end_with '/search/aol?aol=All'
end

And(/^to search by postcode$/) do
  postcode = navigation_page.global_breadcrumb.li[3]

  expect(postcode.link.text).to eq 'Search by postcode'
  expect(postcode.link['href']).to have_content '/search/postcode'
end

Then(/^I see I can find out more about BETA$/) do
  feedback = navigation_page.feedback_banner

  expect(feedback.link[0].text).to eq 'BETA'
  expect(feedback.link[0]['href']).to end_with '/service-manual/phases/beta.html'
end

Then(/^I see I can give feedback$/) do
  feedback = navigation_page.feedback_banner

  expect(feedback.link[1].text).to eq 'your feedback'
  expect(feedback.link[1]['href']).to end_with '/feedback'
end
