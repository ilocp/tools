#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import re

# location list
locations = []

# valid location line
RE_LOC = re.compile(r'^Location')

# regex to grab Longitude/Latitude
RE_LAT = re.compile(r'.*,mLatitude=(?P<value>\-*[0-9]{1,3}\.[0-9]*),')
RE_LNG = re.compile(r'.*,mLongitude=(?P<value>\-*[0-9]{1,3}\.[0-9]*),')

kml_head = '''<?xml version="1.0" encoding="UTF-8"?>
   <kml xmlns="http://www.opengis.net/kml/2.2">
   <Document>
   '''

# replace {},{} with longitude,latitude
placemark_tpl = '''\
   <Placemark>
   <name>Random Placemark</name>
   <Point>
   <coordinates>{},{}</coordinates>
   </Point>
   </Placemark>'''

kml_footer = '''</Document>
    </kml>'''

def parse_locations(logfile):
    """parse locations in locations dictionary"""
    try:
        with open(logfile, 'r') as f:
            for line in f.readlines():
                if RE_LOC.match(line) is None:
                    continue

                try:
                    lat = RE_LAT.match(line).group('value')
                    lng = RE_LNG.match(line).group('value')
                    coordinates = (lng, lat)

                    if coordinates not in locations:
                        locations.append(coordinates)
                except AttributeError:
                    print("Error at line: {}".format(line))

    except IOError as e:
        print("Cannot read from file: {}".format(logfile))

def build_kml():
    kml = []
    kml.append(kml_head)
    for coordinates in locations:
        kml.append(placemark_tpl.format(*coordinates))
    kml.append(kml_footer)
    print(''.join(kml))


if __name__ == '__main__':
    if len(sys.argv) ==  1:
        print("Please supply a location log file")
        sys.exit()

    log = sys.argv[1]
    if not os.path.isfile(log):
        print("Argument does not seem to be a valid file")
        sys.exit()

    parse_locations(log)
    build_kml()

