web: gunicorn -w 1 -b '0.0.0.0:$PORT' Flask_App:app
worker: python scripts/twitter_stream_listener.py
init: python scripts/init_db.py