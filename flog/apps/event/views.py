"""
Created on Apr 13, 2012

@author: leifj
"""
from dateutil import parser as dtparser
from django.utils.timezone import localtime
import json
import re
from flog.apps.event.models import Entity, Event, DailyEventAggregation
from flog.apps.event.models import Country, EduroamRealm, DailyEduroamEventAggregation
from flog.apps.event.models import OptimizedDailyEduroamEventAggregation
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import F
from django.db.models.aggregates import Count, Sum
from django.core.cache import cache
from django.db import connections, transaction, DatabaseError


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
    try:
        cursor = connections['default'].cursor()
        cursor.execute('DELETE FROM flog_cache_table')
    except DatabaseError:
        pass  # No database cache used


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
    return render(request, 'event/index.html', {})


def websso_entities(request):
    idp = Entity.objects.filter(is_idp=True).all()
    rp = Entity.objects.filter(is_rp=True).all()
    return render(request, 'event/websso_list.html', {'rps': rp.all(), 'idps': idp.all()})


def eduroam_realms(request, country_code=None):
    if not country_code:
        countries = Country.objects.all().exclude(name='Unknown').order_by('name')
        return render(request, 'event/eduroam_list.html', {'from_country': None, 'to_country': None,
                                                           'countries': countries, 'country_name': None})
    country = get_object_or_404(Country, country_code=country_code)
    from_country = OptimizedDailyEduroamEventAggregation.objects.filter(realm__country=country).order_by(
        'realm__realm').distinct('realm__realm').values_list(
        'realm__id', 'realm__realm', 'realm__name')
    to_country = OptimizedDailyEduroamEventAggregation.objects.filter(visited_institution__country=country).order_by(
        'visited_institution__realm').distinct('visited_institution__realm').values_list(
        'visited_institution__id', 'visited_institution__realm', 'visited_institution__name')
    return render(request, 'event/eduroam_list.html', {'from_country': from_country, 'to_country': to_country,
                                                       'countries': None, 'country_name': country.name})


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
            threshold = float(request.GET.get('threshold', 0.01))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render(request, 'event/piechart.html', {'entity': entity, 'cross_type': cross_type, 'threshold': threshold,
                                                   'default_min': default_min, 'default_max': default_max,
                                                   'protocol': protocol})


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
            threshold = float(request.GET.get('threshold', 0.01))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render(request, 'event/piechart.html', {'entity': entity, 'cross_type': cross_type, 'threshold': threshold,
                                                   'default_min': default_min, 'default_max': default_max,
                                                   'protocol': protocol})


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
            qs = OptimizedDailyEduroamEventAggregation.objects.filter(visited_institution=realm,
                                                                      date__range=(start_time, end_time)).values(
                'realm__id', 'realm__realm').annotate(count=Sum('calling_station_id_count')).order_by('-count')
            for item in qs:
                data.append({
                    'label': item['realm__realm'],
                    'data': item['count'],
                    'id': item['realm__id']
                })
            cache.set('to-realm-%s-%s-%s' % (pk, start_time.date(), end_time.date()),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        try:
            threshold = float(request.GET.get('threshold', 0.01))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render(request, 'event/piechart.html', {'realm': realm, 'cross_type': cross_type, 'threshold': threshold,
                                                   'default_min': default_min, 'default_max': default_max})


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
            qs = OptimizedDailyEduroamEventAggregation.objects.filter(realm=realm,
                                                                      date__range=(start_time, end_time)).values(
                'visited_institution__id', 'visited_institution__realm').annotate(
                count=Sum('calling_station_id_count')).order_by('-count')
            for item in qs:
                data.append({
                    'label': item['visited_institution__realm'],
                    'data': item['count'],
                    'id': item['visited_institution__id']
                })
            cache.set('from-realm-%s-%s-%s' % (pk, start_time.date(), end_time.date()),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        try:
            threshold = float(request.GET.get('threshold', 0.01))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render(request, 'event/piechart.html', {'realm': realm, 'cross_type': cross_type, 'threshold': threshold,
                                                   'default_min': default_min, 'default_max': default_max})


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
            'nodes': list(nodes.values()),
            'links': links
        }
        cache.set('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol),
                  data, 60*60*24)  # 24h
    return data


def get_eduroam_auth_flow_data(start_time, end_time, protocol, country_code='se'):
    for_country = get_object_or_404(Country, country_code=country_code)
    data = cache.get('auth-flow-%s-%s-%s-%s' % (start_time.date(), end_time.date(), protocol, country_code), False)
    if not data:
        qs = OptimizedDailyEduroamEventAggregation.objects.filter(
            date__range=(start_time.date(), end_time.date())).values(
            'realm', 'realm__realm', 'realm__country', 'realm__country__name', 'visited_institution',
            'visited_institution__realm', 'visited_institution__country',
            'visited_institution__country__name').order_by().annotate(Sum('calling_station_id_count'))
        nodes = {}
        links = {}
        for e in qs:
            from_country = e['realm__country']
            to_country = e['visited_institution__country']
            if for_country.id == from_country:  # We only want to show countries to swedish realms ...
                from_realm = e['realm__realm']
            else:
                from_realm = e['realm__country__name']
            if for_country.id == to_country:  # ... and only swedish realms to other countries.
                to_realm = e['visited_institution__realm']
            else:
                to_realm = e['visited_institution__country__name']
            realm_keys = ('from-%s' % from_realm, 'to-%s' % to_realm)
            country_keys = ('from-%s' % e['realm__country__name'], 'to-%s' % e['visited_institution__country__name'])
            links[realm_keys] = {
                'source': realm_keys[0],
                'target': realm_keys[1],
                'value': e['calling_station_id_count__sum']
            }
            if (country_keys[0], realm_keys[0]) in links:
                links[(country_keys[0], realm_keys[0])]['value'] += e['calling_station_id_count__sum']
            else:
                links[(country_keys[0], realm_keys[0])] = {
                    'source': country_keys[0],
                    'target': realm_keys[0],
                    'value': e['calling_station_id_count__sum']
                }
            if (country_keys[1], realm_keys[1]) in links:
                links[(country_keys[1], realm_keys[1])]['value'] += e['calling_station_id_count__sum']
            else:
                links[(country_keys[1], realm_keys[1])] = {
                    'source': realm_keys[1],
                    'target': country_keys[1],
                    'value': e['calling_station_id_count__sum']
                }
            nodes[realm_keys[0]] = {'id': realm_keys[0], 'name': from_realm}
            nodes[realm_keys[1]] = {'id': realm_keys[1], 'name': to_realm}
            nodes[country_keys[0]] = {'id': country_keys[0], 'name': e['realm__country__name']}
            nodes[country_keys[1]] = {'id': country_keys[1], 'name': e['visited_institution__country__name']}
            data = {
                'nodes': list(nodes.values()),
                'links': list(links.values())
            }
        cache.set('auth-flow-%s-%s-%s-%s' % (start_time.date(), end_time.date(), protocol, country_code),
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
    return render(request, 'event/sankey.html', {'default_min': default_min, 'default_max': default_max,
                                                 'threshold': threshold, 'protocol': protocol})