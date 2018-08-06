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
        When I press "view in new window"
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

@when(u'I select "{select_text}" from "{select_id}"')
def step_impl(context, select_text, select_id):
    elem = context.browser.find_by_xpath("//select[@id='%s']/option[@value='%s']" % (select_id, select_text))
    elem.first._element.click()

@when(u'I press "{button_name}" in the form "{form_id}"')
def step_impl(context, button_name, form_id):
    elem = context.browser.find_by_css(("form#%s input[value='%s']") % (form_id, button_name))
    elem.first._element.click()

@when(u'I remove the first form instance')
def step_impl(context):
    elem = context.browser.find_by_css("button.remove").first
    elem._element.click()


@when(u'I fill in rich editor "{textarea}" with "{content}"')
def step_impl(context, content, textarea):
    with context.browser.get_iframe('id_%s_ifr' % textarea) as iframe:
        iframe.find_by_tag('body').fill(content)

@when(u'I clear rich editor "{textarea}"')
def step_impl(context, textarea):
    with context.browser.get_iframe('id_%s_ifr' % textarea) as iframe:
        iframe.find_by_tag('body').fill("")


@when(u'I check box with label "{label}"')
def step_impl(context, label):
    box = context.browser.find_by_xpath("//label[contains(text(), '%s')]" % label).first
    box.click()


@when(u'I uncheck box with label "{label}"')
def step_impl(context, label):
    box = context.browser.find_by_xpath("//label[contains(text(), '%s')]" % label).first
    box.click()


@then(u'I should see "{text}" in section "{section}"')
def step_impl(context, text, section):
    container = context.browser.find_by_xpath("//*[contains(text(), '%s')]/.." % section).first
    assert text in container.text


@then(u'I should not see "{text}" in section "{section}"')
def step_impl(context, text, section):
    container = context.browser.find_by_xpath("//*[contains(text(), '%s')]/.." % section).first
    assert text not in container.text


@then(u'I should see "{text}" in element "{id}"')
def step_impl(context, text, id):
    container = context.browser.find_by_id(id).first
    haystack = container.text.replace('\n', ' ')
    assert text in haystack

@then(u'"{name}" should be marked as required')
def step_impl(context, name):
    assert context.browser.is_element_present_by_xpath("//input[@name='%s'][@required='']" % name)

@then(u'I should see an image with text "{text}"')
def step_impl(context, text):
    assert context.browser.is_element_present_by_xpath("//img[contains(@alt, '%s')]" % text)

@then(u'I should see a link with title "{text}"')
def step_impl(context, text):
    assert context.browser.is_element_present_by_xpath("//a[contains(@title, '%s')]" % text)

@then(u'I should not see a link with title "{text}"')
def step_impl(context, text):
    assert not context.browser.is_element_present_by_xpath("//a[contains(@title, '%s')]" % text)

@then(u'I should see a link with href "{text}"')
def step_impl(context, text):
    assert context.browser.is_element_present_by_xpath("//a[contains(@href, '%s')]" % text)

@then(u'I should not see a link with href "{text}"')
def step_impl(context, text):
    assert not context.browser.is_element_present_by_xpath("//a[contains(@href, '%s')]" % text)