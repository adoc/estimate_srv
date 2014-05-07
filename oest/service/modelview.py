import logging
import formencode
import posixpath
import urllib.parse
import thredis
import thredis.model
import pyramid.config
import pyramid.httpexceptions
import pyramid.response
import oest.model

# Decorators
# This is more of a general function. we should put this in gist.
def validate_model(params=None, match=None, headers=lambda r: tuple()):
    """Basic validation decorator for usage in `view_config`.

    Takes `params` and `match` as arguments. 
        `params` - Schema to use to and instruct to validate requests.params
        `match` - Schema to use to and isntruct to validate request.match
    """
    
    if params is None and match is None: # Validate the usage of the validator!
        raise ValueError("`validate_model` expected a `params` schema or a `match` "
                            "schema.")

    # Check to see if Validator works as well.
    if params and issubclass(params, (formencode.Schema, formencode.FancyValidator)):
        params = params()
    elif params is not None:
        raise ValueError("`params` expected a `formencode.Schema` type.")

    if match and issubclass(match, (formencode.Schema, formencode.FancyValidator)):
        match = match()
    elif match is not None:
        raise ValueError("`match` expected a `formencode.Schema` type.")

    def _decorator(view_callable):
        def _inner(context, request):
            def validate_params(this):
                data = request.json_body or request.params
                try:
                    data = params.to_python(data)
                    print("Validate params %s " % data)
                    return data
                except formencode.Invalid as e:
                    logging.error("`validate_model` failed on request.params %s. Error: %s" % (data, e.msg))
                    raise pyramid.httpexceptions.HTTPBadRequest(headers=headers(request),
                                                                body=thredis.json.dumps({'msg': e.unpack_errors()}))

            def validate_match(this):
                try:
                    return match.to_python(request.matchdict)
                except formencode.Invalid:
                    logging.error("`validate_model` failed on request.matchdict %s." % request.matchdict)
                    raise pyramid.httpexceptions.HTTPNotFound(headers=headers(request),
                                                              body=thredis.json.dumps({'msg': e.unpack_errors()}))

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


class DictSets:
    """ """
    def __init__(self):
        self.__inner = {}

    def add(self, key, method):
        item = self.__inner.get(key, set())
        item.add(method)
        self.__inner[key] = item

    def __getitem__(self, key):
        return self.__inner[key]

    def __setitem__(self, key, val):
        self.__inner[key] = set(val)

    def __delitem__(self, key):
        del self.__inner[key]

    def __contains__(self, key):
        return key in self.__inner


class CrudConfigurator:
    """ """
    def __init__(self, config, route_prefix='', route_name_func=None):
        self.config = config
        self.route_prefix = route_prefix
        if callable(route_name_func):
            self._gen_route_name = lambda ns: route_name_func(ns)
        else:
            self._gen_route_name = lambda ns: ns
        self._added_methods = DictSets()
        self._allowed_headers = ['Content-Type']

    # The magic sauce in "CORS". Though this will need to be dyanimcally generated.
    def headers(self, request):
        # Consider these headers:
        # X-CSRF-Token
        # X-Requested-With
        # Accept
        # Accept-Version
        # Content-Length
        # Content-MD5
        # Content-Type
        # Date
        # X-Api-Version
        added_methods = self._added_methods[request.matched_route.pattern]
        headers = [
            # Always creds?
            ('Access-Control-Allow-Credentials', 'true'),
            ('Access-Control-Allow-Headers', ','.join(self._allowed_headers)),
            ('Access-Control-Allow-Methods', ','.join(added_methods))]
        # At first glance, this may appear insecure, but if the referer
        # should be checked, it should be checked elsewhere.
        if request.referer:
            refp = urllib.parse.urlparse(request.referer)
            origin = urllib.parse.urlunparse((refp.scheme, refp.netloc, '', '', '', ''))

            headers.append(('Access-Control-Allow-Origin', origin))
            #headers.append(('Access-Control-Allow-Origin', request.referer.rstrip('/')))
            #headers.append(('Access-Control-Allow-Origin', request.referer))
        return headers

    def auth_origin(self, view_callable):
        """Decorator """
        def _auth_origin(context, request):
            request.response.headers.update(self.headers(request))
            return view_callable(context, request)
        return _auth_origin

    def add_route_view(self, request_method, view_callable,
                        route_namespace=None, route_postfix='', decorators=()):
        request_method = request_method.upper()
        route_name = self._gen_route_name(route_namespace or
                                            request_method.lower())

        if route_postfix:
            route_prefix = posixpath.join(self.route_prefix, route_postfix)
        else:
            route_prefix = self.route_prefix

        logging.debug("Add %s Route: name: %s, prefix: %s" % (request_method,
                        route_name, route_prefix))
        self.config.add_route(route_name, route_prefix, request_method=request_method)
        self.config.add_view(view_callable,
                        route_name=route_name,
                        decorator=(self.auth_origin,)+decorators,
                        renderer='json')
        self._added_methods.add(route_prefix, request_method)


