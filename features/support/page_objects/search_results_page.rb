class SearchResultsPage < BasePage
  set_url '/search/results?aol=All&postcode=ig1+2bn'

  element :page_header, 'h1'

  section :search_results, '.search-results' do
    element :p, 'p'
    element :number_of_results, '#number-of-results'
    section :court_results, '#court-results' do
      elements :header, 'h2'
      elements :court_address, '.court-address'
      elements :court_town, '.court-town'
      elements :court_postcode, '.court-postcode'
      sections :court_aol, '.court-aol' do
        element :court_result_heading, '.court-result-heading'
        sections :li, 'ul > li' do
          element :link, 'a'
          element :screen_reader_hide, '.screen_reader_hide'
        end
      end
      elements :more_details_link, '.more-details-link'
    end
  end
  elements :document_exchange_label, '#document-exchange-label'
  elements :document_exchange_value, '#document-exchange-value'
  elements :court_location_code_label, '#court-location-code-label'
  elements :court_location_code_value, '#court-location-code-value'

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
