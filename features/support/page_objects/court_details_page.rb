class CourtDetailsPage < BasePage
  set_url '/courts/cannock-magistrates-court'

  element :h1, 'h1'

  section :addresses, '#addresses' do
    section :visiting, '#visiting' do
      element :h2, 'h2'
      elements :span, 'span'
      element :map_link, '#map-link > a'
    end
    section :postal, '#postal' do
      element :h2, 'h2'
    end
    element :pros, '#pros'
  end

  element :photo, '#photo > img'

  section :opening_times, '#opening-times' do
    element :h2, 'h2'
    element :li, 'li'
  end

  section :contacts, '#contacts' do
    element :h2, 'h2'
    elements :label_pad, '.label-pad'
    elements :phone_number, '.phone-number'
  end

  section :facilities, '#facilities' do
    element :h2, 'h2'
    element :p, 'p'
    sections :li, 'li' do
      element :icon, '.icon'
      element :facility, '.facility'
    end
  end

  section :areas_of_law, '#areas_of_law' do
    element :h2, 'h2'
    element :li, 'li'
  end

  section :useful_links, '#useful_links' do
    element :h2, 'h2'
    elements :link, 'a'
  end

  element :last_update, '#last_update'

  def load_page(page_version = nil)
    load(v: page_version)
  end
end

