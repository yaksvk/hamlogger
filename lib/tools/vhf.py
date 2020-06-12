#!/usr/bin/env python

import datetime
import re
import os.path
from libs import gridsquare
import json

l1 = 'abcdefghijklmnopqr'
l2 = '0123456789'
l3 = 'abcdefghijklmnopqrstuvx'
l2 = '0123456789'

def small_square_distance(sq1, sq2):

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

def points(point_distance):
    return 2 + point_distance

def execute(db_handle):
    
        sessions = db_handle.get_qso_sessions()
        
        for session in sessions[-1:]:
            print session.description

            orig_qsos = {}
            orig_gridsquares = {}
            orig_large_gridsquares = {}
            map_data = []
            
            my_gridsquare = None

            print "QSO count before check: %i" % len(session.qsos)

            for qso in session.qsos:
                # my own gridsquare
                if 'QTH_SENT' in qso.variables:
                    my_gridsquare = qso.variables.get('QTH_SENT').value
                    orig_gridsquares[my_gridsquare] = 1

                orig_qsos[qso.callsign] = qso.qth_received
                orig_gridsquares[qso.qth_received] = orig_gridsquares.get(qso.qth_received, 0) + 1
                orig_large_gridsquares[qso.qth_received[0:4]] = orig_large_gridsquares.get(qso.qth_received[0:4], 0) + 1

            for call, square in orig_qsos.items():
        
                if len(square) != 6:
                    raise ValueError("Wrong gridsquare format: %s for call: %s" % (square, call))

                latlng_from = gridsquare.gridquare2latlng(my_gridsquare)
                latlng_to = gridsquare.gridquare2latlng(square)
                map_data.append({'call': call, 'from': latlng_from, 'to': latlng_to})

            
            print json.dumps(map_data)
            print "My gridsquare: %s" % (my_gridsquare)
            print "QSO count after check: %i" % len(orig_qsos.values())
            print "original large GRID square count (multipliers) %i" % len(orig_large_gridsquares.keys())

            # compute scores
            score = 0
            max_dist = 0
            locator_max = '' 

            for qth in orig_qsos.values():
                dist = small_square_distance(my_gridsquare, qth)
                score += points(dist)
                if dist > max_dist:
                    max_dist = dist
                    locator_max = qth

            print "Score: %i multiplied: %i" % (score, score*len(orig_large_gridsquares.keys()))
            print "Max locator: %s" % locator_max


        
