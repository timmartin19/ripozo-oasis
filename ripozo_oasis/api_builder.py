from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask
from flask_ripozo import FlaskDispatcher
from ripozo import adapters
from ripozo_sqlalchemy import ScopedSessionHandler, create_resource
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine


def create_app(database_uri):
    """
    Creates a new flask app that exposes the database
    provided as a ReSTful Application

    :param str|unicode|sqlalchemy.engine.url.URL database_uri: The database
        URI in a manner that SQLAlchemy can understand
    :return: A flask app that exposes a database as
        a ReSTful API that can be accessed using either
        the Hal or SIREN protocol
    :rtype: Flask
    """
    # Create the flask application
    app = Flask(__name__)

    # Setup SQLAlchemy to reflect the database
    engine = create_engine(database_uri)
    base = automap_base()
    base.prepare(engine, reflect=True)

    # Create the ripozo dispatcher and register the response formats
    dispatcher = FlaskDispatcher(app)
    dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)
    session_handler = ScopedSessionHandler(engine)

    # Create and register resources from the sqlalchemy models
    # We need to pass ``append_slash=True`` due to a quirk in how flask handles routing
    resources = [create_resource(model, session_handler, append_slash=True) for model in base.classes]
    dispatcher.register_resources(*resources)
    return app
