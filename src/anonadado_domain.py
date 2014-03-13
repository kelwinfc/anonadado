#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from os import getcwd as cwd
from annotations import *
import wx
import wx.lib.scrolledpanel as wxScrolled
import wx.lib.intctrl as wxIntctrl

class FeatureWidget(wx.Panel):
    def __init__(self, parent, an, annotation, feature, id):
        wx.Panel.__init__(self, parent, id)

        self.top_app = an
        self.annotation = annotation
        self.feature = feature
        
        self.createControls()
        self.addTooltips()
        self.setInitialValues()
        self.bindControls()
        self.setLayout()

    def addTooltips(self):
        pass
    
    def createControls(self):
        self.name = wx.StaticText(self,
            label=self.annotation.name + "::" + self.feature.name + \
                  " (" + self.feature.ftype + ")")
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.name.SetFont(font)
    
    def setInitialValues(self):
        pass
    
    def bindControls(self):
        pass
    
    def setLayout(self, extra_values=[]):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        seq = [(self.sizer, self.name)]
        
        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

#TODO: agregar marca como positivo o negativo dependiendo si el default
#      value es correcto

class DefaultValueFeatureWidget(FeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        self.default = str(feature.default)
        FeatureWidget.__init__(self, parent, an, annotation, feature, id)
        self.changeValidator(self.is_valid())
    
    def createControls(self):
        FeatureWidget.createControls(self)

        self.defaultLabel = wx.StaticText(self, label="Default value:")
        self.defaultInput = wx.TextCtrl(self, value=self.default,
                                        style=wx.TE_PROCESS_ENTER)
        self.validValue = wx.StaticBitmap(self, id=wx.ID_ANY)
    
    def bindControls(self):
        self.Bind(wx.EVT_TEXT, self.OnChangeDefault,
                  id=self.defaultInput.GetId())
    
    def setLayout(self, extra_values=[]):

        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.defaultSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.name),
               (self.sizer, self.defaultSizer),

               (self.defaultSizer, self.defaultLabel),
               (self.defaultSizer, self.defaultInput),
               (self.defaultSizer, self.validValue)
              ]

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def OnChangeDefault(self, event):
        pass
    
    def changeValidator(self, value):
        if value:
            self.validValue.SetBitmap(wx.Bitmap(cwd() + '/media/ok.png'))
        else:
            self.validValue.SetBitmap(wx.Bitmap(cwd() + '/media/remove.png'))
    
    def is_valid(self):
        self.changeValidator(True)
        return True

class BoolFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def addTooltips(self):
        self.defaultLabel.SetToolTip(wx.ToolTip("Values: True, False"))
        self.defaultInput.SetToolTip(self.defaultLabel.GetToolTip())
    
    def OnChangeDefault(self, event):

        new_value = self.defaultInput.GetValue()
        if not self.is_valid():
            return
        
        if new_value.capitalize() == "True":
            self.feature.default = True
        elif new_value.capitalize() == "False":
            self.feature.default = False

    def is_valid(self):
        new_value = self.defaultInput.GetValue().capitalize()
        if new_value == "True" or new_value == "False":
            self.changeValidator(True)
            return True
        self.changeValidator(False)
        return False

class StringFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def OnChangeDefault(self, event):
        self.feature.default = self.defaultInput.GetValue()

class IntFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def OnChangeDefault(self, event):
        new_value = self.defaultInput.GetValue()
        aux_value = ""
        for ch in new_value:
            if ch in "0123456789.,+-e":
                aux_value += ch
        
        if new_value != aux_value:
            self.defaultInput.SetValue(aux_value)
        self.is_valid()
    
    def is_valid(self):
        def is_number(s):
            try:
                i = float(s)
            except ValueError, TypeError:
                return False
            return True
        
        new_value = self.defaultInput.GetValue().capitalize()
        
        if is_number(str(new_value)):
            self.changeValidator(True)
            return True
        self.changeValidator(False)
        return False

class ChoiceFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        self.choices = feature.values
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)
    
    def createControls(self):
        DefaultValueFeatureWidget.createControls(self)

        self.defaultInput.Hide()
        self.defaultInput = wx.Choice(self, id=wx.ID_ANY,
                                    choices=self.choices)

        for idx, x in enumerate(self.choices):
            if x == self.feature.default:
                self.defaultInput.SetSelection(idx)
                break
        
        self.validValue.Hide()
        
        self.addChoiceButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(cwd() + '/media/add.png'))
        self.addChoiceLabel = wx.StaticText(self, label="New value:")
        self.addChoiceInput = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)
        self.ChoiceLabel = wx.StaticText(self, label="Values:")
        self.ChoiceList = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                     (150, 100), self.choices,
                                     wx.LB_SINGLE|wx.EXPAND)

        #wx.Choice(self, id=wx.ID_ANY,
                                    #choices=self.choices)
    
    def bindControls(self):
        self.addChoiceButton.Bind(wx.EVT_BUTTON, self.OnAddChoice)
        self.addChoiceInput.Bind(wx.EVT_TEXT_ENTER, self.OnAddChoice)
        self.defaultInput.Bind(wx.EVT_CHOICE, self.OnChangeDefault)
    
    def setLayout(self, extra_values=[]):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.subSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subLeftSizer = wx.BoxSizer(wx.VERTICAL)
        self.subRightSizer = wx.BoxSizer(wx.VERTICAL)
        self.defaultSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.choicesSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.listSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        seq = [(self.sizer, self.name),
               (self.sizer, self.subSizer),
               
               (self.subSizer, self.subLeftSizer),
               (self.subSizer, self.subRightSizer),
               (self.subLeftSizer, self.defaultSizer),
               (self.subLeftSizer, self.choicesSizer),
               (self.subRightSizer, self.listSizer),
               
               (self.defaultSizer, self.defaultLabel),
               (self.defaultSizer, self.defaultInput),
               
               (self.choicesSizer, self.addChoiceLabel),
               (self.choicesSizer, self.addChoiceInput),
               (self.choicesSizer, self.addChoiceButton),
               
               (self.listSizer, self.ChoiceLabel),
               (self.listSizer, self.ChoiceList),
              ]
        
        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def OnAddChoice(self, event):
        s = self.addChoiceInput.GetValue()
        print s
        
        if not s in self.choices:
            self.feature.values.append(s)

            selected_label = \
                self.top_app.domainTab.domainLabelsList.GetSelection()
            self.top_app.domainTab.select_label(selected_label)
            self.Layout()
    
    def OnChangeDefault(self, event):
        name = self.defaultInput.GetStringSelection()
        self.feature.default = name
        print self.feature.default

class BoundingBoxFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)
    
    def OnChangeDefault(self, event):
        pass

widget_by_name = {"bool": BoolFeatureWidget,
                  "string": StringFeatureWidget,
                  "int": IntFeatureWidget,
                  "choice": ChoiceFeatureWidget,
                  "bbox": BoundingBoxFeatureWidget
                }

class AnnotationWidget(scrolled.ScrolledPanel):
    def __init__(self, parent, an, annotation, id):
        scrolled.ScrolledPanel.__init__(self, parent, id, size=(700,440),
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
                            bitmap=wx.Bitmap(cwd() + '/media/add.png'))
        self.addFeatureLabel = wx.StaticText(self, label="New Feature:")
        self.addFeatureInput = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)
        self.addFeatureType = wx.Choice(self, id=wx.ID_ANY,
                                        choices=widget_by_name.keys())
        self.removeButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(cwd() + '/media/remove.png'),
                            pos=(10,10))
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
        self.formSizer = wx.GridSizer(rows=2, cols=2, hgap=20, vgap=5)
        self.globalSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.uniqueSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.commandSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.addFeatureSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        seq = [ (self.sizer, self.removeButton, wx.ALIGN_RIGHT),
                (self.sizer, self.name, wx.ALIGN_CENTER),
                (self.sizer, self.formSizer, wx.CENTER),
                (self.formSizer, self.globalSizer, wx.CENTER),
                (self.formSizer, self.uniqueSizer),
                (self.sizer, self.addFeatureSizer),
                
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
              ]

        for f in self.features:
            seq.append( (self.sizer, f) )
        
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
        
        if s != "" and filter(lambda x : x.name == s,
                              self.annotation.features) == []:
            f = get_class_by_type(type_name)({"name":s, "type":type_name})
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

        # Add Label Form
        self.addLabelButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(cwd() + '/media/add.png'))
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
        
        # Global commands (Load, Save, New, ...)
        self.newDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/new.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.openDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/open.png'), style=wx.NO_BORDER,
                           pos=(10, 10))
        self.saveDomainButton = wx.BitmapButton(self, id=wx.ID_ANY,
          bitmap=wx.Bitmap(cwd() + '/media/save.png'), style=wx.NO_BORDER,
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
    
    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)          # Global
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)       # Left bar
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)      # Right bar
        
        self.form_sizer = wx.BoxSizer(wx.HORIZONTAL)     # Add label form
        self.labels_sizer = wx.BoxSizer(wx.VERTICAL)     # List of labels
        self.features_sizer = wx.BoxSizer(wx.VERTICAL)   # List of features
        self.commands_sizer = wx.BoxSizer(wx.HORIZONTAL) # Commands
        
        seq = [
               # Skeleton
               (self.sizer, self.left_sizer),
               (self.sizer, self.right_sizer),
               (self.left_sizer, self.commands_sizer, wx.CENTER),
               (self.left_sizer, self.form_sizer, wx.CENTER),
               (self.left_sizer, self.labels_sizer),
               (self.left_sizer, self.features_sizer),
               
               # Commands
               (self.commands_sizer, self.newDomainButton),
               (self.commands_sizer, self.openDomainButton),
               (self.commands_sizer, self.saveDomainButton),
               
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
    
    def OnLabelSelect(self, event):
        index = event.GetSelection()
        self.select_label(index)
    
    def OnAddLabel(self, event):
        name = self.addLabelInput.GetValue()
        if name != "":
            self.top_app.am.domain[name] = annotation({"name":name})
            self.load_domain()
    
    def select_label(self, index):
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
