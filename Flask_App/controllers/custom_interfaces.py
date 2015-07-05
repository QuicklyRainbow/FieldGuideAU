__author__ = 'lachlan'

import logging
import json
logger = logging.getLogger(__name__)

from flask import abort, jsonify, Response, redirect, url_for, request, render_template, flash
from Flask_App import app, db_session
from Flask_App.models.services.request_service import RequestService
from Flask_App.models.services.thing_service import ThingService

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/request/<uuid>')
def serve_request(uuid):
    req_service = RequestService(db_session)
    try:
        req = req_service.get_by_uid(uuid)
        user_name = json.loads(req.person)
        user_name = '@' + user_name['user']['screen_name']
    except Exception as e:
        pass

    if req is None:
        abort(404)
    else:
        return render_template('request.html', user_request=req, user_name=user_name)

