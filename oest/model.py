""" """
import formencode
import thredis


# TODO: Extend the basic validator types.
#       Use codalib code as well.
class LocationGetSchema(formencode.schema.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    id = formencode.validators.String(min=36, max=36)


class LocationUpdateSchema(LocationGetSchema):
    allow_extra_fields = True
    filter_extra_fields = True

    key = formencode.validators.String(min=1, max=16, not_empty=True, lower=True, if_missing=None)
    display = formencode.validators.UnicodeString(min=3, max=64, not_empty=True, if_missing=None)
    description = formencode.validators.UnicodeString(min=5, max=1024, if_missing=None)


class Location(thredis.Collection):
    get_schema = LocationGetSchema
    update_schema = LocationUpdateSchema

    def __init__(self, session):
        self.modelspace = self.__class__.__name__.lower()
        thredis.Collection.__init__(self, self.modelspace, session=session)
    '''
    # This can all be wrapped to include the Schema.
    # Possibly use a map dict.
    # Also standardize errors.
    def add(self, obj):
        try:
            obj = self._update_schema.to_python(obj)
        except formencode.Invalid:
            return {'status': '500', 'status_text': 'Validation failed.'}
        else:
            thredis.Collection.add(self, obj)
            return obj'''