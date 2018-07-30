from pyramid.config import Configurator

from pyramid.session import SignedCookieSessionFactory
from pyramid.renderers import JSON


def do_config(global_config, **settings):

    session_factory = SignedCookieSessionFactory(settings.get('session.secret', 'hello'))
    config = Configurator(session_factory=session_factory, settings=settings)
    config.configure_celery(global_config['__file__'])
    config.add_renderer('prettyjson', JSON(indent=4))

    config.add_route('schedules_api', '/schedule*endpoint')
    config.scan()

    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = do_config(global_config, **settings)

    return config.make_wsgi_app()
