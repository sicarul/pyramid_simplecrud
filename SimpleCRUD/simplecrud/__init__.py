from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include('apex', route_prefix='/auth')
    config.add_route('crimes', '/')
    config.add_route('crimes_page', '/crimes/{page}')
    config.add_route('crime_detail', '/crime/detail/{id}')
    config.add_route('crime_add', '/crime/add')
    config.add_route('crime_edit', '/crime/edit/{id}')
    config.add_route('crime_delete', '/crime/delete/{id}')
    config.scan()
    return config.make_wsgi_app()
