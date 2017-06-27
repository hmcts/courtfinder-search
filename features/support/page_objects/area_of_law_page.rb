class AreaOfLawPage < BasePage
  set_url 'search/aol'

  element :page_header, 'h1'
  element :continue_button, '#continue'

  section :form, '#aols' do
    elements :block_label, '.block-label input'
    elements :aol_name, '.aol-name'
    elements :aol_description, '.aol-description'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
