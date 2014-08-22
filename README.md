Court and Tribunal Finder search
==================

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

Compile the static assets:

    gulp

Start the server:

    ./courtfinder/manage.py runserver

## Testing




