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
import wx.lib.scrolledpanel as scrolled
import copy

from annotations import *
from instance_feature_widgets import *
from utils import *

widget_by_name = {"bool": InstanceBoolFeatureWidget,
                  "string": InstanceStringFeatureWidget,
                  "float": InstanceFloatFeatureWidget,
                  "int": InstanceIntFeatureWidget,
                  "choice": InstanceChoiceFeatureWidget,
                  "bbox": InstanceBoundingBoxFeatureWidget,
                  "vector": InstanceVectorFeatureWidget,
                  "point": InstancePointFeatureWidget
                }


class InstanceAnnotationWidget(wx.Panel):
    def __init__(self, parent, an, annotation):
        wx.Panel.__init__(self, parent, id=wx.NewId())
        self.top_app = an
        self.annotation = annotation

        self.createControls()
        self.addTooltips()
        self.bindControls()
        self.setLayout()
        self.top_app.instanceTab.load_domain()

    def createControls(self):
        # Name
        self.name = wx.StaticText(self, -1, self.annotation.name, (20, 100))
        font = wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.name.SetFont(font)

        self.addInterestPointButton = wx.BitmapButton(self, id=wx.ID_ANY,
                bitmap=wx.Bitmap(cwd() + "/media/pin_add.png"),
                                 style=wx.NO_BORDER, pos=(10, 10))
        self.rmInterestPointButton = wx.BitmapButton(self, id=wx.ID_ANY,
                bitmap=wx.Bitmap(cwd() + "/media/pin_rm.png"),
                                 style=wx.NO_BORDER, pos=(10, 10))
        self.prevInterestPointButton = wx.BitmapButton(self, id=wx.ID_ANY,
                bitmap=wx.Bitmap(cwd() + "/media/pin_prev.png"),
                                 style=wx.NO_BORDER, pos=(10, 10))
        self.nextInterestPointButton = wx.BitmapButton(self, id=wx.ID_ANY,
                bitmap=wx.Bitmap(cwd() + "/media/pin_next.png"),
                                 style=wx.NO_BORDER, pos=(10, 10))

        self.features = []
        for f in self.annotation.features:
            self.add_feature(f)

    def add_feature(self, f):
        nf = widget_by_name[f.ftype](self, self.top_app, self.annotation, f,
                                     wx.ID_ANY)
        self.features.append(nf)

    def addTooltips(self):
        self.addInterestPointButton.SetToolTip(
                                        wx.ToolTip("Add annotation point"))
        self.rmInterestPointButton.SetToolTip(
                                        wx.ToolTip("Remove annotation point"))
        self.prevInterestPointButton.SetToolTip(
                                wx.ToolTip("Go to previous annotation point"))
        self.nextInterestPointButton.SetToolTip(
                                wx.ToolTip("Go to next annotation point"))

    def bindControls(self):
        self.addInterestPointButton.Bind(wx.EVT_BUTTON,
                                         self.addAnnotationPoint)
        self.rmInterestPointButton.Bind(wx.EVT_BUTTON, self.rmInterestPoint)
        self.nextInterestPointButton.Bind(wx.EVT_BUTTON,
                                          self.nextInterestPoint)
        self.prevInterestPointButton.Bind(wx.EVT_BUTTON,
                                          self.previousInterestPoint)

    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.featuresSizer = wx.BoxSizer(wx.VERTICAL)
        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.commandSizer),
               (self.sizer, self.topSizer),
               (self.sizer, self.featuresSizer),

               (self.commandSizer, self.addInterestPointButton),
               (self.commandSizer, self.rmInterestPointButton),
               (self.commandSizer, self.prevInterestPointButton),
               (self.commandSizer, self.nextInterestPointButton),

               (self.topSizer, self.name)
              ]

        for f in self.features:
            seq.append((self.featuresSizer, f))

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def addAnnotationPoint(self, event):
        index = self.top_app.instanceTab.annotationsChoice.GetSelection()
        annotation = self.top_app.am.add_point_to_annotation(index,
                                        self.top_app.instanceTab.current_frame)

        tmp_frame = self.top_app.instanceTab.current_frame
        self.top_app.instanceTab.load_instance()
        self.top_app.instanceTab.select_annotation(annotation)
        self.top_app.instanceTab.current_frame = tmp_frame

    def previousInterestPoint(self, event):
        index = self.top_app.instanceTab.annotationsChoice.GetSelection()
        frame = self.top_app.instanceTab.current_frame

        next_frame = None
        current_frame = self.top_app.instanceTab.current_frame
        annotation = None
        idx = 0

        for nidx, x in enumerate(self.top_app.am.sequence[index]):
            if x.frame < current_frame:
                next_frame = x.frame
                annotation = x
                idx = nidx

        if next_frame is not None:
            self.top_app.instanceTab.current_frame = next_frame
            self.top_app.instanceTab.select_annotation(
                                        self.top_app.am.sequence[index])
            self.top_app.instanceTab.go_to_frame()

    def nextInterestPoint(self, event):
        index = self.top_app.instanceTab.annotationsChoice.GetSelection()
        frame = self.top_app.instanceTab.current_frame

        next_frame = None
        current_frame = self.top_app.instanceTab.current_frame
        annotation = None
        idx = 0

        for nidx, x in enumerate(self.top_app.am.sequence[index]):
            if x.frame > current_frame:
                next_frame = x.frame
                annotation = x
                idx = nidx
                break

        if next_frame is not None:
            self.top_app.instanceTab.current_frame = next_frame
            self.top_app.instanceTab.select_annotation(
                                        self.top_app.am.sequence[index])
            self.top_app.instanceTab.go_to_frame()

    def rmInterestPoint(self, event):
        index = self.top_app.instanceTab.annotationsChoice.GetSelection()
        annotation = self.top_app.am.rm_point_from_annotation(index,
                                        self.top_app.instanceTab.current_frame)

        tmp_frame = self.top_app.instanceTab.current_frame
        self.top_app.instanceTab.load_instance()
        self.top_app.instanceTab.select_annotation(annotation)
        self.top_app.instanceTab.current_frame = tmp_frame


