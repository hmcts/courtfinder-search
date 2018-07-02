#!/bin/bash
#
# Regenerate the language (.po) files based on strings marked
# for translation. This should be re-run every time the templates
# or language files are changed.

python ./manage.py makemessages --locale=en --no-wrap -e jinja,py,html
python ./manage.py makemessages --locale=cy --no-wrap -e jinja,py,html
