#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from os import getcwd as cwd
from annotations import *
import wx
import wx.lib.intctrl as intctrl

class InstanceFeatureWidget(wx.Panel):
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

    def get_feature_index(self):
        index = -1
        for idx, f in enumerate(self.annotation.features):
            if f.name == self.feature.name:
                index = idx
        return index

    def createControls(self):
        self.name = wx.StaticText(self,
            label=self.feature.name + " (" + self.feature.ftype + ")")
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
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.nameSizer, self.name)
              ]
        
        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

class InstanceDefaultValueFeatureWidget(InstanceFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        self.default = str(feature.default)
        self.value = str(feature.value) if feature.value is not None else None
        
        InstanceFeatureWidget.__init__(self, parent, an, annotation,
                                       feature, id)
        self.changeValidator(self.is_valid())

    def createControls(self):
        InstanceFeatureWidget.createControls(self)

        self.valueLabel = wx.StaticText(self, label="Value:")
        self.valueInput = wx.TextCtrl(self,
                                      value=self.value \
                                              if self.value is not None \
                                              else self.default,
                                        style=wx.TE_PROCESS_ENTER)
        self.validValue = wx.StaticBitmap(self, id=wx.ID_ANY)
    
    def bindControls(self):
        InstanceFeatureWidget.bindControls(self)
        self.valueInput.Bind(wx.EVT_TEXT, self.OnChangeValue)

    def setLayout(self, extra_values=[]):

        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.valueSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.sizer, self.valueSizer),

               (self.nameSizer, self.name),
               
               (self.valueSizer, self.valueLabel),
               (self.valueSizer, self.valueInput),
               (self.valueSizer, self.validValue)
              ]

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def OnChangeValue(self, event):
        pass

    def changeValidator(self, value):
        if value:
            self.validValue.SetBitmap(wx.Bitmap(cwd() + '/media/ok.png'))
        else:
            self.validValue.SetBitmap(wx.Bitmap(cwd() + '/media/remove.png'))
    
    def is_valid(self):
        self.changeValidator(True)
        return True

class InstanceBoolFeatureWidget(InstanceDefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        InstanceDefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                                   feature, id)
        self.valueInput.Hide()
        self.validValue.Hide()
        self.valueInput = wx.Choice(self, id=wx.ID_ANY,
                                      choices=["True", "False"])
        self.valueInput.Bind(wx.EVT_CHOICE, self.OnChangeValue)
        
        if self.feature.value is not None:
            if self.feature.value:
                self.valueInput.SetSelection(0)
            else:
                self.valueInput.SetSelection(1)
        else:
            for idx, x in enumerate([True, False]):
                print x, self.feature.default, x == self.feature.default
                if x == self.feature.default:
                    self.valueInput.SetSelection(idx)
                    break
        
        self.setLayout()
    
    def addTooltips(self):
        pass
    
    def OnChangeValue(self, event):
        name = self.valueInput.GetStringSelection()
        self.feature.value = True if name == "True" else False
    
    def is_valid(self):
        return False

class InstanceStringFeatureWidget(InstanceDefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        InstanceDefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                                   feature, id)

    def OnChangeValue(self, event):
        self.feature.value = self.valueInput.GetValue()

class InstanceFloatFeatureWidget(InstanceDefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        InstanceDefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                                   feature, id)

    def OnChangeValue(self, event):
        new_value = self.valueInput.GetValue()
        aux_value = ""
        for ch in new_value:
            if ch in "0123456789.,+-e":
                aux_value += ch
        
        if new_value != aux_value:
            self.valueInput.SetValue(aux_value)
            
        if self.is_valid():
            self.feature.value = float(aux_value)
    
    def is_valid(self):
        def is_number(s):
            try:
                i = float(s)
            except ValueError, TypeError:
                return False
            return True

        new_value = self.valueInput.GetValue().capitalize()

        if is_number(str(new_value)):
            self.changeValidator(True)
            return True
        self.changeValidator(False)
        return False

class InstanceIntFeatureWidget(InstanceFloatFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        InstanceFloatFeatureWidget.__init__(self, parent, an, annotation,
                                            feature, id)

    def OnChangeValue(self, event):
        new_value = self.valueInput.GetValue()
        aux_value = ""
        for ch in new_value:
            if ch in "0123456789+-":
                aux_value += ch
        
        if new_value != aux_value:
            self.valueInput.SetValue(aux_value)

        if self.is_valid():
            self.feature.value = int(aux_value)
    
    def is_valid(self):
        def is_number(s):
            try:
                i = int(s)
            except ValueError, TypeError:
                return False
            return True
        
        new_value = self.valueInput.GetValue().capitalize()

        if is_number(str(new_value)):
            self.changeValidator(True)
            return True
        self.changeValidator(False)
        return False

class InstanceChoiceFeatureWidget(InstanceDefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        self.choices = feature.values
        InstanceDefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                                   feature, id)

    def createControls(self):
        InstanceDefaultValueFeatureWidget.createControls(self)
        self.validValue.Hide()
        self.valueInput.Hide()
        self.valueInput = wx.Choice(self, id=wx.ID_ANY,
                                    choices=self.choices)

        for idx, x in enumerate(self.choices):
            if (self.feature.value is not None and x == self.feature.value) or\
               (self.feature.value is None and x == self.feature.default):
                self.valueInput.SetSelection(idx)
                break
    
    def bindControls(self):
        InstanceDefaultValueFeatureWidget.bindControls(self)
        self.valueInput.Bind(wx.EVT_CHOICE, self.OnChangeValue)

    def setLayout(self, extra_values=[]):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.valueSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        seq = [(self.sizer, self.nameSizer),
               (self.sizer, self.subSizer),

               (self.nameSizer, self.name),
               
               (self.subSizer, self.valueSizer),
               
               (self.valueSizer, self.valueLabel),
               (self.valueSizer, self.valueInput)
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

    def OnChangeValue(self, event):
        self.feature.value = self.valueInput.GetStringSelection()