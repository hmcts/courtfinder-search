class PostcodePage < BasePage
  set_url '/search/postcode'

  element :page_header, 'h1'
  element :postcode, '#postcode'
  element :continue_button, '#continue'
  element :validation_error, '.validation-error'
  element :search_results, '.search-results p'

  section :court_results, '#court-results' do
    elements :result, 'li > h2'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
