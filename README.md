# How to turn your database into a ReSTful API in under 10 lines

This tutorial will show you how to turn your database into a ReSTful
API in just 10 lines of code.

The tutorial will use a powerful and extensible ReST framework called
[ripozo](https://github.com/vertical-knowledge/ripozo) and a couple
packages in the ripozo ecosystem: [flask-ripozo](https://github.com/vertical-knowledge/flask-ripozo)
and [ripozo-sqlalchemy](https://github.com/vertical-knowledge/ripozo-sqlalchemy).  Ripozo
is web framework independent which means that you could use it in any framework you
desire.  Currently, there are packages to make integration with Flask and Django
incredibly painless.  In addition to building seamless ReSTful API's, ripozo allows
you to create Hypermedia/HATEOAS driven API's with no additional effort.

## Step 1: Create the Flask App

The first step is to setup our [Flask](https://github.com/mitsuhiko/flask) application.
You can use [Django](https://www.djangoproject.com/) with 
[django-ripozo](https://github.com/vertical-knowledge/django-ripozo) with minimal differences
but unfortunately, bootstrapping a django project requires more than 10 lines of code.

First we need to install Flask

```bash
pip install Flask
```

Now we simply instantiate a Flask Application.

```python
from flask import Flask
app = Flask(__name__)
```

## Step 2: Setup SQLAlchemy

[SQLAlchemy](http://www.sqlalchemy.org/) is another favorite tool of mine.  It provides
an excellent ORM and in addition it allows us to generate an ORM from an existing database
with no additional work.

```bash
pip install SQLAlchemy
```

To create our sqlalchemy engine is incredibly simple.  We simply
pass it a database uri in the format that SQLAlchemy expects.  See
the [Engine Configuration documentation](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html)
for more details but it's simply a string in this format: 
`'dialect+driver://username:password@host:port/database'`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

database_uri = 'mysql://localhost:3306/mydatabase'
engine = create_engine(database_uri)
base = automap_base()
base.prepare(engine, reflect=True)
```

This creates an ORM where we can access the tables in the database
as if they were python objects.

## Step 3: Bind ripozo

Now that we have our database and web application working we need to bind 
[ripozo](https://github.com/vertical-knowledge/ripozo) to Flask and SQLAlchemy.
Ripozo does not require Flask or SQLAlchemy, however there are helpful packages
to make it easy if you choose to do so.

```bash
pip install ripozo, flask-ripozo, ripozo-sqlalchemy
```

Now in our code:

```python
from flask_ripozo import FlaskDispatcher
from ripozo import adapters
from ripozo_sqlalchemy import ScopedSessionHandler

# attach the flask app created before
dispatcher = FlaskDispatcher(app)
# adapters inform ripozo how to represent the resources over HTTP (typically a
# protocol for a JSON response.  In this case we've chosen the Hal and SIREN protocols.
dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)
# A handler to cleanly handle our database transactions even in failure cases
session_handler = ScopedSessionHandler(engine)
```

## Step 4: Expose our database

At this point we have done all of the necessary setup.  We can simply
expose our database as a ReSTful API.

```python
# A shortcut for creating ripozo Resources.  The create_resource method
# is simply a mechanism for easily creating basic sets of endpoints.
# It has many additional parameters you can pass to dictate how it works and the
# standard way is incredibly flexible and verbose
resources = [create_resource(model, session_handler) for model in base.classes]
# Register our resources with the adapter which exposes them as an API
dispatcher.register_resources(*resources)

# and now we run our Flask app
app.run()
```

## Step 5: Putting it all together

We now have everything that we need so we're going to put it all together
into one function that you simply pass a database URI to.

```python
from flask import Flask
from flask_ripozo import FlaskDispatcher
from ripozo import adapters
from ripozo_sqlalchemy import ScopedSessionHandler, create_resource
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine


def create_app(database_uri):
    app = Flask(__name__)
    
    engine = create_engine(database_uri)
    base = automap_base()
    base.prepare(engine, reflect=True)

    dispatcher = FlaskDispatcher(app)
    dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)
    session_handler = ScopedSessionHandler(engine)

    resources = [create_resource(model, session_handler) for model in base.classes]
    dispatcher.register_resources(*resources)
    app.run()
```

And just like that we have exposed our database as a ReSTful API.  Additionally,
because this is [ripozo](https://github.com/vertical-knowledge/ripozo), if a table
has a relationship to another table, we automatically get a link to the resource that it's
related to.  For example, if we have a user that is part of a group.  When we go to 
the user's endpoint, we'll get a fully qualified url to the group's endpoint.


## Conclusion

We can see how easy [ripozo](https://github.com/vertical-knowledge/ripozo) makes
creating ReSTful API's.  This example is not particularly useful in production.
However, using the power of [ripozo](https://github.com/vertical-knowledge/ripozo)
you could include authentication and authorization, additional endpoints and much more.
Ripozo is designed to be flexible and easy at the same time.  It provides shortcuts
where valuable while allowing you to extend it however you see fit.  Finally, is both more
flexible and gives you more than any of the existing ReSTful frameworks for python.  

