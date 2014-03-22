from pyramid.config import Configurator
from thredis import UnifiedSession
import oest.model


__VERSION__ = "0.1"
__DESCRIPTION__ = "Online Estimate Web Service API."
__URL__ = "http://oest.webmob.net"


def config_location_view(config):
    config.add_route('location_all', '/')
    config.add_route('location_get', '/{id}')
    config.add_route('location_add', '/')
    config.add_route('location_update', '/{id}')
    config.add_route('location_delete', '/{id}')

    config.add_view(oest.model.all, route_name='location_all', request_method='GET',
                    renderer='json')
    config.add_view(oest.model.get, route_name='location_get', request_method='GET',
                    renderer='json')
    config.add_view(oest.model.add, route_name='location_add', request_method='POST',
                    renderer='json', decorator=oest.model.cleanup)
    config.add_view(oest.model.update, route_name='location_update', request_method='PUT',
                    renderer='json', decorator=oest.model.cleanup)
    config.add_view(oest.model.delete, route_name='location_delete', request_method='DELETE',
                    renderer='json', decorator=oest.model.cleanup)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.include('oest.service.views:config_this', route_prefix='/')
    config.include(config_location_view, route_prefix='/location')
    
    #config.scan()

    config.add_settings(redis=UnifiedSession.from_url(settings['redis']))

    return config.make_wsgi_app()


def info():
    return {
        'version': __VERSION__,
        'description': __DESCRIPTION__,
        'url': __URL__
    }