class AnnotationTimeline(wx.Panel):

    """Draw a line to a panel."""

    def __init__(self, parent, id, an):
        wx.Panel.__init__(self, parent, id, size=(600, 50))
        self.top_app = an

    def frame_to_bin(self, i):
            return int(i * 600.0 / self.top_app.instanceTab.num_of_frames)

    def OnPaintSelection(self, event=None):
        if self.top_app.am is None:
            return

        if len(self.top_app.am.sequence) > 0:
            sel_i = self.top_app.instanceTab.annotationsChoice.GetSelection()
            frames = [x.frame for x in self.top_app.am.sequence[sel_i]]

            left_f = min(frames)
            right_f = max(frames)

            self.dc.SetPen(wx.Pen("red"))
            self.dc.DrawLine(self.frame_to_bin(left_f), 45,
                             self.frame_to_bin(right_f), 45)

            for f in frames:
                self.dc.DrawLine(self.frame_to_bin(f), 40,
                                 self.frame_to_bin(f), 50)

        self.dc.SetPen(wx.Pen("black"))
        current = self.top_app.instanceTab.current_frame
        self.dc.DrawLine(self.frame_to_bin(current), 0,
                             self.frame_to_bin(current), 50)

    def OnPaint(self, event=None):

        def get_points():
            points = []
            for idx, a in enumerate(self.top_app.am.sequence):
                frames = map(lambda x: x.frame, a)
                points.append((min(frames), 0))
                points.append((max(frames), 1))
            points.sort()
            return points

        def get_max_in_frame(points):
            ret = 0
            current = 0
            for (_, v) in points:
                if v == 0:
                    current += 1
                else:
                    current -= 1
                ret = max(ret, current)
            return ret

        self.dc = wx.PaintDC(self)
        self.dc.Clear()
        self.dc.SetPen(wx.Pen("grey"))
        self.dc.SetBrush(wx.Brush("grey", wx.SOLID))

        if self.top_app.am == None:
            return

        points = get_points()
        max_points = get_max_in_frame(points)

        current = 0
        for idx, (f, v) in enumerate(points):

            if idx > 0 and current > 0:
                (pf, _) = points[idx - 1]
                pf = int(self.frame_to_bin(pf))
                f = int(self.frame_to_bin(f))

                if pf == f:
                    f += 1

                h = int(40.0 * float(current) / float(max_points))
                self.dc.DrawRectangle(pf, 40 - h, f - pf, h)
            if v == 0:
                current += 1
            else:
                current -= 1

        self.OnPaintSelection()