class ModelViews:
    """An adapter between RedisObj Model and it's relevant Pyramid
    Views.
    """
    def __init__(self, model_class, config=None):
        if issubclass(model_class, thredis.model.ModelObject):
            self.__model_class = model_class
        else:
            raise ValueError("`Model` requires a ModelObject class for an argument.")

        if config is not None:
            self.config(config)

    @property
    def modelspace(self):
        return self.__model_class.modelspace

    @property
    def get_schema(self):
        return self.__model_class.get_schema

    @property
    def create_schema(self):
        return self.__model_class.create_schema

    @property
    def update_schema(self):
        return self.__model_class.update_schema

    def bind(self, request):
        return self.__model_class(session=get_redis(request))

    def build_obj(self, request):
        """Builds an input object based on validated match and
        parameters.
        """
        obj = {}

        if hasattr(request, 'validated_params'):
            obj.update(request.validated_params)
        if hasattr(request, 'validated_matchdict'):
            obj.update(request.validated_matchdict)
        return obj

    def config(self, config, route_prefix=''):
        if not isinstance(config, pyramid.config.Configurator):
            raise ValueError('`Model.config` requires argument to be a Pyramid '
                             'Configurator.')

        def _gen_route_name(ns):
            return '_'.join([self.modelspace, ns])

        config = CrudConfigurator(config, route_prefix=route_prefix,
                    route_name_func=_gen_route_name)

        id_attr = self.__model_class.id_attr
        id_pattern = '{%s}' % id_attr

        def null_action(this, request):
            return request.response

        def model_action(action_name):
            """Hook in to model actions with this decorator. The inner
            function acts as the view_callable."""
            def _model_action(this, request):
                #TODO: Let's deal with query args!
                model = self.bind(request)
                obj = self.build_obj(request)
                action = getattr(model, action_name)
                try:
                    return action(**obj)
                except thredis.model.ConstraintFailed as e:
                    request.response.status = 400
                    return {'errors': str(e)}
                else:
                    raise

            return _model_action

        def add_all():
            config.add_route_view('GET', model_action('all'),
                                    route_namespace='all')

        def add_create():
            config.add_route_view('POST', model_action('create'), 
                    route_namespace='create',
                    decorators=(validate_model(match=self.get_schema,
                                               params=self.create_schema,
                                               headers=config.headers),
                                execute_model))

        def add_retrieve():
            config.add_route_view('GET', model_action('retrieve'),
                    route_namespace='retrieve', route_postfix=id_pattern,
                    decorators=(validate_model(match=self.get_schema,
                                               headers=config.headers),))

        def add_update():
            config.add_route_view('PUT', model_action('update'),
                    route_namespace='update', route_postfix=id_pattern,
                    decorators=(validate_model(match=self.get_schema,
                                               params=self.update_schema,
                                               headers=config.headers),
                                execute_model))

        def add_delete():
            config.add_route_view('DELETE', model_action('delete'),
                    route_namespace='delete', route_postfix=id_pattern,
                    decorators=(validate_model(match=self.get_schema,
                                               headers=config.headers),
                               execute_model))

        def add_options():
            """Add OPTIONS method routes.
            """
            config.add_route_view('OPTIONS', null_action)
            config.add_route_view('OPTIONS', null_action,
                                route_namespace='options_id',
                                route_postfix=id_pattern)
        

        # TODO: Add permissions!
        Model = self.__model_class
        add_options()

        # Probably use a map dict in the model instead of looking at attribs.
        if hasattr(Model, 'all'):
            add_all()

        if hasattr(Model, 'create'):
            add_create()

        if hasattr(Model, 'retrieve'):
            add_retrieve()

        if hasattr(Model, 'update'):
            add_update()

        if hasattr(Model, 'delete'):
            add_delete()



    '''
    # Views
    def options(self, request):
        return request.response

    def all(self, request):
        model = self.bind(request)
        return model.all(**self.build_obj(request))

    def create(self, request):
        model = self.bind(request)
        return model.create(**self.build_obj(request))

    def retrieve(self, request):
        model = self.bind(request)
        return model.retrieve(**self.build_obj(request))

    def update(self, request):
        model = self.bind(request)
        return model.update(**self.build_obj(request))

    def delete(self, request):
        model = self.bind(request)
        return model.delete(**self.build_obj(request))'''