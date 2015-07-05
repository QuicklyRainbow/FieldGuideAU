VERSION = (1, 0, 0, 'final', 2)


def get_version(version=None):
    version = version or VERSION

    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #  | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join('{0}'.format(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        sub = '.dev'

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = '{0}{1}'.format(mapping[version[3]], version[4])

    # see http://bugs.python.org/issue11638 - .encode('ascii')
    return '{0}{1}'.format(main, sub)

# we might be run from setup.py during setup :)
try:
    from flask import Flask
except ImportError:
    pass
else:
    from Flask_App import settings

    app = Flask(__name__)
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    # Initialise logging
    import os
    import logging

    defaults = {
            'level': logging.DEBUG,
            'format': "%(relativeCreated)d %(levelname)s: %(message)s"
        }
    handler = logging.basicConfig(**defaults)
    app.logger.addHandler(handler)


    # ---Initialise extensions here---

    # SQLAlchemy for easy database access
    from flask.ext.sqlalchemy import SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    db = SQLAlchemy(app)
    db_session = db.session

    # Admin for easy access to the data in the database
    from flask.ext.admin import Admin
    admin = Admin(app)

    # Register the endpoints for the app
    from Flask_App.controllers.admin_interfaces import *
    from Flask_App.controllers.custom_interfaces import *
