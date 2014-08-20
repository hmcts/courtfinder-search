Court and Tribunal Finder search
==================

## Dependencies

* [Virtualenv](http://www.virtualenv.org/en/latest/)
* [Python](http://www.python.org/) (Can be installed using `brew`)
* [Postgres](http://www.postgresql.org/)
* [nodejs.org](http://nodejs.org/)

## Installation

Clone the repository:

    git clone git@github.com:ministryofjustice/courtfinder-search.git

Next, create the environment and start it up:

    virtualenv env --prompt=\(courtfinder-search\)

    source env/bin/activate

Install python dependencies:

    pip install -r requirements/local.txt

If you get an error about python 1.7 not being found, type:

    pip install https://www.djangoproject.com/download/1.7c2/tarball/
    pip install -r requirements/local.txt


Install node packages:

    npm install

Start the server:

    ./courtfinder/manage.py runserver 8001

## Testing

NightWatch is used to run basic functional/browser tests on basic DOM interactions. To run the tests, make sure you have the following dependencies:

* [Selenium](http://docs.seleniumhq.org/) (2.41.0) (Install using homebrew `brew install selenium-server-standalone`)
* [Nightwatch.js](http://nightwatchjs.org/) (~0.4.14)
* [PhantomJS](http://phantomjs.org/) (1.9.7)

To run the tests, use the following make command:

    make test

By default, tests will be run on `http://0.0.0.0:8001/`. To change this you can pass the `--url` argument on the command called in the make file. To see what command is called look at the `Makefile` at the project root.

To run the test on the API, use the command:

    cd courtfinder
    python manage.py test



