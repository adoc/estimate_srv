"""Online Estimator Object Models.
"""
import logging
logger = logging.getLogger(__name__)


import formencode
import thredis.primal
import thredis.model


# TODO: Do the conversion in backbone and just sent lists of zips.
class ZipValidator(formencode.validators.FancyValidator):
    # This should be validating for both a comma delimited list of zips and
    # for a single zip.
    min = 5
    max = 1024

    subval = formencode.validators.Int(min=90000, max=99999)
    if_empty = tuple()
    def _convert_to_python(self, value, state):
        # Accept comma delimited string of zip codes. Return as tuple.
        value = value or ''

        def extract_string():
            for zip_ in value.split(','):
                if zip_:
                    yield self.subval._convert_to_python(zip_, state)

        return tuple(extract_string())

    def _validate_python(self, value, state):
        # Validate the tuple of zip codes.
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

    key = formencode.validators.String(min=1, max=16, not_empty=True, lower=True)
    name = formencode.validators.UnicodeString(min=3, max=64, not_empty=True)
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


class ZipLocationSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    zip = formencode.validators.Int(min=90000, max=99999)


class LocationZipCode(thredis.model.SubModelObject):
    modelspace = 'zips'
    id_attr = '_id'

    def model(self, id_):
        return thredis.primal.Set(self.namespace, 'set', str(id_),
                                 session=self.s)

    def retrieve(self, id_):
        key, val = self.model(id_).all()
        return val

    def update(self, id_, *objs):
        print ('LocationZipCode.update(%s, *%s)' % (id_, objs))
        ziplocation_model = ZipCodeLocation(session=self.s)
        current_model = self.model(id_)

        # Check for any of these zips in other locations, otherwise add
        #   it to the location.
        # Constraint.
        for zip_ in objs:
            location = ziplocation_model.retrieve(zip=zip_)
            if location:
                location_id = location['_id']
                if location_id and location_id != id_:
                    location_obj = self.supermodel.retrieve(location_id)
                    print("Deleting %s from %s" % (zip_, location_obj['name']))
                    self.model(location_id).delete(zip_)

                    #location_obj = self.supermodel.retrieve(location_id)
                    #raise thredis.model.UniqueFailed("This zip '%s' is already "
                    #    "applied to Location '%s'." % (zip_, location_obj['name']))

        # Check for removed Zips
        #objs_set = set(objs)
        key, values = current_model.all()
        for delete_zip in values - set(objs):
            ziplocation_model.delete(delete_zip)
            current_model.delete(delete_zip)
            print("Delete %s" % delete_zip)

        if objs:
            ziplocation_model.update(id_, *objs)
            current_model.add(*objs)

    def delete(self, id_, *objs):
        self.model(id_).delete(*objs)


class ZipCodeLocation(thredis.model.ModelObject):
    """
    """
    modelspace = 'zip'
    id_attr = 'zip'

    get_schema = ZipLocationSchema
    update_schema = ZipLocationSchema

    def model(self, zip_):
        return thredis.primal.String(self.namespace, 'string', str(zip_),
                                     session=self.s)

    def retrieve(self, **obj):
        key, val = self.model(obj['zip']).get()
        return Location(session=self.s).retrieve(val)

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
            'all': thredis.primal.Set,
            'active': thredis.primal.Set,
            'record': thredis.primal.Hash
            }

    unique = {'key', 'name'}

    child_models = {'zips': LocationZipCode}

    def all(self, **obj):
        obj['active_only'] = False
        return thredis.model.Record.all(self,**obj)