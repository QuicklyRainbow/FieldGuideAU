import uuid

from Flask_App.utils.models.data_service import DataService, ServiceLayerError


__author__ = 'lachlan'

class DataUUIDService(DataService):

    def __init__(self, db):
        super(DataUUIDService, self).__init__(db)
        self.bad_keys.append('uuid')

    def create_server_side_fields(self, **fields):
        # create a uuid for this record
        uid = uuid.uuid4()
        fields['uuid'] = str(uid) # This ensures that a fake uuid cant be sent up
        return fields

    def get_by_uid(self, uid):
        try:
            req = self.db.query(self.tablename).filter(self.tablename.uuid == uid).first()
            if req ==[]:
                return None
            else:
                return req
        except Exception as e:
            self.logger.error("Error occurred while retrieving record by uuid with error msg: %s" % (str(e)))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while retrieving record by uuid with error msg: %s" % (str(e)))