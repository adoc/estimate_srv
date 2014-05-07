import uuid
import thredis
import thredis.util

import pyramid.renderers

from pyramid.config import Configurator
from pyramid.request import Request

from thredis import UnifiedSession
from thredis.util import JsonEncoder

import oest.model

from oest.service.modelview import ModelViews


__VERSION__ = "0.1"
__DESCRIPTION__ = "Online Estimate Web Service API."
__URL__ = "http://oest.webmob.net"


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)

    # config.include('oest.service.views:config_this', route_prefix='/')

    ModelViews(oest.model.Location).config(config, route_prefix='/location')
    ModelViews(oest.model.ZipCodeLocation).config(config, route_prefix='/zip')

    # config.add_renderer('jsonp', pyramid.renderers.JSONP(param_name='callback', indent=4))
    json = pyramid.renderers.JSON(separators=(',', ':'), cls=JsonEncoder)
    def adapt_uuid(obj, request):
        return obj.urn
    json.add_adapter(uuid.UUID, adapt_uuid)
    json.add_adapter(set, lambda o, r: list(o))
    config.add_renderer('json', json)

    # Let's add the Redis Session as a registry setting.
    config.add_settings(redis=UnifiedSession.from_url(settings['redis']))

    config.add_route('info_route', '/')
    config.add_view(info, route_name='info_route', renderer='json')

    config.add_route('toolbar_route', '/toolbar')
    config.add_view(toolbar, route_name='toolbar_route', renderer="string")

    app = config.make_wsgi_app()
    
    #from oest.service.translogger import TransLogger
    #app = TransLogger(app, setup_console_handler=False)
    return app


def toolbar(request):
    request.response.headers['Content-Type'] = 'text/html'
    return """<html><body><h2>Toolbar!<h2></body></html>"""


def info(request):
    request.response.headers.update([('Access-Control-Allow-Origin', '*')])
    return {
        'sig': "On6t5z4edrRLTpaITVECjOmY8Lu8nGswa4WeN7TmNmDDByHtmj8IrvTHWkGMMz6IJilN1rsnSo8bycBkDT8ysSnitogXV2mF",
        'version': __VERSION__,
        'description': __DESCRIPTION__,
        'url': __URL__
    }