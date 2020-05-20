from os import environ
from os.path import exists
from sys import path

PROJECT_PATH = "/root/projectoria/votewebxxl"
PACKAGES_PATH = "/root/venv/lib/python3.6/site-packages/"
if exists(PACKAGES_PATH):
    path.append(PACKAGES_PATH)
if exists(PROJECT_PATH):
    path.append(PROJECT_PATH)
environ['DJANGO_SETTINGS_MODULE']='VoteSimple.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

