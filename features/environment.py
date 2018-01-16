from behaving import environment as benv
from behaving.web.steps import *
from behaving.mail.steps import *
from behaving.personas.steps import *
from selenium import webdriver
import os

PERSONAS = {
    'admin': dict(
        username='admin',
        password='admin',
    ),
}

# override with -Dkey=value
config = {
    'base_url': 'http://127.0.0.1:8000',
    'headless': False,
    'remote': False,
}

def before_all(context):
    config.update(context.config.userdata)

    if config['remote']:
        context.remote_webdriver = True
        s_username = os.environ['SAUCELABS_USER']
        s_apikey = os.environ['SAUCELABS_KEY']
        saucelabs_url = 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (s_username, s_apikey)
        context.browser_args = {'url': saucelabs_url}
    else:
        context.default_browser = 'chrome'
        context.single_browser = True
        if config['headless']:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            context.browser_args = {'options': chrome_options}

    context.base_url = config['base_url']
    benv.before_all(context)


def after_all(context):
    benv.after_all(context)


def before_feature(context, feature):
    benv.before_feature(context, feature)


def after_feature(context, feature):
    benv.after_feature(context, feature)


def before_scenario(context, scenario):
    benv.before_scenario(context, scenario)
    context.personas = PERSONAS
    context.execute_steps(u'''
        Given a browser
    ''')


def after_scenario(context, scenario):
    benv.after_scenario(context, scenario)
