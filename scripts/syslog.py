import re
import urllib

p = re.compile(r'F-TICKS/(?P<federation>[\w]+)/(?P<version>[\d+][\.]?[\d]*)#TS=(?P<ts>[\w]+)#RP=(?P<rp>[\w/:_@\.\?\-]+)#AP=(?P<ap>[\w/:_@\.\?\-]+)#PN=(?P<pn>[\w]+)#AM=(?P<am>[\w:\.]*)')


f = open('idp-test.nordu.net.log')
for l in f:
    print ';'.join(p.search(l).groups())



params = urllib.urlencode({'body': data})
f = urllib.urlopen("http://www.musi-cal.com/cgi-bin/query", params)
print f.read()