# How to turn your database into a ReSTful API in under 10 lines of code

A package to turn your database into a ReSTful API in just 10 lines of code.

You can either install the package and simply start the API from the
command line or you can follow this tutorial to build it yourself.

## Installation

```bash
pip install ripozo-oasis
```

## Running your API

To turn your database into a ReSTful API simply run the following command.

```bash
auto-api "mysql://localhost:3306/mydatabase"
```

You will need to pass a Database URI according to the 
[SQLALchemy Engine Configuration documentation](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html).
The format is `'dialect+driver://username:password@host:port/database_name'`.
The driver is optional and only necessary if you do not wish to use the default.  If you get import errors
you will need to install a specific driver for your database.  For example, with MySQL you'll need
to run ``pip install mysql-python`` or for postgresql you'll need to run ``pip install psycopg2``.

Now we can curl the base to get all available endpoints

```bash
curl -X OPTIONS http://localhost:5000/
```

We may see something like this assuming we had two tables, groups and users.

```javascript
{
  "_embedded": {},
  "_links": {
    "group": {
      "href": "/group/"
    },
    "user": {
      "href": "/user/"
    },
    "self": {
      "href": "http://localhost:5000/"
    }
  }
}
```

We could additionally vary the accept type to get a SIREN formatted response

```bash
curl -X OPTIONS -H "Accept: application/vnd.siren+json" http://localhost:5000/
```

```javascript
{
  "entities": [],
  "class": [
    ""
  ],
  "links": [
    {
      "href": "http://localhost:5000/",
      "rel": [
        "self"
      ]
    },
    {
      "href": "http://localhost:5000/group/",
      "rel": [
        "group_list"
      ]
    },
    {
      "href": "http://localhost:5000/group/<id>/",
      "rel": [
        "group"
      ]
    },
    {
      "href": "http://localhost:5000/user/",
      "rel": [
        "user_list"
      ]
    },
    {
      "href": "http://localhost:5000/user/<id>/",
      "rel": [
        "user"
      ]
    }
  ],
  "actions": [
    {
      "fields": [],
      "href": "http://localhost:5000/",
      "title": "All Options",
      "method": "OPTIONS",
      "name": "all_options"
    }
  ],
  "properties": {}
}
```

We have full CRUD+L (Create, Retrieve, Update, Delete and List) operations: a POST to ``/user/`` creates
a new user, a GET to ``/user/`` returns a list of all users, a GET on ``/user/<id>/``
returns an individual user and so forth.

## Tutorial

This tutorial uses a powerful and extensible ReST framework called
[ripozo](https://github.com/vertical-knowledge/ripozo) and a couple
packages in the ripozo ecosystem: [flask-ripozo](https://github.com/vertical-knowledge/flask-ripozo)
and [ripozo-sqlalchemy](https://github.com/vertical-knowledge/ripozo-sqlalchemy).  Ripozo
is web framework independent, meaning you can use it in any desired web framework.
Official integrations include [flask-ripozo](https://github.com/vertical-knowledge/flask-ripozo)
and [django-ripozo](https://github.com/vertical-knowledge/django-ripozo) with more to come.
In addition to building seamless ReSTful API's, ripozo can expose [Hypermedia/HATEOAS](http://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)
driven API's with *no additional effort*.

### Step 1: Create the Flask App

The first step is to setup our [Flask](https://github.com/mitsuhiko/flask) application.
You can use [django-ripozo](https://github.com/vertical-knowledge/django-ripozo) 
with minimal deviations from this tutorial.
Unfortunately, bootstrapping a django project requires more than 10 lines of code.

First, install Flask.

```bash
pip install Flask
```

Now instantiate a Flask Application.

```python
from flask import Flask
app = Flask(__name__)
```

### Step 2: Setup SQLAlchemy

[SQLAlchemy](http://www.sqlalchemy.org/) is another favorite tool of mine.  It provides
an excellent ORM and allows us to generate an ORM from an existing database
with no additional work.

```bash
pip install SQLAlchemy
```

Creating a sqlalchemy engine is incredibly simple.  We simply
pass SQLAlchemy a database URI in the expected format.  See
the [Engine Configuration documentation](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html)
for more details. TL;DR this is the general format: 
`'dialect+driver://username:password@host:port/database_name'`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

database_uri = 'mysql://localhost:3306/mydatabase'
engine = create_engine(database_uri)
base = automap_base()
base.prepare(engine, reflect=True)
```

This creates an ORM where we can access tables in the database
as python objects.

### Step 3: Bind ripozo

Now that we have our database and web application working, we need to bind 
[ripozo](https://github.com/vertical-knowledge/ripozo) to Flask and SQLAlchemy.

```bash
pip install ripozo flask-ripozo ripozo-sqlalchemy
```

```python
from flask_ripozo import FlaskDispatcher
from ripozo import adapters
from ripozo_sqlalchemy import ScopedSessionHandler

# Attach the previously create Flask application
dispatcher = FlaskDispatcher(app)
# Adapters inform ripozo how to represent the resources over HTTP (typically a
# protocol for a JSON response).  In this case, we've chosen the Hal and SIREN protocols.
dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)
# Create a session handler to cleanly handle database transactions and cleanup
session_handler = ScopedSessionHandler(engine)
```

### Step 4: Expose our database

Now that we have completed all necessary setup, we can
expose our database as a ReSTful API.

```python
# The create_resource method is a shortcut for creating ripozo resources 
# containing common sets of endpoints.
# We need to pass append_slash=True due to a quirk in how flask handles routing
resources = [create_resource(model, session_handler, append_slash=True) for model in base.classes]
# Register the resources with the adapter to expose them in the API.
dispatcher.register_resources(*resources)

# and now we run our Flask app
app.run()
```

The ``create_resource`` method is highly customizable.  Additionally, you can use a
declarative, class based implementation that is incredibly flexible.  In fact,
the ``create_resource`` method uses the declarative implementation under the covers.

### Step 5: Putting it all together

Now that we have everything we need, let's put it all together
into one function.

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
    dispatcher.register_adapters(adapters.HalAdapter, adapters.SirenAdapter)
    session_handler = ScopedSessionHandler(engine)

    resources = [create_resource(model, session_handler, append_slash=True) for model in base.classes]
    dispatcher.register_resources(*resources)
    
    app.run()
```

And just like that we have exposed our database as a ReSTful API.  Additionally,
because this is [ripozo](https://github.com/vertical-knowledge/ripozo), if a table
has a relationship to another table, a link to the corresponding row/resource is 
automatically generated.  For example, consider a user table has a Many-to-One relationship with a group table.
When we go to a user's endpoint, we'll get a fully qualified URL linking to the associated group's endpoint.


## Conclusion

We can see how easy [ripozo](https://github.com/vertical-knowledge/ripozo) makes
creating ReSTful API's.  With [ripozo](https://github.com/vertical-knowledge/ripozo),
you can include authentication and authorization, additional endpoints and much more.
[Ripozo](https://github.com/vertical-knowledge/ripozo) is designed to be flexible and 
efficient at the same time.  It provides shortcuts
while priotizing extensibility.  It unleashes more flexibility and power than 
any other Hypermedia/HATEOAS ReSTful framework.  Ripozo: less effort, better APIs. 

