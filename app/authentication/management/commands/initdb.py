# -*- coding: utf-8 -*-
"""
reset_db command

originally from https://github.com/django-extensions/django-extensions
"""
import logging
import psycopg2 as Database

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from six.moves import input

from django.db.utils import OperationalError
from utils.retry import retry


PROMPT_TEXT = """
You have requested a database reset.
This will IRREVERSIBLY DESTROY
ALL data in the database "%s".
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """


logger = logging.getLogger('metamapper.commands.initdb')


@retry((OperationalError, Database.OperationalError), delay=1.5)  # noqa: C901
def create_database(database_name, owner, conn_params, is_verbose, close_sessions=True):  # noqa: C901
    """Create database with the provided parameters. We add a retry mechanism
    in case we need to wait for the database to start.
    """
    connection = Database.connect(**conn_params)
    connection.set_isolation_level(0)  # autocommit false
    cursor = connection.cursor()

    if close_sessions:
        close_sessions_query = """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '%s';
        """ % database_name
        if is_verbose:
            logger.info('Executing... "%s"', ' '.join(close_sessions_query.split('\n')))
        try:
            cursor.execute(close_sessions_query)
        except Database.ProgrammingError as e:
            if is_verbose:
                logger.exception("Error: %s", str(e))

    create_query = "CREATE DATABASE \"%s\"" % database_name
    if owner:
        create_query += " WITH OWNER = \"%s\" " % owner
    create_query += " ENCODING = 'UTF8'"

    if settings.DEFAULT_TABLESPACE:
        create_query += ' TABLESPACE = %s;' % settings.DEFAULT_TABLESPACE
    else:
        create_query += ';'

    if is_verbose:
        logger.info('Executing... "%s"', create_query)

    try:
        cursor.execute(create_query)
    except Database.errors.DuplicateDatabase:
        pass


class Command(BaseCommand):
    help = "Create the database for this project."

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--noinput', action='store_false',
            dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'
        )
        parser.add_argument(
            '--no-utf8', action='store_true', dest='no_utf8_support',
            default=False,
            help='Tells Django to not create a UTF-8 charset database'
        )
        parser.add_argument(
            '-U', '--user', action='store', dest='user', default=None,
            help='Use another user for the database than defined in settings.py'
        )
        parser.add_argument(
            '-O', '--owner', action='store', dest='owner', default=None,
            help='Use another owner for creating the database than the user defined in settings or via --user'
        )
        parser.add_argument(
            '-P', '--password', action='store', dest='password', default=None,
            help='Use another password for the database than defined in settings.py'
        )
        parser.add_argument(
            '-D', '--dbname', action='store', dest='dbname', default=None,
            help='Use another database name than defined in settings.py'
        )
        parser.add_argument(
            '-R', '--router', action='store', dest='router', default='default',
            help='Use this router-database other than defined in settings.py'
        )
        parser.add_argument(
            '-c', '--close-sessions', action='store_true', dest='close_sessions', default=False,
            help='Close database connections before dropping database (PostgreSQL only)'
        )

    def handle(self, *args, **options):
        """
        Reset the database for this project.

        Note: Transaction wrappers are in reverse as a work around for
        autocommit, anybody know how to do this the right way?
        """
        router = options['router']
        dbinfo = settings.DATABASES.get(router)

        if dbinfo is None:
            raise CommandError("Unknown database router %s" % router)

        user = password = database_name = database_host = database_port = ''
        user = options['user'] or dbinfo.get('USER') or user
        password = options['password'] or dbinfo.get('PASSWORD') or password
        owner = options['owner'] or user
        database_name = options['dbname'] or dbinfo.get('NAME') or database_name

        if database_name == '':
            raise CommandError("You need to specify DB_NAME via the METAMAPPER_DB_NAME environment variable.")

        database_host = dbinfo.get('HOST') or database_host
        database_port = dbinfo.get('PORT') or database_port

        verbosity = options['verbosity']

        if options['interactive']:
            confirm = input(PROMPT_TEXT % (database_name,))
        else:
            confirm = 'yes'

        if confirm != 'yes':
            print("Create database operation cancelled.")
            return

        conn_params = {'database': 'template1'}
        if user:
            conn_params['user'] = user
        if password:
            conn_params['password'] = password
        if database_host:
            conn_params['host'] = database_host
        if database_port:
            conn_params['port'] = database_port

        create_database(database_name, owner, conn_params, verbosity >= 1, options['close_sessions'])

        if verbosity >= 2 or options['interactive']:
            print("Database has been created.")
