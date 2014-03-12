#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from annotations import *
import wx

class DomainPanel(wx.Panel):

    def createControls(self):

        # Add Label Form
        self.addLabelButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap('media/add.png'))
        self.addLabelLabel = wx.StaticText(self, label="Label:")
        self.addLabelInput = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)

        # List of domain labels
        self.domainLabelsLabel = wx.StaticText(self, wx.ID_ANY,
                                               "Domain labels")
        self.domainLabelsList = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                           (200, 300), [],
                                           wx.LB_SINGLE|wx.EXPAND)
        self.domainLabelsList.SetSelection(0)

        # List of label features
        self.domainFeaturesLabel = \
            wx.StaticText(self, wx.ID_ANY, "Domain labels")
        self.domainFeaturesList = \
            wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (200, 300), [],
                       wx.LB_SINGLE|wx.EXPAND)
        
        self.domainFeaturesList.SetSelection(0)
        
        # Global commands (Load, Save, New, ...)
        self.newDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap('media/new.png'), style=wx.NO_BORDER, pos=(10, 10))
        self.openDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap('media/open.png'), style=wx.NO_BORDER, pos=(10, 10))
        self.saveDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap('media/save.png'), style=wx.NO_BORDER, pos=(10, 10))
    
    def addTooltips(self):
        self.addLabelButton.SetToolTip(wx.ToolTip("Add label to domain"))
        self.newDomainButton.SetToolTip(wx.ToolTip("New empty domain"))
        self.openDomainButton.SetToolTip(wx.ToolTip("Open domain"))
        self.saveDomainButton.SetToolTip(wx.ToolTip("Save the domain"))
    
    def bindControls(self):
        self.addLabelInput.Bind(wx.EVT_TEXT_ENTER, self.OnAddLabel)
        self.addLabelButton.Bind(wx.EVT_BUTTON, self.OnAddLabel)
        self.domainLabelsList.Bind(wx.EVT_LISTBOX, self.OnLabelSelect)
        self.domainFeaturesList.Bind(wx.EVT_LISTBOX, self.OnFeatureSelect)
        
        self.newDomainButton.Bind(wx.EVT_BUTTON, self.top_app.OnNewProject)
        self.openDomainButton.Bind(wx.EVT_BUTTON, self.top_app.OnLoadDomain)
        self.saveDomainButton.Bind(wx.EVT_BUTTON, self.top_app.OnSaveDomain)
    
    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)          # Global
        left_sizer = wx.BoxSizer(wx.VERTICAL)       # Left bar
        right_sizer = wx.BoxSizer(wx.VERTICAL)      # Right bar
        
        form_sizer = wx.BoxSizer(wx.HORIZONTAL)     # Add label form
        labels_sizer = wx.BoxSizer(wx.VERTICAL)     # List of labels
        features_sizer = wx.BoxSizer(wx.VERTICAL)   # List of features
        commands_sizer = wx.BoxSizer(wx.HORIZONTAL) # Commands
        
        seq = [
               # Skeleton
               (sizer, left_sizer), (sizer, right_sizer),
               (left_sizer, commands_sizer, wx.CENTER),
               (left_sizer, form_sizer, wx.CENTER),
               (left_sizer, labels_sizer),
               (left_sizer, features_sizer),
               
               # Commands
               (commands_sizer, self.newDomainButton),
               (commands_sizer, self.openDomainButton),
               (commands_sizer, self.saveDomainButton),
               
               # Add Label Form
               (form_sizer, self.addLabelLabel),
               (form_sizer, self.addLabelInput),
               (form_sizer, self.addLabelButton),

               # List of labels
               (labels_sizer, self.domainLabelsLabel),
               (labels_sizer, self.domainLabelsList),

               # List of Features
               (features_sizer, self.domainFeaturesLabel),
               (features_sizer, self.domainFeaturesList)
              ]
        
        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        
        self.SetSizer(sizer)
        self.load_domain()
    
    def __init__(self, parent, an):

        wx.Panel.__init__(self, parent=parent, id=wx.NewId())
        self.top_app = an
        
        self.createControls()
        print "created"
        self.addTooltips()
        print "tooltips added"
        self.bindControls()
        print "controls binded"
        self.setLayout()
        print "layout"
    
    def OnLabelSelect(self, event):
        index = event.GetSelection()
        print index

    def OnFeatureSelect(self, event):
        print "blah blah"
    
    def OnAddLabel(self, event):
        name = self.addLabelInput.GetValue()
        if name != "":
            self.top_app.am.domain[name] = annotation({"name":name})
            self.load_domain()
    
    def load_domain(self):
        self.domainLabelsList.Set([])
        
        if self.top_app.am is not None:
            for k in self.top_app.am.domain.keys():
                self.domainLabelsList.Append(k)
