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
