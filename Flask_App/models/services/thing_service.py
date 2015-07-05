__author__ = 'Lachlan'

from Flask_App.utils.models.data_uuid_service import DataUUIDService
from Flask_App.models.db_models import Thing

class ThingService(DataUUIDService):

    def __init__(self, db):
        super(ThingService, self).__init__(db)
        self.tablename = Thing
        self.key = ''
        self.valid_fields = ['uuid', 'name', 'image_url', 'description', 'description_url', 'request']