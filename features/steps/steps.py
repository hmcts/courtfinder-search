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
