@when(u'I choose to search by "{choice}"')
def step_impl(context, choice):
    map = {
        'A-Z list of all courts': 'list',
        'The Area of Law I am interested in (recommended)': 'aol',
    }

    context.execute_steps(u'''
        When I choose "%s" from "searchby"
        And I press "Next"
    ''' % map[choice])


@when(u'I choose "{aol}" as Area of Law')
def step_impl(context, aol):
    context.execute_steps(u'''
        When I choose "%s" from "aol"
        And I press "Continue"
    ''' % aol)


@given(u'I log in to the admin interface')
def step_impl(context):
    context.execute_steps(u'''
        When I visit "staff/"
        And I fill in "username" with "$username"
        And I fill in "password" with "$password"
        And I press "Log in"
    ''')


@when(u'I switch to the new window')
def step_impl(context):
    driver = context.browser.driver
    driver.switch_to_window(driver.window_handles[1])


@when(u'I view court in the new window')
def step_impl(context):
    context.execute_steps(u'''
        When I press "view"
        And I switch to the new window
    ''')

@when(u'I fill "{field_name}" with "{input_val}" in the form "{form_id}"')
def step_impl(context, field_name, input_val, form_id):
    elem = context.browser.find_by_css(("form#%s *[name='%s']") % (form_id, field_name))
    elem.first._element.send_keys(input_val)


@when(u'I select "{input_val}" from "{field_name}" in the form "{form_id}"')
def step_impl(context, input_val, field_name, form_id):
    elem = context.browser.find_by_xpath("//form[@id='%s']//select[@name='%s']//option[contains(text(), '%s')]"
                                         % (form_id, field_name, input_val))
    elem.first._element.click()


@when(u'I press "{button_name}" in the form "{form_id}"')
def step_impl(context, button_name, form_id):
    elem = context.browser.find_by_css(("form#%s input[value='%s']") % (form_id, button_name))
    elem.first._element.click()


@when(u'I fill in rich editor "{textarea}" with "{content}"')
def step_impl(context, content, textarea):
    with context.browser.get_iframe('id_%s_ifr' % textarea) as iframe:
        iframe.find_by_tag('body').fill(content)
