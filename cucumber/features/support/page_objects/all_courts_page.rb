class AllCourtsPage < BasePage
  set_url 'courts/'

  section :search_index_page, '#search-index-page' do
    element :page_header, '.page-header'
    elements :p, 'p'
    section :a_z_navigation, '.a-z-navigation' do
      section :ul, 'ul' do
        elements :link, 'a'
        elements :li, 'li'
      end
    end
  end
  element :continue_button, '#continue'

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
