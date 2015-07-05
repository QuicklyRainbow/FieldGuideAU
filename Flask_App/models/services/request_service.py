__author__ = 'Lachlan'

from Flask_App.utils.models.data_uuid_service import DataUUIDService
from Flask_App.models.db_models import Request

class RequestService(DataUUIDService):

    def __init__(self, db):
        super(RequestService, self).__init__(db)
        self.tablename = Request
        self.key = ''
        self.valid_fields = ['uuid', 'time', 'person']