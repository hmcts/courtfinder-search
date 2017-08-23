require 'pry'
require 'site_prism'
require 'capybara'
require 'capybara/dsl'
require 'capybara/cucumber'
require 'capybara/poltergeist'
require 'capybara-screenshot/cucumber'

ENV['ZAP_PROXY'] ||= "localhost"
ENV['ZAP_PROXY_PORT'] ||= "8080"

require File.dirname(__FILE__) + '/../support/capybara_driver_helper'
require File.dirname(__FILE__) + '/../support/site_prism_config'
