import re
import urllib
import argparse
import sys
import dateutil.parser


#p = re.compile(r'F-TICKS/(?P<federation>[\w]+)/(?P<version>[\d+][\.]?[\d]*)#TS=(?P<ts>[\w]+)#RP=(?P<rp>[\w/:_@\.\?\-]+)#AP=(?P<ap>[\w/:_@\.\?\-]+)#PN=(?P<pn>[\w]+)#AM=(?P<am>[\w:\.]*)')
# Takes extra whitespace in RP until the F-TICKS bug gets fixed
p = re.compile(r'F-TICKS/(?P<federation>[\w]+)/(?P<version>[\d+][\.]?[\d]*)#TS=(?P<ts>[\w]+)#RP=(?P<rp>[\w/:_@\.\?\-\ ]+)#AP=(?P<ap>[\w/:_@\.\?\-]+)#PN=(?P<pn>[\w]+)#AM=(?P<am>[\w:\.]*)')


def post_data(url, data):
    r = urllib.urlopen(url, data)
    return r.read()


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
    return post_data(url, '\n'.join(batch))


def single_importer(f, url):
    try:
        for line in f:
            m = p.search(line)
            if m:
                post_data(url, format_data(m) + '\n')
    except KeyboardInterrupt:
        sys.exit(0)


def main():
    # User friendly usage output
    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='*', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-u', '--url', help='URL for flog import', required=True, type=str)
    parser.add_argument('-b', '--batch', help='Parse whole files and bulk send to import', default=False, action='store_true')
    args = parser.parse_args()

    if args.batch:
        for f in args.infiles:
            print batch_importer(f, args.url)
    else:
        single_importer(args.infiles, args.url)

    sys.exit(0)

if __name__ == '__main__':
    main()