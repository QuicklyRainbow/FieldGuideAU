__author__ = 'lachlan'

import logging

class ServiceLayerError(Exception):
    pass

class DataService(object):
    def __init__(self, db_session):
        self.db = db_session
        self.tablename = None
        self.bad_keys = ['id']  # Fields that should not be created or updated using uploaded data. They need to be created server side.
        self.valid_fields = []  # Fields that can be updated using uploaded data
        self.relationship_fields = {}  # Fields that describe relationships with other objects (i.e. other database tables)
        self.has_version_management = False
        self.logger = logging.getLogger(__name__)
        self.key = ''


    def create(self, **fields):
        fields = self.create_server_side_fields(**fields)
        try:
            direct_fields = {}
            for key in self.valid_fields:
                if key in fields.keys():
                    direct_fields[key] = fields.pop(key)
            record = self.tablename(**direct_fields)
            for key in self.relationship_fields.keys():
                if key in fields.keys():
                    service_layer = self.relationship_fields[key]['service'](self.db)
                    if self.relationship_fields[key]['many']:
                        for item_id in fields.pop(key):
                            item_obj = service_layer.get_one(int(item_id))
                            getattr(record, key).append(item_obj)
                    else:
                        item_id = fields.pop(key)
                        item_obj = service_layer.get_one(int(item_id))
                        setattr(record, key, item_obj)
            if len(fields.keys()) is 0:
                self.db.add(record)
                self.db.commit()
                return self.get_one(record.id)
            else:
                raise ServiceLayerError("Surplus keys detected while creating record")
        except Exception as e:
            self.logger.error("Error occurred while creating record with error msg: %s" % (str(e)))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while creating record with error msg: %s" % (str(e)))

    def update(self, id, **fields):
        if self.exists(id):
            try:
                for key in self.bad_keys:
                    if key in fields.keys():
                        del fields[key]

                direct_fields = {}
                for key in self.valid_fields:
                    if key in fields.keys():
                        direct_fields[key] = fields.pop(key)

                if len(direct_fields.keys()) > 0:
                    self.db.query(self.tablename).filter(self.tablename.id == id).update(direct_fields)
                record = self.get_one(id)
                for key in self.relationship_fields.keys():
                    if key in fields.keys():
                        service_layer = self.relationship_fields[key]['service'](self.db)
                        if self.relationship_fields[key]['many']:
                            setattr(record, key, [])
                            for item_id in fields.pop(key):
                                item_obj = service_layer.get_one(int(item_id))
                                getattr(record, key).append(item_obj)
                        else:
                            item_id = fields.pop(key)
                            item_obj = service_layer.get_one(int(item_id))
                            setattr(record, key, item_obj)
                if len(fields.keys()) is 0:
                    self.db.add(record)
                    self.db.commit()
                    return self.get_one(record.id)
                else:
                    raise ServiceLayerError("Surplus keys detected while updating record")
            except Exception as e:
                self.logger.error("Error occurred while updating record with error msg: %s" % (str(e)))
                self.db.rollback()
                raise ServiceLayerError("Error occurred while updating record with error msg: %s" % (str(e)))
        else:
            raise ServiceLayerError()


    def get_one(self, id):
        try:
            if self.exists(id):
                return self.db.query(self.tablename).get(id)
            else:
                return None
        except Exception as e:
            self.logger.error("Error occurred while retrieving individual record with error msg: %s" % (str(e)))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while retrieving individual record with error msg: %s" % (str(e)))

    def get_many(self):
        try:
            req = self.db.query(self.tablename).all()
            if req == []:
                return None
            else:
                return req
        except Exception as e:
            self.logger.error("Error occurred while retrieving multiple records with error msg: %s" % (str(e)))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while retrieving multiple records with error msg: %s" % (str(e)))

    def delete(self, id):
        try:
            if self.exists(id):
                record = self.get_one(id)
                self.db.delete(record)
                self.db.commit()
                return record
            else:
                return None
        except Exception as e:
            self.logger.error("Error occurred while deleting record with error msg: %s" % (str(e)))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while deleting record with error msg: %s" % (str(e)))

    def exists(self, id):
        if self.db.query(self.tablename).get(id) == None:
            return False
        else:
            return True


    def get_by_name(self, name):
        key = '{0}_name'.format(self.key)
        try:
            req = self.db.query(self.tablename).filter(getattr(self.tablename, key) == name).first()
            if req is None:
                return None
            else:
                return req
        except Exception as e:
            self.logger.error("Error occurred while retrieving individual record by name: {0} with error msg: {1}".format(name, e))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while retrieving individual record by name: {0} with error msg: {1}".format(name, e))

    def get_id_by_name(self, name):
        try:
            req = self.get_by_name(name)
            if req is None:
                return None
            else:
                return req.id
        except Exception as e:
            self.logger.error("Error occurred while retrieving individual record id by name: {0} with error msg: {1}".format(name, e))
            self.db.rollback()
            raise ServiceLayerError("Error occurred while retrieving individual record id by name: {0} with error msg: {1}".format(name, e))


    def update_or_create(self, **fields):
        key = '{0}_name'.format(self.key)

        if key in fields.keys():
            try:
                id = self.get_id_by_name(fields[key])
                if id is None:
                    return self.create(**fields)
                else:
                    return self.update(id, **fields)
            except Exception as e:
                self.logger.error("Error occurred in update or create with data: {0} and error msg: {1}".format(fields, e))
                self.db.rollback()
                raise ServiceLayerError("Error occurred in update or create with data: {0} and error msg: {1}".format(fields, e))
        else:
            return None



    def create_server_side_fields(self, **fields):
        return fields

    def update_server_side_fields(self, **fields):
        return fields