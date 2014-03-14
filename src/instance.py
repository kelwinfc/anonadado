#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from annotations import *
import numpy as np
import wx

class InstancePanel(wx.Panel):

    def __init__(self, parent, an):
        wx.Panel.__init__(self, parent=parent, id=wx.NewId())
        self.top_app = an
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)