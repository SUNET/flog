"""
Created on Apr 13, 2012

@author: leifj
"""

from dateutil import parser as dtparser
from django.utils.timezone import localtime
import json
import gc
import re
from apps.event.models import Entity, Event, DailyEventAggregation
from apps.event.models import Country, EduroamRealm, DailyEduroamEventAggregation
from django.shortcuts import get_object_or_404, render_to_response, RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models.aggregates import Count, Sum
from django.core.cache import cache
from django.db import connections, transaction


def get_protocol(protocol):
    protocols = {
        'Unknown': Event.Unknown,
        'WAYF': Event.WAYF,
        'Discovery': Event.Discovery,
        'SAML2': Event.SAML2,
    }
    if protocol in protocols:
        return protocols[protocol]
    return Event.SAML2

# Clear cache for sqlite (workaround)
def flush_cache():
    # This works as advertised on the memcached cache:
    cache.clear()
    # This manually purges the SQLite/postgres cache:
    cursor = connections['default'].cursor()
    cursor.execute('DELETE FROM flog_cache_table')
    transaction.commit_unless_managed(using='default')


def queryset_iterator(queryset, chunksize=100000):
    """
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 100000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    """
    pk = 0
    try:
        last_pk = queryset.order_by('-pk')[0].pk
    except IndexError:
        raise StopIteration
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


def jsdt2pydt(jsdt):
    """
    Takes a date and time string formatted as javascript seemed fit.
    Returns datetime object.
    """
    try:
        dt = dtparser.parse(jsdt)
    except ValueError:
        dt = dtparser.parse(' '.join(jsdt.split()[:6]))
    return dt


def index(request):
    return render_to_response('event/index.html', {},
                              context_instance=RequestContext(request))


def websso_entities(request):
    idp = Entity.objects.filter(is_idp=True).all()
    rp = Entity.objects.filter(is_rp=True).all()
    return render_to_response('event/websso_list.html',
                              {'rps': rp.all(), 'idps': idp.all()},
                              context_instance=RequestContext(request))


