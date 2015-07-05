#!/usr/bin/env python

import os
import logging

__author__ = 'lachlan'

from Flask_App import app

logger = logging.getLogger(__name__)

logger.info('Flask Service Starting')

app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000),
        debug=os.environ.get('DEBUG', False))
