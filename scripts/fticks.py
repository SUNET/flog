#! /usr/bin/env python

"""
Created on Apr 12, 2013

@author: lundberg@nordu.net
"""

import re
import urllib
import argparse
import sys
import dateutil.parser
import dateutil.tz
import daemon

# F-TICKS importer for flog
#
# Requires python-dateutil and python-daemon.

# Federated Identity Management data
websso = re.compile(r'''
                F-TICKS/
                (?P<federation>[\w]+)/
                (?P<version>[\d+][\.]?[\d]*)
                \#TS=(?P<ts>[\w]+)
                \#RP=(?P<rp>[\w/:_@\.\?\-\ ]+) # Takes extra whitespace in RP until the F-TICKS bug gets fixed
                \#AP=(?P<ap>[\w/:_@\.\?\-\ ]+) # Takes extra whitespace in RP until the F-TICKS bug gets fixed
                \#PN=(?P<pn>[\w]+)
                \#AM=(?P<am>[\w:\.]*)
                ''', re.VERBOSE)

# eduroam data
eduroam = re.compile(r'''
                   (?P<meta>.*)
                   F-TICKS/
                   eduroam/
                   (?P<version>[\d+][\.]?[\d]*)
                   \#REALM=(?P<realm>[\w/:_@\.\?\-]+)
                   \#VISCOUNTRY=(?P<visited_country>[\w]{2,3})  # a two-letter (ISO 3166-1 alpha-2), a three-letter (ISO 3166-1 alpha-3) or a three-digit numeric (ISO 3166-1 numeric) code.
                   \#VISINST=(?P<visited_institution>[\w/:_@\.\?\-]+)
                   \#CSI=(?P<calling_station_id>[\w\-:]+)
                   \#RESULT=(?P<result>OK|FAIL)
                   ''', re.VERBOSE)


def post_data(url, data):
    try:
        r = urllib.urlopen(url, data)
        return r.read()
    except IOError as e:
        print e


def format_timestamp(ts):
    dt = dateutil.parser.parse(ts)
    if not dt.tzinfo:
        dt.replace(tzinfo=dateutil.tz.tzutc())
    return dt.isoformat(sep=' ')


def format_websso_data(m):
    data = [
        format_timestamp(m.group('ts')),
        '3',                             # 0:'Unknown', 1:'WAYF', 2:'Discovery', 3:'SAML2'
        ''.join(m.group('rp').split()),  # Hack until extra whitespace bug in F-TICKS get fixed.
        ''.join(m.group('ap').split()),  # Hack until extra whitespace bug in F-TICKS get fixed.
        m.group('pn')
    ]
    return ';'.join(data)


def format_eduroam_data(m):
    try:
        # Legacy rsyslog date format "Mar  5 15:22:15"
        ts = format_timestamp(' '.join(m.group('meta').split()[:3]))
    except ValueError:
        # New rsyslog date format "2014-03-06T14:59:04.677583+00:00"
        ts = format_timestamp(m.group('meta').split()[0])
    data = [
        ts,
        'eduroam',
        m.group('version'),
        m.group('realm'),
        m.group('visited_country'),
        m.group('visited_institution'),
        m.group('calling_station_id'),
        m.group('result')
    ]
    return ';'.join(data)


def batch_importer(f, url):
    batch = []
    for line in f:
        websso_match = websso.search(line)
        if websso_match:
            batch.append(format_websso_data(websso_match))
        else:
            eduroam_match = eduroam.search(line)
            if eduroam_match:
                batch.append(format_eduroam_data(eduroam_match))
        if len(batch) > 1000:  # Approx. 300kb in file size
            print post_data(url, '\n'.join(batch))
            batch = []
    post_data(url, '\n'.join(batch))
    return True


def single_importer(f, url):
    try:
        for line in f:
            websso_match = websso.search(line)
            if websso_match:
                print post_data(url, format_websso_data(websso_match) + '\n')
            else:
                eduroam_match = eduroam.search(line)
                if eduroam_match:
                    print post_data(url, format_eduroam_data(eduroam_match) + '\n')
    except (KeyboardInterrupt, TypeError) as e:
        raise e


def main():
    # User friendly usage output
    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='*', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-u', '--url', help='URL for flog import', required=True, type=str)
    parser.add_argument('-b', '--batch', help='Parse whole files and bulk send to import', default=False,
                        action='store_true')
    parser.add_argument('-d', '--daemon', help='Run in daemon mode and read from named pipe [PIPE]', default=False,
                        action='store_true')
    parser.add_argument('-p', '--pipe', help='Named pipe', type=str)
    parser.add_argument('-f', '--foreground', help='Run daemon in foreground', default=False,
                        action='store_true')
    args = parser.parse_args()

    try:
        if args.batch:
            # Open files and post all found F-TICKS lines to URL
            for f in args.infiles:
                batch_importer(f, args.url)
        elif args.daemon:
            # Starts the daemon reading the named pipe, posts every found line to URL
            if not args.pipe:
                print 'Please set a path to the pipe using --pipe.'
                sys.exit(0)
            context = daemon.DaemonContext(working_directory='/tmp')
            if args.foreground:
                context.detach_process = False
                context.stdout = sys.stdout
                context.stderr = sys.stderr
            with context:
                if args.foreground:
                    print 'Reading from %s...' % args.pipe
                while True:
                    try:
                        f = open(args.pipe)
                        single_importer(f, args.url)
                    except IOError as e:
                        if args.foreground:
                            print e
        else:
            # Read from stdin and post every found line to URL
            single_importer(args.infiles, args.url)
    except TypeError as e:
        print 'Input not as expected.'
        print e
    except KeyboardInterrupt:
        sys.exit(0)
    sys.exit(0)

if __name__ == '__main__':
    main()