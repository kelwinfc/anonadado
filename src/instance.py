#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from os import getcwd as cwd
import numpy as np
import wx
import tempfile
import cv2.cv as cv
import cv2

from annotations import *

class InstancePanel(wx.Panel):

    def __init__(self, parent, an):
        wx.Panel.__init__(self, parent=parent, id=wx.NewId())
        self.top_app = an
        
        self.createControls()
        self.addTooltips()
        self.bindControls()
        self.setLayout()
    
    def __del__(self):
        pass
    
    def createControls(self):
        # Instance name
        self.instanceNameLabel = wx.StaticText(self, label="Instance name:")
        self.instanceNameInput = wx.TextCtrl(self)
        
        # Video
        self.rows = 600
        self.cols = 400

        ## Video: Current image
        self.image = wx.Bitmap("test/0.jpg")
        (self.rows, self.cols) = self.image.GetSize()
        factor = 600.0 / self.rows
        self.rows *= factor
        self.cols *= factor
        self.scale_image()
        self.current_frame = 0

        ## Video: Process video
        self.imageControl = wx.StaticBitmap(self, -1, self.image)
        
        self.tracker = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0,
                                 maxValue=0, size=(600,40),
                                 style=wx.SL_HORIZONTAL
                                       |wx.SL_LABELS|wx.SL_AUTOTICKS)
        
        self.videoFilenameLabel = wx.StaticText(self, label="Video:")
        self.videoFilenameButton = \
            wx.BitmapButton(self, id=wx.ID_ANY,
                            bitmap=wx.Bitmap(cwd() + '/media/video.png'),
                                             style=wx.NO_BORDER,
                                             pos=(10, 10))
        self.num_of_frames = 0
        
        ## Video: Load video
        self.sequenceLabel = wx.StaticText(self, label="Sequence:")
        self.sequenceButton = \
            wx.BitmapButton(self, id=wx.ID_ANY,
                            bitmap=wx.Bitmap(cwd() + '/media/sequence.png'),
                                             style=wx.NO_BORDER,
                                             pos=(10, 10))
        self.sequence_dir = None
        
        # Add Annotation
        if self.top_app.am is not None:
            print self.top_app.am.domain.keys()
        
        self.addAnnotationLabel = wx.StaticText(self, wx.ID_ANY,
                                               "Add annotation:")
        self.addAnnotationList = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                           (200, 400), [],
                                           wx.LB_SINGLE|wx.EXPAND)
        self.addAnnotationList.SetSelection(0)
        
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

        self.videoFilenameButton.SetToolTip(
            wx.ToolTip("Load Video to be processed"))
        self.sequenceButton.SetToolTip(
            wx.ToolTip("Sequence of images to be processed"))
        
        self.addAnnotationLabel.SetToolTip(wx.ToolTip("Double click to select"))
        self.addAnnotationList.SetToolTip(wx.ToolTip("Double click to select"))
    
    def bindControls(self):
        
        self.newInstanceButton.Bind(wx.EVT_BUTTON, self.top_app.OnNewInstance)
        self.openInstanceButton.Bind(wx.EVT_BUTTON,
                                     self.top_app.OnLoadInstance)
        self.saveInstanceButton.Bind(wx.EVT_BUTTON,
                                     self.top_app.OnSaveInstance)
        self.videoFilenameButton.Bind(wx.EVT_BUTTON, self.OnProcessVideo)
        self.sequenceButton.Bind(wx.EVT_BUTTON, self.OnLoadSequence)
        self.tracker.Bind(wx.EVT_SCROLL_CHANGED, self.OnTrackerChanged)
        
        self.addAnnotationList.Bind(wx.EVT_LISTBOX_DCLICK, self.OnAddAnnotation)
        
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
        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)      # Commands
        self.addAnnotationSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.instanceNameSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        seq = [
                # Skeleton
                (self.sizer, self.left_sizer),
                (self.sizer, self.imageSizer),

                (self.left_sizer, self.commandSizer, wx.ALIGN_CENTER),
                (self.left_sizer, self.instanceNameSizer),
                (self.left_sizer, self.addAnnotationSizer),
                
                # Instance Name
                (self.instanceNameSizer, self.instanceNameLabel),
                (self.instanceNameSizer, self.instanceNameInput),
                
                # Image
                (self.imageSizer, self.videoFilenameLabel),
                (self.imageSizer, self.sequenceLabel),
                (self.imageSizer, self.imageControl),
                (self.imageSizer, self.tracker),

                # Commands
                (self.commandSizer, self.newInstanceButton),
                (self.commandSizer, self.openInstanceButton),
                (self.commandSizer, self.saveInstanceButton),
                (self.commandSizer, self.videoFilenameButton),
                (self.commandSizer, self.sequenceButton),
               
                # Add annotation
                (self.addAnnotationSizer, self.addAnnotationLabel),
                (self.addAnnotationSizer, self.addAnnotationList)
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

    def load_sequence(self):
        try:
            lines = open(self.sequence_dir + "/anonadado.data").readlines()
            vpath = lines[0]
            self.num_of_frames = int(lines[1])
            self.videoFilenameLabel.SetLabel("Video: " + vpath)
            self.videoFilenameLabel.SetToolTip(wx.ToolTip(vpath))

            self.sequenceLabel.SetLabel("Sequence: " + self.sequence_dir)
            self.sequenceLabel.SetToolTip(wx.ToolTip(self.sequence_dir))

            self.current_frame = 0
            self.tracker.SetMax(self.num_of_frames)
            
            self.Layout()
            self.go_to_frame()
        except:
            wx.MessageBox('Invalid sequence folder', 'Error',
                           wx.OK | wx.ICON_ERROR)
    
    def go_to_frame(self):
        self.tracker.SetValue(self.current_frame)
        
        self.image = wx.Bitmap(self.sequence_dir + "/" + \
                               str(self.current_frame) + ".jpg")
        self.scale_image()
        self.imageControl.SetBitmap(self.image)
    
    def OnAddAnnotation(self, event):
        print self.addAnnotationList.GetStringSelection()
    
    def OnTrackerChanged(self, event):
        self.current_frame = self.tracker.GetValue()
        self.go_to_frame()
    
    def OnLoadSequence(self, event):
        dlg = wx.DirDialog(self, message = "Choose a file",
                             defaultPath = os.getcwd(),
                             style=wx.OPEN
                            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.isdir(path):
                self.sequence_dir = path
                self.load_sequence()
            else:
                pass
    
    def OnChangeInstanceName(self, event):
        if self.top_app.am is not None:
            self.top_app.am.instance_name = self.instanceNameInput.GetValue()
    
    def OnLoadInstance(self, event):
        pass
    
    def OnSaveInstance(self, event):
        pass
    
    def OnProcessVideo(self, event):
        dlg = wx.FileDialog(self, message = "Choose a file",
                             defaultDir = os.getcwd(),
                             defaultFile = "",
                             wildcard = "(*.*)" \
                                        "All files (*.*)|*.*",
                             style=wx.OPEN
                            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            dst_path = '.'.join(path.split(".")[:-1])
            try:
                os.mkdir(dst_path)
            except:
                pass
            
            cap = cv2.VideoCapture(path)
            
            progress_dlg = wx.ProgressDialog(
                        "Please wait.", 
                        "Please wait while your video is processed.\n" +\
                        "The image sequence is being saved in " +\
                        dst_path + "/<frame_number>.jpg",
                        maximum = cap.get(cv.CV_CAP_PROP_FRAME_COUNT),
                        parent=self,
                        style = wx.PD_CAN_ABORT
                        |wx.PD_ELAPSED_TIME
                        |wx.PD_REMAINING_TIME
                        |wx.PD_ESTIMATED_TIME
                        |wx.PD_APP_MODAL
                        |wx.PD_AUTO_HIDE
                        )
            
            keepGoing = True
            skip = False
            
            # This file helps to recover the video that generated the sequence
            instance_description = open(dst_path + "/anonadado.data", "w")
            instance_description.writelines(
                [path + "\n", str(int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT)))]
            )
            instance_description.close()

            # Retrieve each frame and save them in order to be able to have
            # random access to any frame of the video
            while keepGoing:
                counter = int(cap.get(cv.CV_CAP_PROP_POS_FRAMES))
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                filename = dst_path + "/" + str(counter) + ".jpg"
                
                if not os.path.isfile(filename):
                    cv2.imwrite(filename, frame)
                
                (keepGoing, skip) = progress_dlg.Update(counter)
            
            cap.release()
            progress_dlg.Destroy()
            
            self.sequence_dir = dst_path
            self.load_sequence()

        dlg.Destroy()
    
    def OnGoToPrevious(self, event):
        self.current_frame = max(0, self.current_frame - 1)
        self.go_to_frame()
        
    def OnGoToNext(self, event):
        self.current_frame = min(self.num_of_frames, self.current_frame + 1)
        self.go_to_frame()
    
    def OnKeyPress(self, event):
        
        keycode = event.GetKeyCode()
        
        if event.GetKeyCode() == wx.WXK_LEFT:
            self.OnGoToPrevious(self)
        if event.GetKeyCode() == wx.WXK_RIGHT:
            self.OnGoToNext(self)
        else:
            event.Skip()
    
    def load_domain(self):
        self.addAnnotationList.Set([])
        
        if self.top_app.am is not None:
            for k in self.top_app.am.domain.keys():
                self.addAnnotationList.Append(k)
                if k == 0:
                    self.select_label(0)
        self.Layout()
    
    def load_instance(self):
        pass