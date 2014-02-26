#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import pygame
from pygame.locals import *
from annotations import *
import numpy as np
import cv2

import cv2.cv as cv

def parse_args(a):
    def check(i, a, n, s):
        if a[i] == s and i + 1 < n:
            return True
        else:
            return False
    
    d = {}
    n = len(a)
    
    for i in xrange(n):
        if check(i, a, n, "--domain"):
            d["domain"] = a[i + 1]
        elif check(i, a, n, "--instance"):
            d["instance"] = a[i + 1]
        elif check(i, a, n, "--out-domain"):
            d["out-domain"] = a[i + 1]
        elif check(i, a, n, "--out-instance"):
            d["out-instance"] = a[i + 1]
    
    return d

pygame.init()

dargs = parse_args(sys.argv[1:])

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

domain_filename = dargs.get("domain", None)
instance_filename = dargs.get("instance", None)

am = annotation_manager()
am.parse_domain(domain_filename)
am.parse_instance(instance_filename)

if "out-domain" in dargs:
    f  = open(dargs["out-domain"], 'w')
    json.dump(am.domain_to_json(), f, indent = 4)

if "out-instance" in dargs:
    f  = open(dargs["out-instance"], 'w')
    json.dump(am.instance_to_json(), f, indent = 4)

#cap = cv2.VideoCapture('test/0.mpg')

#counter = 0
#while(cap.isOpened()):
    #ret, frame = cap.read()
    #if not ret:
        #break
    
    #counter += 1
    
    ##cv2.imshow('frame', frame)
    ##if cv2.waitKey(1) & 0xFF == ord('q'):
        ##break
    
    #if counter % 100 == 0:
        #print counter, cap.get(cv.CV_CAP_PROP_FRAME_COUNT)

#print counter

#cap.release()
#cv2.destroyAllWindows()
