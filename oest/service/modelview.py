import formencode
import thredis
import oest.model

# Decorators

def validate_model(params=None, match=None):
    """Basic validation decorator for usage in `view_config`.

    Takes `params` and `match` as arguments. 
        `params` - Schema to use to and instruct to validate requests.params
        `match` - Schema to use to and isntruct to validate request.match
    """
    
    if params is None and match is None: # Validate the usage of the validator!
        raise ValueError("`validate` expected a `params` schema or a `match` "
                            "schema.")
    if params and not issubclass(params, Schema):
        raise ValueError("`params` expected a `formencode.Schema` type.")
    if match and not issubclass(match, Schema):
        raise ValueError("`match` expected a `formencode.Schema` type.")

    def _decorator(view_callable):
        def _inner(context, request):
            def validate_params(this):
                try:
                    data = request.json_body or request.params
                    return params.to_python(data)
                except Invalid as e:
                    log.error("`validate` failed on request.params %s. Error: %s" % (data, e.msg))
                    raise exc.HTTPBadRequest()

            def validate_match(this):
                try:
                    return match.to_python(request.matchdict)
                except Invalid:
                    log.error("`validate` failed on request.matchdict %s." % request.matchdict)
                    raise exc.HTTPNotFound()

            if params:
                request.set_property(validate_params, 'validated_params',
                                        reify=True)
            if match:
                request.set_property(validate_match, 'validated_matchdict',
                                        reify=True)
            return view_callable(context, request)
        return _inner
    return _decorator


def execute_model(view_callable):
    """Decorator """
    def execute_pipe(request):
        redis = request.registry.settings['redis']
        redis.execute()

    def _execute_model(context, request):
        request.add_finished_callback(execute_pipe)
        return view_callable(context, request)

    return _execute_model


# Utility
get_redis = lambda request: request.registry.settings['redis']


class ModelView:
    """
    """
    __bound_methods = ('all', 'get', 'add', 'update', 'delete')
    
    def __init__(self, model_class):
        if issubclass(model, thredis.RedisObj)
            self.__model_class = model_class
        else:
            raise ValueError("`Model` requires a RedisObj class for an argument.")

    def __bind_methods(self):
        # Decorate and add "bind" to all methods.
        for attr in self.__bound_methods:
            val = getattr(self, attr)
            if not attr.starswith('_') and callable(val, function):
                def bind(self, request):
                    model = self.__model_class(get_redis(request))
                    return val(self, model, request)
                self[attr] = bind

    def config(self, config):
        # TODO: Add permissions!
        config.add_route(self.modelspace+'_all', '/')
        config.add_route(self.modelspace+'_add', '/')
        config.add_route(self.modelspace+'_get', '/{id}')
        config.add_route(self.modelspace+'_update', '/{id}')
        config.add_route(self.modelspace+'_delete', '/{id}')

        config.add_view(self.all,
                        route_name='location_all',
                        request_method='GET',
                        renderer='json')
        config.add_view(self.get,
                        route_name='location_get',
                        request_method='GET',
                        renderer='json',
                        decorator=(validate_model(match=self.get_schema),))
        config.add_view(self.add,
                        route_name='location_add',
                        request_method='POST',
                        renderer='json',
                        decorator=(validate_model(match=self.get_schema,
                                                  params=self.update_schema),
                                   execute_model))
        config.add_view(self.update,
                        route_name='location_update',
                        request_method='PUT',
                        renderer='json',
                        decorator=(validate_model(match=self.get_schema,
                                                  params=self.update_schema),
                                   execute_model))
        config.add_view(self.delete,
                        route_name='location_delete',
                        request_method='DELETE',
                        renderer='json',
                        decorator=(validate_model(match=self.get_schema),))


    # Views
    def all(self, model, request):
        return list(model.all())

    def get(self, model, request):
        id_ = request.validated_matchdict['id']
        return model.get(id_)

    def add(self, model, request):
        return model.add(request.json_body)

    def update(self, model, request):
        id_ = request.validated_matchdict['id']
        return model.add(request.json_body, id=id_)

    def delete(self, model, request):
        id_ = request.validated_matchdict['id']
        return model.delete(id_)