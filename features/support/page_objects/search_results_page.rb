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
        end
      end
      elements :more_details_link, '.more-details-link'
    end
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
