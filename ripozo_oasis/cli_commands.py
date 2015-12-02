from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import traceback

import click
from sqlalchemy.engine.url import URL

from ripozo_oasis.api_builder import create_app


@click.command()
@click.argument('database_uri', required=False)
@click.option('-p', '--port', type=int, help='The port of the database that you wish to expose')
@click.option('-h', '--host', type=str, help='The data base host e.g. "localhost"')
@click.option('-d', '--dialect', type=str, help='The database dialect e.g. "mysql" or "postgres"')
@click.option('--driver', type=str, help='The database driver to use e.g. "psycopg2" or "pg8000"')
@click.option('-n', '--name', type=str, help='The database name')
@click.option('-u', '--user', type=str, help='The database user')
@click.option('-p', '--password', type=str, help='The database user\'s password if necessary')
@click.option('--debug', is_flag=True, help='A flag to run the application in debug mode')
@click.option('--app-port', type=int, help='The port to run the application on')
def auto_ripozo_db(app_port, debug, password, user, name, driver, dialect, host, port, database_uri):
    """
    Creates and starts a ReSTful API from a database.  Full CRUD+L (Create,
    Retrieve, Update, Delete, and List) is available for every model in the
    database.  Additionally, the application is completely HATEOAS with
    full urls pointing to related objects.

    See the SQLAlchemy documentation on
    `Engine Configuration <http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html>`_
    for more details on constructing a datbase uri.

    Either the database_uri argument is required or host, port, name and dialect are
    required at a minimum.
    """
    if not database_uri:
        dialect = '{0}+{1}'.format(dialect, driver) if driver else dialect
        database_uri = URL(dialect, username=user, password=password, host=host,
                           port=port, database=name)

    try:
        app = create_app(database_uri)
    except ImportError:
        traceback.print_exc()
        print()
        print("It appears there was an import error.  Typically,"
              " this is because you are missing the driver.  Simply "
              "pip install the driver you prefer for your database and "
              "try again.")
        print("For example, for MySQL `pip install MySQL-python` or "
              "for PostGreSQL: `pip install psycopg2`.  ")
        print("Check out this link for more details: "
              "http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html")
        print()
    else:
        app.run(debug=debug, port=app_port)


def run_commands():
    auto_ripozo_db()

if __name__ == '__main__':
    auto_ripozo_db()
