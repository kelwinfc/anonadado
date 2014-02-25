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

pygame.init()

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

domain_filename = None
instance_filename = None

if len(sys.argv) > 1:
    domain_filename = sys.argv[1]
if len(sys.argv) > 2:
    instance_filename = sys.argv[2]

am = annotation_manager(domain_filename, instance_filename)

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
