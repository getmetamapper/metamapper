#
# Gunicorn (https://docs.gunicorn.org/en/stable/configure.html)
#
# Metamapper uses Gunicorn to handle web requests by default. We recommend
# spinning up a few of these and putting them behind a reverse proxy like nginx.
#
# You can override these default settings by creating your own file and referencing the
# path to the Python file via the METAMAPPER_GUNICORN_CONFIG_PATH environment variable.
#

bind = '0.0.0.0:5050'
