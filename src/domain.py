#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from os import getcwd as cwd
import wx
import wx.lib.scrolledpanel as scrolled

from annotations import *
from domain_feature_widgets import *

widget_by_name = {"bool": BoolFeatureWidget,
                  "string": StringFeatureWidget,
                  "float": FloatFeatureWidget,
                  "int": IntFeatureWidget,
                  "choice": ChoiceFeatureWidget,
                  "bbox": BoundingBoxFeatureWidget,
                  "vector": VectorFeatureWidget,
                  "point": PointFeatureWidget
                }


class AnnotationWidget(scrolled.ScrolledPanel):
    def __init__(self, parent, an, annotation, id):
        scrolled.ScrolledPanel.__init__(self, parent, id, size=(1100, 640),
                                        style=wx.ALWAYS_SHOW_SB)
        self.SetBestSize()
        self.SetAutoLayout(1)
        self.SetupScrolling()

        self.top_app = an
        self.annotation = annotation
        self.createControls()
        self.setInitialValues()
        self.bindControls()
        self.setLayout()

    def createControls(self):
        # Name
        self.name = wx.StaticText(self, -1, self.annotation.name, (20, 100))
        font = wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.name.SetFont(font)

        # Is Global?
        self.isGlobalButtonLabel = wx.StaticText(self, label="Is Global:")
        self.isGlobalButtonTrue = wx.RadioButton(self, -1, 'True',
                                                 (10, 10), style=wx.RB_GROUP)
        self.isGlobalButtonFalse = wx.RadioButton(self, -1, 'False', (10, 10))

        # Is Unique?
        self.isUniqueButtonLabel = wx.StaticText(self, label="Is Unique:")
        self.isUniqueButtonTrue = wx.RadioButton(self, -1, 'True',
                                                 (10, 10), style=wx.RB_GROUP)
        self.isUniqueButtonFalse = wx.RadioButton(self, -1, 'False', (10, 10))

        # Add new feature form
        self.addFeatureButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(media("add")))
        self.addFeatureLabel = wx.StaticText(self, label="New Feature:")
        self.addFeatureInput = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)
        self.addFeatureType = wx.Choice(self, id=wx.ID_ANY,
                                        choices=widget_by_name.keys())
        self.removeButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(media("remove")),
                            pos=(10, 10))
        # Features
        self.features = []
        for f in self.annotation.features:
            self.add_feature(f)

    def add_feature(self, f):
        nf = widget_by_name[f.ftype](self, self.top_app, self.annotation, f,
                                     wx.ID_ANY)
        self.features.append(nf)

    def setInitialValues(self):
        if not self.annotation.is_global:
            self.isGlobalButtonFalse.SetValue(True)
        if not self.annotation.is_unique:
            self.isUniqueButtonFalse.SetValue(True)

    def bindControls(self):
        self.Bind(wx.EVT_RADIOBUTTON, self.SetGlobal,
                  id=self.isGlobalButtonTrue.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.SetGlobal,
                  id=self.isGlobalButtonFalse.GetId())

        self.isUniqueButtonTrue.Bind(wx.EVT_RADIOBUTTON, self.SetUnique)
        self.isUniqueButtonFalse.Bind(wx.EVT_RADIOBUTTON, self.SetUnique)
        self.removeButton.Bind(wx.EVT_BUTTON, self.top_app.OnRemoveLabel)
        self.addFeatureButton.Bind(wx.EVT_BUTTON, self.OnAddFeature)
        self.addFeatureInput.Bind(wx.EVT_TEXT_ENTER, self.OnAddFeature)

    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.globalSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.uniqueSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addFeatureSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.featuresSizer = wx.GridSizer(rows=len(self.features) / 2 + 1,
                                          cols=2, hgap=20, vgap=5)

        seq = [(self.sizer, self.topSizer),

               (self.topSizer, self.name),
               (self.topSizer, self.removeButton),

               (self.sizer, self.addFeatureSizer),
               (self.sizer, self.featuresSizer),

               (self.globalSizer, self.isGlobalButtonLabel),
               (self.globalSizer, self.isGlobalButtonTrue),
               (self.globalSizer, self.isGlobalButtonFalse),

               (self.uniqueSizer, self.isUniqueButtonLabel),
               (self.uniqueSizer, self.isUniqueButtonTrue),
               (self.uniqueSizer, self.isUniqueButtonFalse),

               (self.addFeatureSizer, self.addFeatureLabel),
               (self.addFeatureSizer, self.addFeatureInput),
               (self.addFeatureSizer, self.addFeatureType),
               (self.addFeatureSizer, self.addFeatureButton),

               (self.addFeatureSizer, self.globalSizer, wx.CENTER),
               (self.addFeatureSizer, self.uniqueSizer),
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
        self.SetupScrolling()

    def OnAddFeature(self, event):
        s = self.addFeatureInput.GetValue()
        type_name = self.addFeatureType.GetString(
                            self.addFeatureType.GetSelection())

        if s != "" and filter(lambda x: x.name == s,
                              self.annotation.features) == []:
            f = get_class_by_type(type_name)({"name": s, "type": type_name})
            self.annotation.features.append(f)
            self.add_feature(f)

        selected_label = self.top_app.domainTab.domainLabelsList.GetSelection()
        self.top_app.domainTab.select_label(selected_label)
        self.Layout()
        self.SetupScrolling()

    def OnFeatureSelect(self, event):
        pass

    def SetGlobal(self, event):
        self.annotation.is_global = self.isGlobalButtonTrue.GetValue()

    def SetUnique(self, event):
        self.annotation.is_unique = self.isUniqueButtonTrue.GetValue()


class DomainPanel(wx.Panel):
    def __init__(self, parent, an):
        wx.Panel.__init__(self, parent=parent, id=wx.NewId())
        self.top_app = an

        self.createControls()
        self.addTooltips()
        self.bindControls()
        self.setLayout()

    def createControls(self):

        # Domain name
        self.domainNameLabel = wx.StaticText(self, label="Domain name:")
        self.domainNameInput = wx.TextCtrl(self)

        # Add Label Form
        self.addLabelButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(media("add")))
        self.addLabelLabel = wx.StaticText(self, label="Label:")
        self.addLabelInput = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)

        # List of domain labels
        self.domainLabelsLabel = wx.StaticText(self, wx.ID_ANY,
                                               "Domain labels")
        self.domainLabelsList = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                           (200, 450), [],
                                           wx.LB_SINGLE | wx.EXPAND)
        self.domainLabelsList.SetSelection(0)

        # Global commands (Load, Save, New, ...)
        self.newDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(media("new")), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.openDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(media("open")), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.saveDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(media("save")), style=wx.NO_BORDER,
                           pos=(10, 10))

        self.annotationWidget = None

        self.select_label(0)

    def addTooltips(self):
        self.addLabelButton.SetToolTip(wx.ToolTip("Add label to domain"))
        self.newDomainButton.SetToolTip(wx.ToolTip("New empty domain"))
        self.openDomainButton.SetToolTip(wx.ToolTip("Open domain"))
        self.saveDomainButton.SetToolTip(wx.ToolTip("Save the domain"))

    def bindControls(self):
        self.addLabelInput.Bind(wx.EVT_TEXT_ENTER, self.OnAddLabel)
        self.addLabelButton.Bind(wx.EVT_BUTTON, self.OnAddLabel)
        self.domainLabelsList.Bind(wx.EVT_LISTBOX, self.OnLabelSelect)

        self.newDomainButton.Bind(wx.EVT_BUTTON, self.top_app.OnNewProject)
        self.openDomainButton.Bind(wx.EVT_BUTTON, self.top_app.OnLoadDomain)
        self.saveDomainButton.Bind(wx.EVT_BUTTON, self.top_app.OnSaveDomain)

        self.domainNameInput.Bind(wx.EVT_TEXT, self.OnChangeDomainName)

    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)            # Global
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)         # Left bar
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)        # Right bar

        self.form_sizer = wx.BoxSizer(wx.HORIZONTAL)       # Add label form
        self.labels_sizer = wx.BoxSizer(wx.VERTICAL)       # List of labels
        self.features_sizer = wx.BoxSizer(wx.VERTICAL)     # List of features
        self.commands_sizer = wx.BoxSizer(wx.HORIZONTAL)   # Commands
        self.domainNameSizer = wx.BoxSizer(wx.HORIZONTAL)  # Domain name

        seq = [
               # Skeleton
               (self.sizer, self.left_sizer),
               (self.sizer, self.right_sizer),
               (self.left_sizer, self.commands_sizer, wx.CENTER),
               (self.left_sizer, self.domainNameSizer),
               (self.left_sizer, self.form_sizer, wx.CENTER),
               (self.left_sizer, self.labels_sizer),
               (self.left_sizer, self.features_sizer),

               # Commands
               (self.commands_sizer, self.newDomainButton),
               (self.commands_sizer, self.openDomainButton),
               (self.commands_sizer, self.saveDomainButton),

               # Domain name
               (self.domainNameSizer, self.domainNameLabel),
               (self.domainNameSizer, self.domainNameInput),

               # Add Label Form
               (self.form_sizer, self.addLabelLabel),
               (self.form_sizer, self.addLabelInput),
               (self.form_sizer, self.addLabelButton),

               # List of labels
               (self.labels_sizer, self.domainLabelsLabel),
               (self.labels_sizer, self.domainLabelsList)
              ] + \
              ([(self.right_sizer, self.annotationWidget)]
                  if (self.annotationWidget is not None) else [])

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)
        self.load_domain()

    def OnChangeDomainName(self, event):
        if self.top_app.am is not None:
            self.top_app.am.domain_name = self.domainNameInput.GetValue()

    def OnLabelSelect(self, event):
        index = event.GetSelection()
        self.select_label(index)

    def OnAddLabel(self, event):
        name = self.addLabelInput.GetValue()
        if name != "":
            self.top_app.am.domain[name] = annotation({"name": name})
            self.load_domain()

    def select_label(self, index):
        if index is None:
            index = 0

        if index >= 0 and self.domainLabelsList.GetString(index) != "":

            label_name = self.domainLabelsList.GetString(index)

            if self.annotationWidget is not None:
                self.annotationWidget.Hide()
                self.right_sizer.Remove(self.annotationWidget)

            self.annotationWidget = \
                AnnotationWidget(self, self.top_app,
                                 self.top_app.am.domain[label_name],
                                 wx.ID_ANY)
            self.right_sizer.Add(self.annotationWidget, 0, wx.ALL, 5)

            self.right_sizer.Layout()
            self.sizer.Layout()

    def load_domain(self):
        self.domainLabelsList.Set([])

        if self.annotationWidget is not None:
            self.annotationWidget.Hide()
            self.right_sizer.Remove(self.annotationWidget)

        if self.top_app.am is not None:
            for k in self.top_app.am.domain.keys():
                self.domainLabelsList.Append(k)
                if k == 0:
                    self.select_label(0)
            self.domainNameInput.SetValue(self.top_app.am.domain_name)

            if self.top_app.instanceTab is not None:
                self.top_app.instanceTab.load_domain()
