Then(/^I see I can navigate to gov\.uk$/) do
  expect(navigation_page.global_header.header_logo.link.text).to eq 'GOV.UK'
  expect(navigation_page.global_header.header_logo.link['title'])
    .to eq 'Go to the GOV.UK homepage'
  expect(navigation_page.global_header.header_logo.link['href'])
    .to eq 'https://www.gov.uk/'
end

Then(/^I see I can navigate to court and tribunal finder$/) do
  expect(navigation_page.global_header.header_proposition.link.text)
    .to eq 'Court and tribunal finder'
  expect(navigation_page.global_header.header_proposition.link['href'])
    .to end_with '/'
end

Then(/^I see I can use breadcrumbs to navigate to home$/) do
  expect(navigation_page.global_breadcrumb.li[0].link.text)
    .to eq 'Home'
  expect(navigation_page.global_breadcrumb.li[0].link['href'])
    .to end_with '/'
end

And(/^to find a court or tribunal$/) do
  expect(navigation_page.global_breadcrumb.li[1].link.text)
    .to eq 'Find a court or tribunal'
  expect(navigation_page.global_breadcrumb.li[1].link['href'])
    .to end_with '/search/'
end

And(/^to about your issue$/) do
  expect(navigation_page.global_breadcrumb.li[2].link.text)
    .to eq 'About your issue'
  expect(navigation_page.global_breadcrumb.li[2].link['href'])
    .to end_with '/search/aol?aol=All'
end

And(/^to search by postcode$/) do
  expect(navigation_page.global_breadcrumb.li[3].link.text)
    .to eq 'Search by postcode'
  expect(navigation_page.global_breadcrumb.li[3].link['href'])
    .to have_content '/search/postcode'
end

Then(/^I see I can find out more about BETA$/) do
  expect(navigation_page.feedback_banner.link[0].text).to eq 'beta'
  expect(navigation_page.feedback_banner.link[0]['href'])
    .to end_with '/service-manual/phases/beta.html'
end

Then(/^I see I can give feedback$/) do
  expect(navigation_page.feedback_banner.link[1].text).to eq 'your feedback'
  expect(navigation_page.feedback_banner.link[1]['href'])
    .to end_with '/feedback'
end
