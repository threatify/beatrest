import sys
import os

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.renderers import JSON

def do_config(global_config, **settings):
    load_project_settings()

    session_factory = SignedCookieSessionFactory(settings.get('session.secret', 'hello'))
    config = Configurator(session_factory=session_factory, settings=settings)
    config.configure_celery(global_config['__file__'])
    config.add_renderer('prettyjson', JSON(indent=4))
    config.add_tween('threatify_api.auth.authenticator')
    config.include('pyramid_mako')
    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')

    # DB configuration
    # engine = engine_from_config(settings, 'sqlalchemy.')
    # db.configure(bind=engine)

    # Logs configuration
    # logger_engine = engine_from_config(settings, 'logsdb.')
    # logsdb.configure(bind=logger_engine)

    # GeoIP Database configuration
    db_location = settings.get('geoip_db', None)
    if not db_location:
        raise RuntimeError("GeoIP database location not provided in settings")

    geodb.load(db_location)

    # Redis configuration
    rdb.connect(host=settings['redis.host'],
                port=int(settings['redis.port']),
                db=int(settings['redis.db']))

    # ArangoDB configuration
    graph_models.connect(server=settings['tf_arangodb.server'],
                         port=settings['tf_arangodb.port'],
                         username=settings['tf_arangodb.username'],
                         password=settings['tf_arangodb.password'],
                         db_name=settings['tf_arangodb.database'])

    graph_models.vdb_connect(server=settings['vfeed_arangodb.server'],
                             port=settings['vfeed_arangodb.port'],
                             username=settings['vfeed_arangodb.username'],
                             password=settings['vfeed_arangodb.password'],
                             db_name=settings['vfeed_arangodb.database'])

    # Other config
    # admin_models = get_admin_models()
    # add_admin_handler(config, db, admin_models, 'admin.', '/admin', MyAdminController)

    application_routes(config)
    configure_app_routes(config)

    all_apps = get_submodules(apps)

    ignored_apps = []
    enabled_app_names = [subapp.APP_NAME for subapp in enabled_apps]
    for app in all_apps:
        if app['is_package'] and app['name'] not in enabled_app_names:
            ignored_apps.append('.apps.' + app['name'])

    config.scan(ignore=ignored_apps)

    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = do_config(global_config, **settings)

    return config.make_wsgi_app()

@app.route('/schedule', method='GET')
def get_schedule():

    schedule = {}

    return schedule


if __name__ == "__main__":
    
    app = main()
    run(app, reloader=True, host='localhost', port=8181, debug=True)
