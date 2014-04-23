""" """
import logging
import uuid
import formencode
import thredis
import thredis.model


# General, maybe in `thredis.schema`
class ModelObject:
    modelspace = 'model'

    def __init__(self, session):
        self.s = session
        self.models = dict(self.__build_models())

    def __build_models(self):
        for name, ModelCls in self.schema.items():
            yield name, ModelCls(self.modelspace,
                                    ModelCls.__name__.lower(),
                                    name, session=self.s)

    def _get_model(self, modelname):
        if modelname in self.models:
            return self.models[modelname]



# TODO: Extend the basic validator types.
#       Use codalib code as well.
class LocationGetSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    _id = formencode.validators.String(min=36, max=36)


class LocationCreateSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    key = formencode.validators.String(min=1, max=16, not_empty=True, lower=True, if_missing=None)
    name = formencode.validators.UnicodeString(min=3, max=64, not_empty=True, if_missing=None)
    desc = formencode.validators.UnicodeString(min=5, max=1024, not_empty=False, if_missing=None)


class LocationUpdateSchema(formencode.schema.Schema):
    # Unfortunate duplicate as inheritance doesn't seem to be working anymore.
    # Update if you change anything above/
    # TODO: Dig in to inheritance issues with formencode Scheme or this
    #   implementation of them.
    allow_extra_fields = True
    filter_extra_fields = True

    _id = formencode.validators.String(min=36, max=36)
    key = formencode.validators.String(min=1, max=16, not_empty=True, lower=True, if_missing=None)
    name = formencode.validators.UnicodeString(min=3, max=64, not_empty=True, if_missing=None)
    desc = formencode.validators.UnicodeString(min=5, max=1024, not_empty=False, if_missing=None)


class ZipCodeSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    zip_id = formencode.validators.Int(min=90000, max=99999)


class LocationZipCodeGetSchema(LocationGetSchema, ZipCodeSchema):
    pass





class Location(ModelObject):
    """
    """

    modelspace = 'location'
    id_attr = '_id'

    get_schema = LocationGetSchema
    create_schema = LocationCreateSchema
    update_schema = LocationUpdateSchema

    schema = {
            'all': thredis.model.Set,
            'active': thredis.model.Set,
            'record': thredis.model.Hash
            }

    @staticmethod
    def _ingress(obj):
        obj['_id'] = uuid.UUID(obj['_id'])

        return obj

    @staticmethod
    def _egress(obj):
        obj['_id'] = str(obj['_id'])

        return obj

    def _retrieve(self, location_id):
        record = self.models['record']
        return self._egress(record.get(location_id))
    retrieve = _retrieve

    def _update(self, **obj):
        active = self.models['active']
        every = self.models['all']
        record = self.models['record']

        obj = self._ingress(obj)

        print(obj)

        if '_active' in obj:
            if obj['_active'] is True:
                active.add(obj['_id'])
            else:
                active.delete(obj['_id'])

        if '_id' in obj:
            every.add(obj['_id'])
            record.set(obj['_id'], obj)
        else:
            raise Exception("model update requires _id value")

    update = _update

    def all(self, **obj):
        # Let's get in to the "location:active:set"
        logging.debug('Model all! obj: %s' % obj)
        record = self.models['record']

        if obj.get('active') is True:
            active = self.models['active']
            return [self.retrieve(id_) for id_ in active.all()]
        else:
            every = self.models['all']
            return [self.retrieve(id_) for id_ in every.all()]

    def create(self, **obj):
        obj['_id'] = uuid.uuid4()
        obj['_active'] = True
        self.update(**obj)
        return obj

    def delete(self, location_id):
        obj['_id'] = location_id
        obj['_active'] = False
        self.update(**obj)




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