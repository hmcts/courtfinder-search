class SearchPage < BasePage
  set_url '/search'

  element :page_header, 'h1'
  element :start_button, '#start-button'
  element :form, '.form-block'

  section :main_option, '.main-option' do
    sections :option, 'li' do
      section :label, 'label' do
        element :input, 'input'
      end
    end
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
