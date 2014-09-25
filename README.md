Court and Tribunal Finder search
==================

## Installation

This applies to OSX, but should be similar with any other Unix variant.

Clone the repository:

    git clone git@github.com:ministryofjustice/courtfinder-search.git

Next, create the environment and start it up:

    virtualenv env --prompt=\(courtfinder-search\)

    source env/bin/activate

Install python dependencies:

    pip install -r requirements/local.txt

Install node packages:

    npm install

Compile the static assets:

    gulp

Start the server:

    ./courtfinder/manage.py runserver

## Testing and code coverage

Testing uses Django's standard unit testing library. In order to run the tests, use:

    python courtfinder/manage.py test search

Code coverage is measured using 'coverage', speficied in the requirements file for the testing environment. In order to run coverage, use:

    coverage run --source='.' courtfinder/manage.py test search

The line above runs the unit tests, so it can replace the first command mentioned above. The coverage report is then available by using:

    coverage report -m

