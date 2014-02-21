#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import pygame
from pygame.locals import *
from annotations import *

pygame.init()

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

a = bool_annotation("foo")

am = annotation_manager()
