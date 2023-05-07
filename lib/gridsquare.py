#!/usr/bin/env python3
"""
Module that contains functions dealing with Maidenhead grid squares
"""

import math
import re

from typing import Union, Tuple
LatLngTuple = Tuple[float, float]

l1 = 'abcdefghijklmnopqr'
l2 = '0123456789'
l3 = 'abcdefghijklmnopqrstuvx'
gridsquare_reg = '^[A-R]{2}\d{2}([a-x]{2})?$'
gridsquare_subreg = '([A-R]{2}\d{2}[a-x]{2})'
R = 6371e3 # earth radius

def _norm_gridsquare(gridsquare: str) -> Tuple[int, ...]:
    # convert gridsquare to a tuple of numbers; letters lowercased and turned
    # to their ordinal values, integers are kept as they are.
    return tuple(int(x) if x.isdigit() else ord(x) - 97 for x in gridsquare.lower())

def is_gridsquare(text: str) -> bool:
    return bool(isinstance(text, str) and \
                re.match(gridsquare_reg, text, re.IGNORECASE))

def extract_gridsquare(text: str) -> Union[str, None]:
    # find a gridsquare as a substring of a string
    match = re.search(gridsquare_subreg, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.groups()[0]
    return None

def small_square_distance(sq1: str, sq2: str) -> int:
    # calculate small grid square distance for contest (small square = JN88)
    sq1 = sq1.lower()
    sq2 = sq2.lower()

    if len(sq1) < 6 or len(sq2) < 6:
        return -1

    x1 = (l1.index(sq1[0]) + 1)*10 + int(sq1[2:4])//10 + 1
    x2 = (l1.index(sq2[0]) + 1)*10 + int(sq2[2:4])//10 + 1

    y1 = (l1.index(sq1[1]) + 1)*10 + int(sq1[2:4]) % 10 + 1
    y2 = (l1.index(sq2[1]) + 1)*10 + int(sq2[2:4]) % 10 + 1

    x_max = len(l1)*len(l2)
    y_max = len(l1)*len(l2)

    dist_x_direct = abs(x1 - x2)
    dist_x_indirect = abs((x_max - x1) - (x_max - x2))
    dist_x = min(dist_x_direct, dist_x_indirect)

    dist_y_direct = abs(y1 - y2)
    dist_y_indirect = abs((y_max - y1) - (y_max - y2))
    dist_y = min(dist_y_direct, dist_y_indirect)

    return max(dist_x, dist_y)

def gridsquare2latlng(gridsquare: str) -> LatLngTuple:
    # get gridsquare center latlng (returns one (lat,lng))
    ((from_lat, from_lng),(to_lat, to_lng)) = gridsquare2latlngedges(gridsquare)
    center_lng = from_lng + (to_lng - from_lng)/2
    center_lat = from_lat + (to_lat - from_lat)/2

    return (center_lat, center_lng)

def gridsquare2latlngedges(gridsquare: str) -> Tuple[LatLngTuple, LatLngTuple]:
    # Convert gridsquares to lat and long and returns top/left, bottom/right 
    # ((lat,lng),(lat,lng))
    # Works for any gridsquares, from 2letter ones to theoretically infinite 
    # ones. The initial steps are 20deg. longitude and 10deg latitude and 
    # bases alternate between 10 and 24

    # convert gridsquare to decimal values
    items = _norm_gridsquare(gridsquare)

    # initial steps
    (step_lng, step_lat) = (20.0, 10.0)
    (from_lng, to_lng) = (-180.0,-180.0)
    (from_lat, to_lat) = (-90.0,-90.0)

    # step through the gridsquare one rectangle (2 items) at a time
    for i in range(0,len(items),2):
        if i == 0:
            base = 1
        else:
            base = 24 if i % 4 == 0 else 10

        (step_lng, step_lat) = (step_lng/base, step_lat/base)

        from_lng += step_lng*items[i]
        from_lat += step_lat*items[i+1]

    # return the rectangle dimensions using the last step
    return ((from_lat, from_lng), (from_lat+step_lat, from_lng+step_lng))

def dist_haversine(param1: Union[str, LatLngTuple], param2: Union[str, LatLngTuple]) -> float:
    # Standard implementation of haversine algorithm, guess operands 
    # so that we can work with both gridsquares and latlng tuples.

    if isinstance(param1, tuple):
        (lat1, lng1) = param1
    else:
        (lat1, lng1) = gridsquare2latlng(param1)

    if isinstance(param2, tuple):
        (lat2, lng2) = param2
    else:
        (lat2, lng2) = gridsquare2latlng(param2)

    (phi1, phi2) = (math.radians(lat1), math.radians(lat2))

    delta_phi = math.radians(lat2-lat1)
    delta_lambda = math.radians(lng2-lng1)

    a = (math.sin(delta_phi/2))**2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda/2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # distance is in meters so return it in km
    distance = R * c / 1000;

    return distance

def dist_ham(*args) -> int:
    # just use haversine with some "bulgarian" constants

    distance = dist_haversine(*args)
    return int(distance) + 1

if __name__ == '__main__':
    print(gridsquare2latlng('JN88oj'))
