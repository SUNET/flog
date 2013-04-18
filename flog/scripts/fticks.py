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
import daemon

# F-TICKS importer for flog
#
# Requires python-dateutil and python-daemon.

#p = re.compile(r'F-TICKS/(?P<federation>[\w]+)/(?P<version>[\d+][\.]?[\d]*)#TS=(?P<ts>[\w]+)#RP=(?P<rp>[\w/:_@\.\?\-]+)#AP=(?P<ap>[\w/:_@\.\?\-]+)#PN=(?P<pn>[\w]+)#AM=(?P<am>[\w:\.]*)')

p = re.compile(r'''
                F-TICKS/
                (?P<federation>[\w]+)/
                (?P<version>[\d+][\.]?[\d]*)
                \#TS=(?P<ts>[\w]+)
                \#RP=(?P<rp>[\w/:_@\.\?\-\ ]+) # Takes extra whitespace in RP until the F-TICKS bug gets fixed
                \#AP=(?P<ap>[\w/:_@\.\?\-]+)
                \#PN=(?P<pn>[\w]+)
                \#AM=(?P<am>[\w:\.]*)
                ''', re.VERBOSE)


def post_data(url, data):
    try:
        r = urllib.urlopen(url, data)
        return r.read()
    except IOError as e:
        print e


def format_timestamp(ts):
    dt = dateutil.parser.parse(ts)
    return dt.isoformat(sep=' ')


def format_data(m):
    data = [
        format_timestamp(m.group('ts')),
        'SAML2',
        ''.join(m.group('rp').split()),  # Hack until extra whitespace bug in F-TICKS get fixed.
        m.group('ap'),
        m.group('pn')
    ]
    return ';'.join(data)


def batch_importer(f, url):
    batch = []
    for line in f:
        m = p.search(line)
        if m:
            batch.append(format_data(m))
        if len(batch) > 1000:  # Approx. 300kb in file size
            print post_data(url, '\n'.join(batch))
            batch = []
    post_data(url, '\n'.join(batch))
    return True


def single_importer(f, url):
    try:
        for line in f:
            m = p.search(line)
            if m:
                print post_data(url, format_data(m) + '\n')
    except KeyboardInterrupt as e:
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
    parser.add_argument('-p', '--pipe', type=str)
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
    except KeyboardInterrupt:
        sys.exit(0)
    sys.exit(0)

if __name__ == '__main__':
    main()