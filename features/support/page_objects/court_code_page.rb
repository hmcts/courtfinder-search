class CourtCodePage < BasePage
  set_url '/search/courtcode'

  section :search_index_page, '#search-index-page' do
    element :page_header, '.page-header'
    elements :p, 'p'
    element :validation_error, '.validation-error'
    element :continue_button, '#continue'
    section :form_block, '.form-block' do
      elements :form_hint, '.form-hint'
      element :courtcode, '#courtcode'
    end
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
