#!/usr/bin/env python3

import csv
import os
import sys
import math
import random

class Point(object):
    def __init__(self, latitude, longitude, bearing=None):
        self._lat = latitude
        self._lng = longitude
        self._brg = bearing

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat):
        self._lat = float("{0:.6f}".format(lat))

    @property
    def lng(self):
        return self._lng

    @lng.setter
    def lng(self, lng):
        self._lng = float("{0:.6f}".format(lng))

    @property
    def brg(self):
        return self._brg

    @brg.setter
    def brg(self, brg):
        self._brg = int(brg % 360)

    def calculate_bearing(self, dest):
        """calculate the bearing towards a destination"""
        lat1 = math.radians(self.lat)
        lat2 = math.radians(dest.lat)
        dlon = math.radians(dest.lng - self.lng)

        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - \
            math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        brg = math.atan2(y, x)

        self.brg = (math.degrees(brg) + 360) % 360


def get_csv_file():
    """get a valid csv file from the arguments or the current working
    directory"""
    default_csv = 'reports.csv'

    if len(sys.argv) == 2:
        return os.path.abspath(sys.argv[1])
    else:
        if os.path.exists(default_csv):
            return os.path.abspath(default_csv)
        else:
            print('Error: invalid csv file')
            sys.exit(1)

def read_csv(csvfile):
    """read csv with coordinates list"""
    points = []
    header = False
    with open(csvfile, 'r') as f:
        # check if header is present
        if csv.Sniffer().has_header(f.read(512)):
            header = True
        f.seek(0)

        reader = csv.reader(f, delimiter=',')
        # skip header
        if header:
            next(reader)

        for row in reader:
            p = Point(float(row[0]), float(row[1]))
            points.append(p)

    #print("=> {} entries read".format(len(points)))
    return points

def shift_coordinate():
    shift = random.randrange(100,900)
    return float("0.000{}".format(str(shift))) * random.choice((1,-1))

def shift_bearing(max_degrees=5):
    degrees = range(max_degrees * -1, max_degrees)
    shift = random.choice(degrees)
    while shift == 0:
        shift = random.choice(degrees)
    return shift

def randomize(points):
    """randomize lat/lng coordinates and bearings"""
    for point in points:
        point.lat += shift_coordinate()
        point.lng += shift_coordinate()
        point.calculate_bearing(REFERENCE_POINT)
        point.brg += shift_bearing()

    return points

def points2csv(points):
    with open('points.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['latitude', 'longitude', 'heading'])
        for point in points:
            writer.writerow([point.lat, point.lng, point.brg])


if __name__ == "__main__":
    REFERENCE_POINT = Point(38.173596, 23.724707)
    random.seed()
    csvfile = get_csv_file()
    points = read_csv(csvfile)
    new_points = randomize(points)
    random.shuffle(new_points)
    points2csv(new_points)