def eduroam_realms(request, country_name=None):
    from_country = None
    to_country = None
    countries = None
    if country_name:
        country = get_object_or_404(Country, name=country_name)
        from_country = country.country_realms.filter(realm_events__successful=True).order_by('name', 'realm').\
            values_list('id', 'realm', 'name').distinct()
        to_country = EduroamRealm.objects.filter(realm_events__visited_country=country, realm_events__successful=True).\
            order_by('name', 'realm').values_list('id', 'realm', 'name').distinct()
    else:
        countries = Country.objects.all().exclude(name='Unknown').order_by('name')
    return render_to_response('event/eduroam_list.html', {'from_country': from_country, 'to_country': to_country,
                                                          'countries': countries, 'country_name': country_name},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def by_rp(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'origin'
    if request.POST:
        start_time = localtime(jsdt2pydt(request.POST['start']))
        end_time = localtime(jsdt2pydt(request.POST['end']))
        protocol = request.POST['protocol']
        data = cache.get('by-rp-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol), False)
        if not data:
            data = []
            d = Entity.objects.filter(origin_events__rp=entity,
                                      origin_events__ts__range=(start_time, end_time),
                                      origin_events__protocol=protocol)
            for e in d.annotate(count=Count('origin_events__id')).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-rp-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        protocol = get_protocol(request.GET.get('protocol', 'SAML2'))
        try:
            threshold = float(request.GET.get('threshold', 0.05))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type,
                               'threshold': threshold, 'default_min': default_min,
                               'default_max': default_max, 'protocol': protocol},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def by_origin(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'rp'
    if request.POST:
        start_time = localtime(jsdt2pydt(request.POST['start']))
        end_time = localtime(jsdt2pydt(request.POST['end']))
        protocol = request.POST['protocol']
        data = cache.get('by-origin-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol), False)
        if not data:
            data = []
            d = Entity.objects.filter(rp_events__origin=entity,
                                      rp_events__ts__range=(start_time, end_time),
                                      rp_events__protocol=protocol)
            for e in d.annotate(count=Count('rp_events__id'),).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-origin-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        protocol = get_protocol(request.GET.get('protocol', 'SAML2'))
        try:
            threshold = float(request.GET.get('threshold', 0.05))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type,
                               'threshold': threshold, 'default_min': default_min,
                               'default_max': default_max, 'protocol': protocol},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def to_realm(request, pk):
    realm = get_object_or_404(EduroamRealm, pk=pk)
    cross_type = 'from'
    if request.POST:
        start_time = localtime(jsdt2pydt(request.POST['start']))
        end_time = localtime(jsdt2pydt(request.POST['end']))
        data = cache.get('to-realm-%s-%s-%s' % (pk, start_time.date(), end_time.date()), False)
        if not data:
            data = []
            d = EduroamRealm.objects.filter(realm_events__visited_institution=realm,
                                            realm_events__successful=True,
                                            realm_events__ts__range=(start_time, end_time))
            for e in d.annotate(count=Count('realm_events__id'),).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('to-realm-%s-%s-%s' % (pk, start_time.date(), end_time.date()),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        try:
            threshold = float(request.GET.get('threshold', 0.05))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render_to_response('event/piechart.html',
                              {'realm': realm, 'cross_type': cross_type,
                               'threshold': threshold, 'default_min': default_min,
                               'default_max': default_max},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def from_realm(request, pk):
    realm = get_object_or_404(EduroamRealm, pk=pk)
    cross_type = 'to'
    if request.POST:
        start_time = localtime(jsdt2pydt(request.POST['start']))
        end_time = localtime(jsdt2pydt(request.POST['end']))
        data = cache.get('from-realm-%s-%s-%s' % (pk, start_time.date(), end_time.date()), False)
        if not data:
            data = []
            d = EduroamRealm.objects.filter(institution_events__realm=realm,
                                            institution_events__successful=True,
                                            institution_events__ts__range=(start_time, end_time))
            for e in d.annotate(count=Count('institution_events__id'),).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('from-realm-%s-%s-%s' % (pk, start_time.date(), end_time.date()),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        try:
            threshold = float(request.GET.get('threshold', 0.05))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render_to_response('event/piechart.html',
                              {'realm': realm, 'cross_type': cross_type,
                               'threshold': threshold, 'default_min': default_min,
                               'default_max': default_max},
                              context_instance=RequestContext(request))


def get_auth_flow_data(start_time, end_time, protocol):
    data = cache.get('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol), False)
    if not data:
        qs = DailyEventAggregation.objects.all().filter(
            date__range=(start_time.date(), end_time.date())).values('origin_name', 'rp_name', 'protocol').annotate(
                total_events=Sum('num_events'))
        nodes = {}
        links = []
        for e in qs:
            keys = ('%s-rp' % e['rp_name'], '%s-origin' % e['origin_name'])
            links.append({
                'source': keys[0],
                'target': keys[1],
                'value': e['total_events']
            })
            nodes[keys[0]] = {'id': keys[0], 'name': e['rp_name']}
            nodes[keys[1]] = {'id': keys[1], 'name': e['origin_name']}
        data = {
            'nodes': nodes.values(),
            'links': links
        }
        cache.set('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol),
                  data, 60*60*24)  # 24h
    return data


def get_eduroam_auth_flow_data(start_time, end_time, protocol):
    data = cache.get('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol), False)
    if not data:
        qs = DailyEduroamEventAggregation.objects.filter(date__range=(start_time.date(), end_time.date())).values(
            'realm', 'realm_country', 'visited_institution', 'visited_country').annotate(Count('id'))
        nodes = {}
        links = {}
        regex = re.compile('Sweden')
        for e in qs:
            from_country = e['realm_country']
            to_country = e['visited_country']
            if regex.match(from_country):  # We only want to show countries to swedish realms ...
                from_realm = e['realm']
            else:
                from_realm = from_country
            if regex.match(to_country):  # ... and only swedish realms to other countries.
                to_realm = e['visited_institution']
            else:
                to_realm = to_country
            realm_keys = ('from-%s' % from_realm, 'to-%s' % to_realm)
            country_keys = ('from-%s' % from_country, 'to-%s' % to_country)
            links[realm_keys] = {
                'source': realm_keys[0],
                'target': realm_keys[1],
                'value': e['id__count']
            }
            if (country_keys[0], realm_keys[0]) in links:
                links[(country_keys[0], realm_keys[0])]['value'] += e['id__count']
            else:
                links[(country_keys[0], realm_keys[0])] = {
                    'source': country_keys[0],
                    'target': realm_keys[0],
                    'value': e['id__count']
                }
            if (country_keys[1], realm_keys[1]) in links:
                links[(country_keys[1], realm_keys[1])]['value'] += e['id__count']
            else:
                links[(country_keys[1], realm_keys[1])] = {
                    'source': realm_keys[1],
                    'target': country_keys[1],
                    'value': e['id__count']
                }
            nodes[realm_keys[0]] = {'id': realm_keys[0], 'name': from_realm}
            nodes[realm_keys[1]] = {'id': realm_keys[1], 'name': to_realm}
            nodes[country_keys[0]] = {'id': country_keys[0], 'name': from_country}
            nodes[country_keys[1]] = {'id': country_keys[1], 'name': to_country}
            data = {
                'nodes': nodes.values(),
                'links': links.values()
            }
        cache.set('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol),
                  data, 60*60*24)  # 24h
    return data


@ensure_csrf_cookie
def auth_flow(request, protocol=None):
    if request.POST:
        start_time = localtime(jsdt2pydt(request.POST['start']))
        end_time = localtime(jsdt2pydt(request.POST['end']))
        protocol = request.POST['protocol']
        if protocol == 'eduroam':
            data = get_eduroam_auth_flow_data(start_time, end_time, protocol)
        else:
            data = get_auth_flow_data(start_time, end_time, protocol)
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 1)
        default_max = request.GET.get('max', 1)
        if not protocol:
            protocol = get_protocol(request.GET.get('protocol', 'SAML2'))
        try:
            threshold = int(request.GET.get('threshold', 50))
        except ValueError:
            return HttpResponse('Argument threshold not a number.', content_type="text/html")
    return render_to_response('event/sankey.html',
                              {'default_min': default_min, 'default_max': default_max,
                               "threshold": threshold, 'protocol': protocol},
                              context_instance=RequestContext(request))