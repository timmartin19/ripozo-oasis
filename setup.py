from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import setup, find_packages

version = '1.0.1'

setup(
    author='Tim Martin',
    author_email='tim.martin@vertical-knowledge.com',
    entry_points={
        'console_scripts': [
            'ripozo-oasis = ripozo_oasis.cli_commands:run_commands'
        ]
    },
    extras_require={
        'dev': [
            'zest.releaser'
        ]
    },
    install_requires=[
        'click==5.1',
        'Flask==0.10.1',
        'ripozo==1.2.3',
        'flask-ripozo==1.0.1',
        'ripozo-sqlalchemy==1.0.1',
        'SQLAlchemy==1.0.9'
    ],
    name='ripozo-oasis',
    packages=find_packages(include=['ripozo_oasis', 'ripozo_oasis.*']),
    version=version
)
