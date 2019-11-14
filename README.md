[![Build Status](https://dev.azure.com/HMCTS-PET/pet-azure-infrastructure/_apis/build/status/courtfinder?branchName=master)](https://dev.azure.com/HMCTS-PET/pet-azure-infrastructure/_build/latest?definitionId=31&branchName=master)

Court and Tribunal Finder search
==================

## Installation

### Set-up with Vagrant 

Clone the repository:

    git clone git@github.com:hmcts/courtfinder-search.git

Rename

    courtfinder/courtfinder/settings/local.py.example to courtfinder/courtfinder/settings/local.py

In the project root run

    vagrant up

This will provision a full development environment in a virtual machine, which include a postgres database.

Then run

    vagrant ssh

Change to the courtfinder directory
    
    cd courtfinder

Set up data

    ./manage.py populate-db

You can now run the Django web server

    ./manage.py runserver 0.0.0.0:8000

NOTE: If you have to run vagrant up more than once you may get an error about conflicting portsi, 
usually port 8000. To resolve this on a mac run

    lsof -i tcp:8000

to get the process number (pid), then kill it with

    kill -9 <pid>


### None vagrant set-up

This applies to OSX, but should be similar with any other Unix variant.

Clone the repository:

    git clone git@github.com:hmcts/courtfinder-search.git

Next, create the environment and start it up:

    virtualenv env --prompt=\(courtfinder-search\)

    source env/bin/activate

Install python dependencies (ignore the warnings):

    pip install -r requirements/local.txt

Install the test dependencies:

    sudo apt install python-libxml2 python-libxslt1 python-dev

Install node packages, gulp and sass:

    npm install
    npm install gulp -g
    npm install gulp --save-dev
    gem install sass


Compile the static assets:

    gulp

Setup postgres: create a user courtfinder with no password and create a database called courtfinder_search, which user courtfinder has owner and superuser rights:

    psql template1
    template1=> create user courtfinder login;
    template1=> create database courtfinder_search;
    template1=> alter database courtfinder_search owner to courtfinder;
    template1=> alter user courtfinder with superuser;
    template1=> \q

Create the database and put sample data in it:

    cd courtfinder
    ./manage.py makemigrations
    ./manage.py migrate
    ./manage.py populate-db

Start the server:

    ./manage.py runserver

## Testing and code coverage

Testing uses Django's standard unit testing library. In order to run the tests, use:

    python courtfinder/manage.py test search

Code coverage is measured using 'coverage', speficied in the requirements file for the testing environment. In order to run coverage, use:

    coverage run --omit='courtfinder/*,*__init__*' --source='.' manage.py test staticpages courts search
    coverage run --append --omit='courtfinder/*,*__init__*' --source='.' manage.py populate-db data/test_data

The two lines above runs the unit tests, so it can replace the first command mentioned above. The coverage report is then available by using:

    coverage report -m

py.test can also be used to run tests faster:

    py.test -n 3

will run the tests using 3 processes. To show the coverage report:

    py.test -n 3 --cov . --cov-report term-missing

## Environment variables

The application uses the following environment variables.

* `FEEDBACK_EMAIL_SENDER`: the from address of the feedback emails sent by the application
* `FEEDBACK_EMAIL_RECEIVER`: the email addresses of the recipients of the feedback emails (comma separated)
* `SMTP_HOSTNAME`
* `SMTP_PASSWORD`
* `SMTP_PORT`
* `SMTP_USERNAME`: SMTP details for sending feedback emails
* `SENTRY_URL`: for monitoring. See <https://getsentry.com/>
* `S3_KEY`, `S3_BUCKET`, `S3_SECRET`: the `populate-db` command above either reads the court data from local files or, if those variables are set, from an S3 bucket.
