class NavigationPage < BasePage
  set_url 'search/'

  section :global_header, '#global-header' do
    section :header_logo, '.header-logo' do
      element :link, 'a'
    end
    section :header_proposition, '.header-proposition' do
      element :link, 'a'
    end
  end

  section :global_breadcrumb, '#global-breadcrumb' do
    sections :li, 'li' do
      element :link, 'a'
    end
  end

  section :feedback_banner, '#feedback-banner' do
    elements :link, 'a'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
