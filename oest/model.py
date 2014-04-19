""" """
import logging
import formencode
import thredis


# TODO: Extend the basic validator types.
#       Use codalib code as well.
class LocationGetSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    id = formencode.validators.String(min=36, max=36)


class LocationUpdateSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    id = formencode.validators.String(min=36, max=36, if_missing=None)
    key = formencode.validators.String(min=1, max=16, not_empty=True, lower=True, if_missing=None)
    name = formencode.validators.UnicodeString(min=3, max=64, not_empty=True, if_missing=None)
    desc = formencode.validators.UnicodeString(min=5, max=1024, not_empty=False, if_missing=None)


class ZipCodeSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    zip_id = formencode.validators.Int(min=90000, max=99999)


class LocationZipCodeGetSchema(LocationGetSchema, ZipCodeSchema):
    pass


class ModelObject:
    modelspace = 'model'

    def __init__(self, session):
        self.s = session
        self.r = RedisObj(self.modelspace, session=session)


class Location(ModelObject):
    """
    """
    get_schema = LocationGetSchema
    update_schema = LocationUpdateSchema
    modelspace = 'location'

    def all(self, **obj):
        logging.debug('Model all!')
        # Let's get in to the "location:active:set"


        if 'active' in obj:
            pass
        else:
            pass

        return []


    def create(self, **obj):
        logging.debug('Model create!')

    def retrieve(self, location_id):
        logging.debug('Model retrieve!')

    def update(self, **obj):
        logging.debug('Model update!')

    def delete(self, location_id):
        logging.debug('Model delete!')



'''
class ZipCode(thredis.String):
    get_schema = ZipCodeSchema
    update_schema = ZipCodeSchema
    modelspace = 'zip'

    def __init__(self, session, *args):
        thredis.String.__init__(self, self.modelspace, *args, session=session)
'''

'''
# Old Model. Too abstracted and couldn't deliver.
# Pragmatism for now.
class Location(object):
    get_schema = LocationGetSchema
    update_schema = LocationUpdateSchema
    modelspace = 'location'
    id_attr = 'location_id'

    def __init__(self, session, *args):
        thredis.Collection.__init__(self, self.modelspace, *args,
                                    session=session)
        
    # Aliases that view expects.
    def create(self, **obj):
        return thredis.Collection.add(self, obj)

    def retrieve(self, location_id=None):
        return  thredis.Collection.get(self, location_id)

    def update(self, **obj):
        return thredis.Collection.add(self, obj)

    def delete(self, location_id=None):
        thredis.Collection.delete(self, location_id)
'''