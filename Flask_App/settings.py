import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.urandom(24)

DATABASE_URL = os.environ.get(
    'DATABASE_URL', 'sqlite:///{0}'.format(os.path.join(ROOT_DIR,
                                                        'sqlite_data.db'))
)

