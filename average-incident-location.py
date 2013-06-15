#!/usr/bin/env python3

# average-incident.py
# requires python >= 3

import os
import sys
import math
import csv
import itertools

class Point(object):
    def __init__(self, latitude, longitude, bearing=None):
        self.lat = latitude
        self.lng = longitude
        self.brg = bearing
        self.angle = None

    def calculate_angle(self, start_point):
        dx = self.lng - start_point.lng
        dy = self.lat - start_point.lat
        # calculate angle in degrees
        self.angle = math.atan2(dy, dx) * 180 / math.pi

        if self.angle < 0:
            self.angle += 360


# earth radius in meters
R = 6378137

# reference points for our experiments
REF_POINT = Point(37.972937, 23.673343)
#SCENARIO_POINT = Point(37.9704459, 23.6703964)
SCENARIO_POINT = Point(37.9765647, 23.6726614)


def distance(p1, p2):
    """calculate distance (in meters) between two points"""
    dlat = math.radians(p2.lat - p1.lat)
    dlng = math.radians(p2.lng - p1.lng)

    lat1 = math.radians(p1.lat)
    lat2 = math.radians(p2.lat)

    # square of half the chord length between the points
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.sin(dlng/2) * math.sin(dlng/2) * math.cos(lat1) * math.cos(lat2)

    # angular distance
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def intersection(p1, p2):
    """calculate intersection of 2 points given start points and bearings"""
    lat1 = math.radians(p1.lat)
    lng1 = math.radians(p1.lng)
    brg13 = math.radians(p1.brg)

    lat2 = math.radians(p2.lat)
    lng2 = math.radians(p2.lng)
    brg23 = math.radians(p2.brg)

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    sqrt1 = math.sqrt(math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2) * math.sin(dlng/2))

    dist12 = 2 * math.asin(sqrt1)

    if dist12  == 0:
        return None

    brgA = math.acos( (math.sin(lat2) - math.sin(lat1) * math.cos(dist12)) /
        (math.sin(dist12) * math.cos(lat1)))

    brgB = math.acos( (math.sin(lat1) - math.sin(lat2) * math.cos(dist12)) /
        (math.sin(dist12) * math.cos(lat2)))

    if math.sin(dlng) > 0:
        brg12 = brgA
        brg21 = 2 * math.pi - brgB
    else:
        brg12 = 2 * math.pi - brgA
        brg21 = brgB

    alpha1 = (brg13 - brg12 + math.pi) % (2 * math.pi) - math.pi
    alpha2 = (brg21 - brg23 + math.pi) % (2 * math.pi) - math.pi

    if math.sin(alpha1) == 0 and math.sin(alpha2) == 0:
        return None

    if math.sin(alpha1) * math.sin(alpha2) < 0:
        return None

    alpha3 = math.acos( -math.cos(alpha1) * math.cos(alpha2) +
                        math.sin(alpha1) * math.sin(alpha2) * math.cos(dist12) )

    dist13 = math.atan2(math.sin(dist12) * math.sin(alpha1) * math.sin(alpha2),
                        math.cos(alpha2) + math.cos(alpha1) * math.cos(alpha3))

    lat3 = math.asin( math.sin(lat1) * math.cos(dist13) +
                      math.cos(lat1) * math.sin(dist13) * math.cos(brg13) )

    dlng13 = math.atan2( math.sin(brg13) * math.sin(dist13) * math.cos(lat1),
                         math.cos(dist13) - math.sin(lat1) * math.sin(lat3) )

    lng3 = lng1 - dlng13
    lng3 = (lng3 + 3 * math.pi) % (2 * math.pi) - math.pi

    p3 = Point(math.degrees(lat3), math.degrees(lng3))
    return p3


def read_csv(csvfile):
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
            p = Point(float(row[0]), float(row[1]), float(row[2]))
            points.append(p)

    print("=> {} entries read".format(len(points)))
    return points


