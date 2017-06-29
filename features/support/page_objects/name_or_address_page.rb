class NameOrAddressPage < BasePage
  set_url '/search/address'

  element :page_header, 'h1'
  element :validation_error, '.validation-error'
  element :continue_button, '#continue'
  section :form_block, '.form-block' do
    elements :form_hint, '.form-hint'
    element :address, '#address'
  end
  section :alert, '.alert' do
    elements :p, 'p'
    element :a, 'a'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
