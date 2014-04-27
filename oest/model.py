""" """
import logging
import uuid
import formencode
import thredis.model


# TODO: Do the conversion in backbone and just sent lists of zips.
class ZipValidator(formencode.validators.FancyValidator):
    min = 5
    max = 1024

    subval = formencode.validators.Int(min=90000, max=99999)
    if_empty = tuple()
    def _convert_to_python(self, value, state):
        print("ZipValidator Convert to")
        value = value or ''

        def extract_string():
            for zip_ in value.split(','):
                if zip_:
                    yield self.subval._convert_to_python(zip_, state)

        return tuple(extract_string())

    def _validate_python(self, value, state):
        print("ZipValidator Validate")
        assert isinstance(value, tuple)
        for zip_ in value:
            self.subval.validate_python(zip_, state)


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
    zips = ZipValidator()


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
    zips = ZipValidator()


'''
class ZipCodeSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    zip_id = formencode.validators.Int(min=90000, max=99999)


class ZipCodesSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    zips = formencode.validators.String(min=5, max=1024)

    def _to_python(self, value_dict, state):
        #valid??
        print("ZipCodesSchema._to_python()")
        zips = value_dict.get('zips')
        if zips:
            value_dict['zips'] = (
                ZipCodeSchema.to_python(zip_) for zip_ in zips.split(','))
        return value_dict


class LocationZipCodeGetSchema(LocationGetSchema, ZipCodeSchema):
    pass
'''

#Submodel
class LocationZipCode(thredis.model.SubModelObject):
    modelspace = 'zips'
    id_attr = '_id'

    def model(self, id_):
        return thredis.model.Set(self.namespace, 'set', str(id_),
                                 session=self.s)

    def retrieve(self, id_):
        return self.model(id_).all()

    def update(self, id_, *objs):
        print ('LocationZipCode.update(%s, *%s)' % (id_, objs))
        ziplocation_model = ZipCodeLocation(session=self.s)
        current_model = self.model(id_)

        # Check for any of these zips in other locations, otherwise add
        #   it to the location.
        # Constraint.
        for zip_ in objs:
            location_id = ziplocation_model.retrieve(zip_)
            if location_id and location_id != id_:
                location_obj = self.supermodel.retrieve(location_id)
                print("Deleting %s from %s" % (zip_, location_obj['name']))
                self.model(location_id).delete(zip_)

                #location_obj = self.supermodel.retrieve(location_id)
                #raise thredis.model.UniqueFailed("This zip '%s' is already "
                #    "applied to Location '%s'." % (zip_, location_obj['name']))

        # Check for removed Zips
        #objs_set = set(objs)
        for delete_zip in current_model.all() - set(objs):
            ziplocation_model.delete(delete_zip)
            current_model.delete(delete_zip)
            #print("Delete %s" % delete)


        ziplocation_model.update(id_, *objs)
        current_model.add(*objs)

    def delete(self, id_, *objs):
        self.model(id_).delete(*objs)


class ZipCodeLocation(thredis.model.ModelObject):
    modelspace = 'zip'

    def model(self, zip_):
        return thredis.model.String(self.namespace, 'string', str(zip_),
                session=self.s)

    def retrieve(self, zip_):
        return self.model(zip_).get()

    def update(self, location_id, *zips):
        print("ZipCodeLocation.update(%s, *%s)" % (location_id, zips))
        for zip_ in zips:
            self.model(zip_).set(location_id)

    def delete(self, zip_):
        self.model(zip_).delete()




class Location(thredis.model.Record):
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

    unique = {'key', 'name'}

    child_models = {'zips': LocationZipCode}


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