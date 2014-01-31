from pyramid.response import Response
from pyramid.view import view_config

import colander
import deform
import transaction

from pyramid.httpexceptions import HTTPForbidden, HTTPFound

from pyramid.url import route_path
from apex.ext.deform import deferred_csrf_token

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from formencode import Schema, validators
from sqlalchemy.exc import DBAPIError, IntegrityError

from .models import (
    DBSession,
    Crime,
    )

class CrimeSchema(Schema):
    allow_extra_fields = True

    state = validators.String()
    ctype = validators.String()
    crime = validators.String()
    year = validators.Number()
    count = validators.Number()

@view_config(route_name='crimes_page', renderer='json', permission="authenticated")
def crimes_page(request):
    try:
        import webhelpers.paginate as paginate
        current_page = int(request.matchdict['page'])
        crimes = DBSession.query(Crime).order_by('state, year desc, count desc').all()
        page_url = paginate.PageURL_WebOb(request)
        records = paginate.Page(crimes, current_page, url=page_url, items_per_page=100)
        
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return records.items

@view_config(route_name='crimes', renderer='templates/crimes.pt', permission="authenticated")
def crimes_list(request):
    try:
        import webhelpers.paginate as paginate
        current_page = 1
        crimes = DBSession.query(Crime).order_by('state, year desc, count desc').all()
        page_url = paginate.PageURL_WebOb(request)
        records = paginate.Page(crimes, current_page, url=page_url, items_per_page=100)
        
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return dict(pagecount = records.page_count)

@view_config(route_name='crime_detail', renderer='simplecrud:templates/crime_detail.pt', permission="authenticated")
def crime_detail(request):
    crime = None
    try:
        crime_id = int(request.matchdict['id'])
        if crime_id:
            crime = DBSession.query(Crime).filter(Crime.id==crime_id).first()
    except ValueError:
        log.warning("invalidate id %s input." % request.matchdict['id'])
    except Exception:
        log.error("database error!")

    if not crime:
        return HTTPForbidden()

    return dict(crime=crime)


@view_config(route_name='crime_add', renderer='simplecrud:templates/crime_add.pt', permission="authenticated")
def crime_add(request):
    form = Form(request, schema=CrimeSchema)
    if form.validate():

        crime = Crime(form.data.get("state"),
                    form.data.get("ctype"),
                    form.data.get("crime"),
                    form.data.get("year"),
                    form.data.get("count"))

        try:
            DBSession.add(crime)
            DBSession.flush()
            transaction.commit()

            return HTTPFound(location=route_path("crimes", request))
        except IntegrityError:
            transaction.abort()
            form.errors["global_error"] = 'database insert error.'
        except Exception, e:
            transaction.abort()
            form.errors["global_error"] = 'database error.' + str(e)
            log.error("database error!")

    return dict(renderer=FormRenderer(form))


@view_config(route_name='crime_edit', renderer='simplecrud:templates/crime_edit.pt', permission="authenticated")
def crime_edit(request):
    crime_id = 0
    try:
        crime_id = int(request.matchdict['id'])
    except Exception:
        pass

    if not crime_id:
        return HTTPForbidden()

    form = Form(request, schema=CrimeSchema)
    if form.validate():
        try:
            DBSession.query(Crime).filter(Crime.id==crime_id).update({Crime.state:form.data.get("state"),
                                                                   Crime.ctype:form.data.get("ctype"),
                                                                   Crime.crime:form.data.get("crime"),
                                                                   Crime.year:form.data.get("year"),
                                                                   Crime.count:form.data.get("count")})
            return HTTPFound(location=route_path("crimes", request))
        except IntegrityError:
            transaction.abort()
            form.errors["global_error"] = 'database update error.'
        except Exception:
            transaction.abort()
            form.errors["global_error"] = 'database error.'
            log.error("database error!")
    else:
        crime = None
        try:
            crime = DBSession.query(Crime).filter(Crime.id==crime_id).first()
        except Exception:
            pass

        if not crime:
            return HTTPForbidden()

        form = Form(request, schema=CrimeSchema, obj = crime)

    return dict(renderer=FormRenderer(form))

@view_config(route_name='crime_delete', permission="authenticated")
def crime_delete(request):
    try:

        crime_id = int(request.matchdict['id'])
        
        if crime_id:
            DBSession.query(Crime).filter(Crime.id==crime_id).delete()
        return HTTPFound(location=route_path("crimes", request))
    except Exception:
        return HTTPForbidden()

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_SimpleCRUD_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