def get_possible_incident_set(report_combinations):
    points = []
    unusable = 0
    for c in report_combinations:
        intersection_point = intersection(c[0], c[1])

        if intersection_point is None:
            unusable += 1
            continue

        # if the intersection is within a 10km radius is a possible incident
        d1 = distance(c[0], intersection_point)
        d2 = distance(c[1], intersection_point)

        if d1 <= 3000 and d2 <= 3000:
            intersection_point.calculate_angle(REF_POINT)
            points.append(intersection_point)
        else:
            unusable += 1

    print("=> {} points could not be used".format(unusable))
    return points


def get_average_incident_location(incidents):
    incident_num = len(incidents)

    print("=> {} usable location points".format(incident_num))

    if incident_num == 0:
        return None

    avg_lat = avg_lng = 0
    for incident in incidents:
        avg_lat += incident.lat
        avg_lng += incident.lng

    avg_lat = avg_lat / incident_num
    avg_lng = avg_lng / incident_num

    return Point(avg_lat, avg_lng)


def calculate_distance_error(scenario, reference, new_point):
    error = round(distance(reference, new_point))
    scenario_error = round(distance(reference, scenario))
    error_difference = scenario_error - error
    verb = 'closer'
    if error_difference < 0:
        error_difference *= -1
        verb = 'farther'

    print("=> Distance error is {} meters, {} meters {} than scenario 3".
            format(error, error_difference, verb))


def filter_incidents_with_angles(incidents, angle):
    filtered = []
    for incident in incidents:
        if incident.angle <= angle:
            filtered.append(incident)
    return filtered


#def generate_angles():
#    step = 45
#    inner = range(0, 360, step)
#    outter = range(step, 360+step, step)
#    return zip(inner, outter)

# the angles iterator
def angles():
    angle = 45
    while angle <= 360:
        yield angle
        angle += 45


def get_data_csv():
    default_csv = 'reports.csv'

    if len(sys.argv) == 2:
        return os.path.abspath(sys.argv[1])
    else:
        if os.path.exists(default_csv):
            return os.path.abspath(default_csv)
        else:
            print('Error: invalid csv file')
            sys.exit(1)


def points2csv(points):
    with open('points.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['latitude', 'longitude', 'angle'])
        for point in points:
            writer.writerow([point.lat, point.lng, point.angle])


def main():
    csvfile = get_data_csv()

    print(":: Reading CSV file for report data")
    points = read_csv(csvfile)

    print(":: Calculating report combination sets")
    combinations = list(itertools.combinations(points, 2))
    print("=> {} unique combinations found".format(len(combinations)))

    print(":: Calculating report intersections")
    incidents = get_possible_incident_set(combinations)
    points2csv(incidents)

    print(":: Calculating location using the average location technique")
    incident = get_average_incident_location(incidents)
    print("=> Incident detected at coordinates (lat,lng) {}, {}".format(incident.lat, incident.lng))
    calculate_distance_error(SCENARIO_POINT, REF_POINT, incident)

    #
    # run the same experiment using incidents from specific angles
    #
    print(":: Calculating location using the average location technique with angle parameters")
    total_incidents = len(incidents)
    results = {}
    for angle in angles():
        print(":: Running for angles [0, {}]".format(angle))
        filtered_incidents = filter_incidents_with_angles(incidents, angle)
        print("=> {} of {} incidents within requested angles".
            format(len(filtered_incidents), total_incidents))
        if len(filtered_incidents) == 0:
            results[angle] = 'NA'
            continue
        incident = get_average_incident_location(filtered_incidents)
        calculate_distance_error(SCENARIO_POINT, REF_POINT, incident)
        results[angle] = round(distance(REF_POINT, incident))

    # write calculated distances in csv
    with open('results.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['angle', 'distance'])
        for row in sorted(results.items()):
            writer.writerow(row)


if __name__ == '__main__':
    main()

