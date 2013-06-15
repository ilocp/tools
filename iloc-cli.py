#!/usr/bin/env python

import os
import sys
import csv
import time
import json
import requests


USERNAME = ""
PASSWORD = ""
BASE_URL = "http://0.0.0.0:3000/api"

def get_csv_file():
    """get a valid csv file from the arguments or the current working
    directory"""
    default_csv = 'points.csv'

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
            points.append(dict(latitude=row[0],
                longitude=row[1], heading=row[2]))
    return points

def login():
    """login to service and return the cookies"""
    cookie_tag = "_incident-locator_session"
    csrf_tag = "X-Csrf-Token"

    credentials = dict(email=USERNAME, password=PASSWORD)
    response = requests.post(BASE_URL+"/signin", data=credentials)

    cookies = {}
    cookies[cookie_tag] = response.cookies[cookie_tag]

    headers = {}
    headers[csrf_tag] = response.headers[csrf_tag]
    return cookies, headers

def post_data(points):
    """docstring for post_data"""
    cookies, headers = login()
    headers['content-type'] = 'application/json'
    #response = requests.get(BASE_URL+"/profile", cookies=cookies, headers=headers)
    for point in points:
        data = json.dumps(point)
        response = requests.post(BASE_URL+"/report", data=data,
                                 cookies=cookies, headers=headers)
        time.sleep(1.3)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

def main():
    csv_file = get_csv_file()
    points = read_csv(csv_file)
    post_data(points)
    return 0

if __name__ == "__main__":
    sys.exit(main())
