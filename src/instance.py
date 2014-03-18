#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from os import getcwd as cwd
import numpy as np
import wx

from annotations import *

class InstancePanel(wx.Panel):

    def __init__(self, parent, an):
        wx.Panel.__init__(self, parent=parent, id=wx.NewId())
        self.top_app = an
        
        self.createControls()
        self.addTooltips()
        self.bindControls()
        self.setLayout()
        
    def createControls(self):
        # Instance name
        self.instanceNameLabel = wx.StaticText(self, label="Instance name:")
        self.instanceNameInput = wx.TextCtrl(self)
        
        # Video
        self.rows = 600
        self.cols = 400
        
        self.image = wx.Bitmap("test/0.jpg")
        (self.rows, self.cols) = self.image.GetSize()
        factor = 600.0 / self.rows
        self.rows *= factor
        self.cols *= factor
        self.scale_image()
        
        self.imageControl = wx.StaticBitmap(self, -1, self.image)
        
        self.videoFilenameLabel = wx.StaticText(self, label="Video:")
        self.videoFilenameButton = \
            wx.BitmapButton(self, id=wx.ID_ANY,
                            bitmap=wx.Bitmap(cwd() + '/media/open.png'),
                                             style=wx.NO_BORDER,
                                             pos=(10, 10))
        
        # Global commands (Load, Save, New, ...)
        self.newInstanceButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/new.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.openInstanceButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/open.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.saveInstanceButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/save.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
    
    def scale_image(self):
        aux = wx.ImageFromBitmap(self.image)
        aux = aux.Scale(self.rows, self.cols, wx.IMAGE_QUALITY_HIGH)
        self.image = wx.BitmapFromImage(aux)
    
    def addTooltips(self):
        self.newInstanceButton.SetToolTip(wx.ToolTip("New empty instance"))
        self.openInstanceButton.SetToolTip(wx.ToolTip("Open instance"))
        self.saveInstanceButton.SetToolTip(wx.ToolTip("Save the instance"))
    
    def bindControls(self):
        
        self.newInstanceButton.Bind(wx.EVT_BUTTON, self.top_app.OnNewInstance)
        self.openInstanceButton.Bind(wx.EVT_BUTTON, self.top_app.OnLoadInstance)
        self.saveInstanceButton.Bind(wx.EVT_BUTTON, self.top_app.OnSaveInstance)
        self.videoFilenameButton.Bind(wx.EVT_BUTTON, self.OnLoadVideo)
        
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)
        
        for x in vars(self):
            try:
                if str(type(getattr(self, x))) != \
                   str(type(self.instanceNameInput)):
                    getattr(self, x).Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)
            except:
                pass
        
        self.instanceNameInput.Bind(wx.EVT_TEXT, self.OnChangeInstanceName)
    
    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)             # Global
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)          # Left bar
        self.imageSizer = wx.BoxSizer(wx.VERTICAL)          # Images
        self.instanceNameSizer = wx.BoxSizer(wx.HORIZONTAL) # Instance name
        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)      # Commands
        self.videoFilenameSizer = wx.GridSizer(2, 2, 5, 10)
        
        seq = [
                # Skeleton
                (self.sizer, self.left_sizer),
                (self.sizer, self.imageSizer),
                
                (self.left_sizer, self.commandSizer, wx.ALIGN_CENTER),
                (self.left_sizer, self.instanceNameSizer),
                (self.left_sizer, self.videoFilenameSizer),
                
                # Instance Name
                (self.videoFilenameSizer, self.instanceNameLabel),
                (self.videoFilenameSizer, self.instanceNameInput),
                
                # Load Video
                (self.videoFilenameSizer, self.videoFilenameLabel),
                (self.videoFilenameSizer, self.videoFilenameButton),
                
                # Image
                (self.imageSizer, self.imageControl),
                
                # Commands
               (self.commandSizer, self.newInstanceButton),
               (self.commandSizer, self.openInstanceButton),
               (self.commandSizer, self.saveInstanceButton)
              ]
        
        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)
        
        self.SetSizer(self.sizer)
        self.load_instance()
    
    def OnChangeInstanceName(self, event):
        if self.top_app.am is not None:
            self.top_app.am.instance_name = self.instanceNameInput.GetValue()
    
    def OnLoadInstance(self, event):
        print "load instance"
    
    def OnSaveInstance(self, event):
        print "save instance"
    
    def OnLoadVideo(self, event):
        dlg = wx.FileDialog(self, message = "Choose a file",
                             defaultDir = os.getcwd(),
                             defaultFile = "",
                             wildcard = "(*.*)" \
                                        "All files (*.*)|*.*",
                             style=wx.OPEN
                            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            
        dlg.Destroy()
    
    def OnGoToPrevious(self, event):
        print "go to previous"
    
    def OnGoToNext(self, event):
        print "go to next"
    
    def OnKeyPress(self, event):
        
        keycode = event.GetKeyCode()
        
        if event.GetKeyCode() == wx.WXK_LEFT:
            self.OnGoToPrevious(self)
        if event.GetKeyCode() == wx.WXK_RIGHT:
            self.OnGoToNext(self)
        else:
            event.Skip()
    
    def load_instance(self):
        pass