class InstancePanel(scrolled.ScrolledPanel):

    def __init__(self, parent, an):
        scrolled.ScrolledPanel.__init__(self, parent=parent, id=wx.NewId(),
                                        size=(1100, 640),
                                        style=wx.ALWAYS_SHOW_SB)
        self.top_app = an
        self.speed = 1

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
        #self.imageControl2 = wx.StaticBitmap(self, -1, self.image)
        self.timeline = AnnotationTimeline(self, wx.ID_ANY, self.top_app)

        self.tracker = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0,
                                 maxValue=0, size=(600, 40),
                                 style=wx.SL_HORIZONTAL
                                       | wx.SL_LABELS | wx.SL_AUTOTICKS)

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
        self.video_dir = None
        self.sequence_dir = None

        # Add Annotation

        self.addAnnotationLabel = wx.StaticText(self, wx.ID_ANY,
                                               "Add annotation:")
        self.addAnnotationList = wx.ListBox(self, wx.ID_ANY,
                                            wx.DefaultPosition,
                                            (200, 100), [],
                                            wx.LB_SINGLE | wx.EXPAND)
        self.annotationsLabel = wx.StaticText(self, wx.ID_ANY,
                                               "Annotations:")
        self.addAnnotationList.SetSelection(0)

        self.annotationWidget = None

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

        self.goToPreviousButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/previous.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.goToNextButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/next.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.rmAnnotation = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/remove.png'), style=wx.NO_BORDER,
                           pos=(10, 10))

        # Annotation
        self.annotationsChoice = wx.Choice(self, id=wx.ID_ANY,
                                           choices=[])

        # Speed
        self.speedLabel = wx.StaticText(self, wx.ID_ANY, "Speed:")
        self.reduceSpeedButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/previous.png'),
                           style=wx.NO_BORDER, pos=(10, 10))
        self.speedInput = wx.TextCtrl(self, value="1", size=(40, -1),
                                      style=wx.TE_CENTRE)
        self.increaseSpeedButton = wx.BitmapButton(self, id=wx.ID_ANY,
              bitmap=wx.Bitmap(cwd() + '/media/next.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        
        self.load_instance()

    def scale_image(self):
        aux = wx.ImageFromBitmap(self.image)
        aux = aux.Scale(self.rows, self.cols, wx.IMAGE_QUALITY_HIGH)
        self.image = wx.BitmapFromImage(aux)

    def addTooltips(self):
        self.newInstanceButton.SetToolTip(wx.ToolTip("New empty instance"))
        self.openInstanceButton.SetToolTip(wx.ToolTip("Open instance"))
        self.saveInstanceButton.SetToolTip(wx.ToolTip("Save the instance"))

        self.speedInput.SetToolTip(wx.ToolTip("Speed"))
        
        self.videoFilenameButton.SetToolTip(
            wx.ToolTip("Load Video to be processed"))
        self.sequenceButton.SetToolTip(
            wx.ToolTip("Sequence of images to be processed"))

        self.addAnnotationLabel.SetToolTip(
                                        wx.ToolTip("Double click to select"))
        self.addAnnotationList.SetToolTip(wx.ToolTip("Double click to select"))

        self.goToPreviousButton.SetToolTip(
            wx.ToolTip("Go to the previous annotation"))
        self.goToNextButton.SetToolTip(
            wx.ToolTip("Go to the next annotation"))
        self.rmAnnotation.SetToolTip(
            wx.ToolTip("Remove the selected annotation"))

    def bindControls(self):

        self.newInstanceButton.Bind(wx.EVT_BUTTON, self.top_app.OnNewInstance)
        self.openInstanceButton.Bind(wx.EVT_BUTTON,
                                     self.top_app.OnLoadInstance)
        self.saveInstanceButton.Bind(wx.EVT_BUTTON,
                                     self.top_app.OnSaveInstance)
        self.videoFilenameButton.Bind(wx.EVT_BUTTON, self.OnProcessVideo)
        self.sequenceButton.Bind(wx.EVT_BUTTON, self.OnLoadSequence)
        self.tracker.Bind(wx.EVT_SCROLL_CHANGED, self.OnTrackerChanged)

        self.addAnnotationList.Bind(wx.EVT_LISTBOX_DCLICK,
                                    self.OnAddAnnotation)
        self.annotationsChoice.Bind(wx.EVT_CHOICE, self.onSelectAnnotation)

        self.goToPreviousButton.Bind(wx.EVT_BUTTON,
                                     self.onGoToPreviousAnnotation)
        self.goToNextButton.Bind(wx.EVT_BUTTON,
                                 self.onGoToNextAnnotation)
        self.rmAnnotation.Bind(wx.EVT_BUTTON,
                                 self.onRmAnnotation)

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        self.reduceSpeedButton.Bind(wx.EVT_BUTTON, self.OnReduceSpeed)
        self.increaseSpeedButton.Bind(wx.EVT_BUTTON, self.OnIncreaseSpeed)
        self.speedInput.Bind(wx.EVT_TEXT, self.OnSpeedChanged)
        
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
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)         # Right bar
        self.imageSizer = wx.BoxSizer(wx.VERTICAL)          # Images
        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)      # Commands
        self.addAnnotationSizer = wx.BoxSizer(wx.VERTICAL)
        self.annotationsSizer = wx.BoxSizer(wx.VERTICAL)
        self.instanceNameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subCommandSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.speedSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        seq = [
                # Skeleton
                (self.sizer, self.left_sizer),
                (self.sizer, self.imageSizer),
                (self.sizer, self.right_sizer),

                (self.left_sizer, self.commandSizer, wx.ALIGN_CENTER),
                (self.left_sizer, self.instanceNameSizer),
                (self.left_sizer, self.addAnnotationSizer),
                (self.left_sizer, self.subCommandSizer, wx.ALIGN_CENTER),
                (self.left_sizer, self.annotationsSizer),
                (self.left_sizer, self.speedSizer),
                
                # Instance Name
                (self.instanceNameSizer, self.instanceNameLabel),
                (self.instanceNameSizer, self.instanceNameInput),

                # Image
                (self.imageSizer, self.videoFilenameLabel),
                (self.imageSizer, self.sequenceLabel),
                (self.imageSizer, self.imageControl),
                (self.imageSizer, self.timeline),
                (self.imageSizer, self.tracker),

                # Commands
                (self.commandSizer, self.newInstanceButton),
                (self.commandSizer, self.openInstanceButton),
                (self.commandSizer, self.saveInstanceButton),
                (self.commandSizer, self.videoFilenameButton),
                (self.commandSizer, self.sequenceButton),

                (self.subCommandSizer, self.goToPreviousButton),
                (self.subCommandSizer, self.goToNextButton),
                (self.subCommandSizer, self.rmAnnotation),

                # Add annotation
                (self.addAnnotationSizer, self.addAnnotationLabel),
                (self.addAnnotationSizer, self.addAnnotationList),

                # Annotations
                (self.annotationsSizer, self.annotationsLabel),
                (self.annotationsSizer, self.annotationsChoice),
                
                # Speed
                (self.speedSizer, self.speedLabel),
                (self.speedSizer, self.reduceSpeedButton),
                (self.speedSizer, self.speedInput),
                (self.speedSizer, self.increaseSpeedButton)
        
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
        self.SetupScrolling()

        self.imageControl.Bind(wx.EVT_LEFT_DOWN, self.OnMousePress)
        self.imageControl.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRelease)
        
    def load_sequence(self):
        try:
            print self.sequence_dir + "/anonadado.data"
            lines = open(self.sequence_dir + "/anonadado.data").readlines()
            vpath = lines[0]
            self.video_dir = vpath
            self.num_of_frames = int(lines[1])
            self.videoFilenameLabel.SetLabel("Video: " + vpath)
            self.videoFilenameLabel.SetToolTip(wx.ToolTip(vpath))
            self.sequenceLabel.SetLabel("Sequence: " + self.sequence_dir)
            self.sequenceLabel.SetToolTip(wx.ToolTip(self.sequence_dir))
            
            if self.current_frame is None:
                self.current_frame = 0
            
            self.tracker.SetMax(self.num_of_frames)
            self.top_app.am.sequence_filename = self.sequence_dir
            self.top_app.am.video_filename = self.video_dir
            self.Layout()
            self.go_to_frame()
        except:
            wx.MessageBox('Invalid sequence folder', 'Error',
                           wx.OK | wx.ICON_ERROR)

    def go_to_frame(self):
        if self.num_of_frames == 0 or self.sequence_dir is None:
            return
        
        self.tracker.SetValue(self.current_frame)
        self.image = wx.Bitmap(self.sequence_dir + "/" + \
                               str(self.current_frame) + ".jpg")
        
        self.scale_image()
        self.imageControl.SetBitmap(self.image)
        self.timeline.OnPaint()
        self.Draw()
    
    def get_annotation_point(self, annotation):
        frames = [x.frame for x in annotation]
        min_dist = self.num_of_frames * 2
        index = 0
        
        for idx, x in enumerate(frames):
            next_dist = abs(x - self.current_frame)
            if next_dist < min_dist and x <= self.current_frame:
                min_dist = next_dist
                index = idx
        return index

    def select_annotation(self, annotation, change_selection=True):
        index = self.get_annotation_point(annotation)
        
        if change_selection:
            self.annotationsChoice.SetSelection(
                    self.top_app.am.get_annotation_index(annotation[index]))
        
        if self.annotationWidget is not None:
            self.annotationWidget.Hide()
            self.annotationWidget = None
        
        self.annotationWidget = InstanceAnnotationWidget(self, self.top_app,
                                                         annotation[index])
        self.right_sizer.Add(self.annotationWidget, 0, wx.ALIGN_LEFT, 5)
        
        self.Layout()
        
        self.SetupScrolling()
        
        self.current_frame = annotation[index].frame
        self.go_to_frame()
    
    def onGoToPreviousAnnotation(self, event):
        last = None
        new_frame = self.current_frame

        for a in self.top_app.am.sequence:
            if a[0].frame < self.current_frame:
                new_frame = a[0].frame
                last = a

        if last is not None:
            self.current_frame = new_frame
            self.go_to_frame()
            self.select_annotation(last)

    def onGoToNextAnnotation(self, event=None):
        first = None
        new_frame = self.current_frame

        for a in self.top_app.am.sequence:
            if a[0].frame > self.current_frame:
                first = a
                new_frame = a[0].frame
                break

        if first is not None:
            self.current_frame = new_frame
            self.go_to_frame()
            self.select_annotation(first)

    def onSelectAnnotation(self, event):
        index = self.annotationsChoice.GetSelection()
        annotation = self.top_app.am.get_annotation(index)

        first_point = min([x.frame for x in annotation])
        self.current_frame = first_point
        self.select_annotation(annotation, False)

    def onRmAnnotation(self, event):
        index = self.annotationsChoice.GetSelection()
        if self.top_app is None or self.top_app.am is None or index < 0:
            return

        self.top_app.am.rm_annotation(index)

        if len(self.top_app.am.sequence) > 0:
            self.select_annotation(self.top_app.am.sequence[0])
        self.load_instance()

    def OnAddAnnotation(self, event):
        if self.num_of_frames == 0:
            return
        
        annotation_label = self.addAnnotationList.GetStringSelection()
        annotation = self.top_app.am.domain[annotation_label].get_instance()
        annotation.frame = self.current_frame
        self.top_app.am.add_annotation(annotation)
        self.load_instance()
        self.select_annotation([annotation])

    def OnTrackerChanged(self, event):
        self.current_frame = self.tracker.GetValue()
        self.go_to_frame()

    def OnLoadSequence(self, event):
        dlg = wx.DirDialog(self, message="Choose a file",
                             defaultPath=os.getcwd(),
                             style=wx.OPEN
                            )
        if dlg.ShowModal() == wx.ID_OK:
            #path = "/home/kelwinfc/Escritorio/anonadado/test/0"
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
        dlg = wx.FileDialog(self, message="Choose a file",
                             defaultDir=os.getcwd(),
                             defaultFile="",
                             wildcard="(*.*)" \
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
                        maximum=cap.get(cv.CV_CAP_PROP_FRAME_COUNT),
                        parent=self,
                        style=wx.PD_CAN_ABORT
                              | wx.PD_ELAPSED_TIME
                              | wx.PD_REMAINING_TIME
                              | wx.PD_ESTIMATED_TIME
                              | wx.PD_APP_MODAL
                              | wx.PD_AUTO_HIDE
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
            index = 0
            while keepGoing:
                counter = int(cap.get(cv.CV_CAP_PROP_POS_FRAMES))

                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("img", frame)
                cv2.waitKey(10)
                
                filename = dst_path + "/" + str(index) + ".jpg"
                
                if not os.path.isfile(filename):
                    cv2.imwrite(filename, frame)
                    index += 1
                (keepGoing, skip) = progress_dlg.Update(counter)

            cap.release()
            progress_dlg.Destroy()

            self.video_dir = path
            self.sequence_dir = dst_path
            self.load_sequence()

        dlg.Destroy()

    def OnGoToPrevious(self, event):
        self.current_frame = max(0, self.current_frame - self.speed)
        self.go_to_frame()

    def OnGoToNext(self, event):
        self.current_frame = min(self.num_of_frames,
                                 self.current_frame + self.speed)
        self.go_to_frame()

    def OnKeyPress(self, event):

        keycode = event.GetKeyCode()
        
        if keycode == wx.WXK_LEFT:
            self.OnGoToPrevious(self)
        if keycode == wx.WXK_RIGHT:
            self.OnGoToNext(self)
        if ord('0') <= event.GetUniChar() and event.GetUniChar() <= ord('9'):
            self.speed = event.GetUniChar() - ord('0')
            if self.speed == 0:
                self.speed = 10
            
            self.speedInput.SetValue(str(self.speed))
            self.speedInput.Layout()
            
            event.Skip()
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
        if self.top_app.am is None:
            return
        
        self.sequence_dir = self.top_app.am.sequence_filename
        self.video_dir = self.top_app.am.video_filename

        self.load_sequence()

        self.update_annotations()

    def update_annotations(self):

        if self.top_app.am is None:
            return

        self.annotationsChoice.SetItems([])

        for idx, a in enumerate(self.top_app.am.sequence):
            if len(a) > 0:
                frames = map(lambda x: x.frame, a)
                min_frame = balance(min(frames), self.num_of_frames)
                max_frame = balance(max(frames), self.num_of_frames)

                self.annotationsChoice.Append(
                    "[" + min_frame + "," + max_frame + "] " + a[0].name)

        self.go_to_frame()

    def OnMousePress(self, e):

        if self.top_app is None or self.top_app.am is None:
            return

        index = self.annotationsChoice.GetSelection()
        annotation = self.top_app.am.get_annotation(index)
        poi = self.get_annotation_point(annotation)

        annotation = self.top_app.am.sequence[index][poi]

        for f in annotation.features:
            if not f.is_active:
                continue

            if f.get_type() == "bbox" or f.get_type() == "vector":
                if f.value == None:
                    f.value = [ [x for x in y] for y in f.default ]
                
                f.value[0][0] = e.GetX()
                f.value[0][1] = e.GetY()
            
            elif f.get_type() == "point":
                if f.value == None:
                    f.value = copy.copy(f.default)

                f.value[0] = e.GetX()
                f.value[1] = e.GetY()
        self.go_to_frame()

    def OnMouseRelease(self, e):
        if self.top_app is None or self.top_app.am is None:
            return

        index = self.annotationsChoice.GetSelection()
        annotation = self.top_app.am.get_annotation(index)
        poi = self.get_annotation_point(annotation)

        annotation = self.top_app.am.sequence[index][poi]
        
        for f in annotation.features:
            if not f.is_active:
                continue

            if f.get_type() == "bbox" or f.get_type() == "vector":
                if f.value == None:
                    f.value = [ [x for x in y] for y in f.default ]
                
                f.value[1][0] = e.GetX()
                f.value[1][1] = e.GetY()

            elif f.get_type() == "point":
                if f.value == None:
                    f.value = list(f.default)

                f.value[0] = e.GetX()
                f.value[1] = e.GetY()
            break
        
        self.go_to_frame()

    def Draw(self, e=None):
        if self.top_app is None or self.top_app.am is None:
            return

        self.image = wx.Bitmap(self.sequence_dir + "/" + \
                              str(self.current_frame) + ".jpg")
        self.scale_image()

        bit = wx.EmptyBitmap(517, 524)
        dc = wx.MemoryDC(self.image)
        
        
        index = self.annotationsChoice.GetSelection()
        
        if index >= 0 and len(self.top_app.am.sequence[index]) > 0:
            annotation = self.top_app.am.get_annotation(index)
            poi = self.get_annotation_point(annotation)

            annotation = self.top_app.am.sequence[index][poi]

            for f in annotation.features:
                if f.is_active:
                    dc.SetPen(wx.Pen(wx.RED, 3))
                    dc.SetBrush(wx.Brush(wx.RED, wx.TRANSPARENT))
                else:
                    dc.SetPen(wx.Pen(wx.GREEN, 2))
                    dc.SetBrush(wx.Brush(wx.GREEN, wx.TRANSPARENT))

                if f.get_type() == "bbox":
                    if f.value == None:
                        f.value = f.default

                    bbox = f.value
                    dc.DrawRectangle(bbox[0][0], bbox[0][1],
                                     bbox[1][0] - bbox[0][0],
                                     bbox[1][1] - bbox[0][1])
                elif f.get_type() == "vector":
                    if f.value == None:
                        f.value = f.default

                    v = f.value
                    dc.DrawLine(v[0][0], v[0][1], v[1][0], v[1][1])
                elif f.get_type() == "point":
                    if f.value == None:
                        f.value = f.default

                    p = f.value
                    dc.DrawCircle(p[0], p[1], 5)

            dc.SelectObject(wx.NullBitmap)
        self.imageControl.SetBitmap(self.image)
    
    def OnIncreaseSpeed(self, e=None):
        self.speed += 1
        self.speedInput.SetValue(str(self.speed))
        self.speedInput.Layout()
    
    def OnReduceSpeed(self, e=None):
        self.speed -= 1
        
        if self.speed < 1:
            self.speed = 1
        
        self.speedInput.SetValue(str(self.speed))
        self.speedInput.Layout()
    
    def OnSpeedChanged(self, e=None):
        new_value = self.speedInput.GetValue()
        aux_value = ""
        for ch in new_value:
            if ch in "0123456789":
                aux_value += ch
        if len(aux_value) == 0:
            aux_value = "1"
        
        if str(self.speed) != aux_value or new_value != aux_value:
            self.speed = int(aux_value)
            self.speedInput.SetValue(str(self.speed))
