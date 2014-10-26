#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from os import getcwd as cwd
from annotations import *
import wx
import wx.lib.intctrl as intctrl

from utils import *

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

    def get_feature_index(self):
        index = -1
        for idx, f in enumerate(self.annotation.features):
            if f.name == self.feature.name:
                index = idx
        return index

    def createControls(self):
        self.name = wx.StaticText(self,
            label="[" + str(self.get_feature_index()) + "] (" + \
                  self.feature.ftype + ")\n" + self.feature.name)
        font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.name.SetFont(font)

        self.removeButton = \
            wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                            bitmap=wx.Bitmap(media("remove")),
                            pos=(10, 10))

        if len(self.annotation.features) > 0 and self.get_feature_index() > 0:
            self.moveUpButton = \
                wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                                bitmap=wx.Bitmap(media("up")),
                                pos=(10, 10))
        else:
            self.moveUpButton = \
                wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                                pos=(10, 10))

        if len(self.annotation.features) > 0 and \
                self.get_feature_index() + 1 < len(self.annotation.features):
            self.moveDownButton = \
                wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                                bitmap=wx.Bitmap(media("down")),
                                pos=(10, 10))
        else:
            self.moveDownButton = \
                wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                                pos=(10, 10))

    def setInitialValues(self):
        pass

    def bindControls(self):
        self.removeButton.Bind(wx.EVT_BUTTON, self.OnRemoveFeature)
        self.moveUpButton.Bind(wx.EVT_BUTTON, self.OnMoveUpFeature)
        self.moveDownButton.Bind(wx.EVT_BUTTON, self.OnMoveDownFeature)

    def setLayout(self, extra_values=[]):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.nameSizer, self.name),
               (self.nameSizer, self.removeButton),
               (self.nameSizer, self.moveDownButton),
               (self.nameSizer, self.moveUpButton),
              ]

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def OnRemoveFeature(self, event):
        index = self.get_feature_index()
        if index >= 0:
            del self.annotation.features[index]

            label = self.top_app.domainTab.domainLabelsList.GetSelection()
            self.top_app.domainTab.select_label(label)

    def OnMoveUpFeature(self, event):
        index = self.get_feature_index()
        if 0 < index and index < len(self.annotation.features):
            tmp = self.annotation.features[index - 1]
            self.annotation.features[index - 1] = \
                self.annotation.features[index]
            self.annotation.features[index] = tmp

            label = self.top_app.domainTab.domainLabelsList.GetSelection()
            self.top_app.domainTab.select_label(label)

    def OnMoveDownFeature(self, event):
        index = self.get_feature_index()
        if 0 <= index and index + 1 < len(self.annotation.features):
            tmp = self.annotation.features[index]
            self.annotation.features[index] = \
                self.annotation.features[index + 1]
            self.annotation.features[index + 1] = tmp

            label = self.top_app.domainTab.domainLabelsList.GetSelection()
            self.top_app.domainTab.select_label(label)


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
        FeatureWidget.bindControls(self)
        self.Bind(wx.EVT_TEXT, self.OnChangeDefault,
                  id=self.defaultInput.GetId())

    def setLayout(self, extra_values=[]):

        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.defaultSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.sizer, self.defaultSizer),

               (self.nameSizer, self.name),
               (self.nameSizer, self.removeButton),
               (self.nameSizer, self.moveDownButton),
               (self.nameSizer, self.moveUpButton),

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
            self.validValue.SetBitmap(wx.Bitmap(media("ok")))
        else:
            self.validValue.SetBitmap(wx.Bitmap(media("remove")))

    def is_valid(self):
        self.changeValidator(True)
        return True


class BoolFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)
        self.defaultInput.Hide()
        self.validValue.Hide()
        self.defaultInput = wx.Choice(self, id=wx.ID_ANY,
                                      choices=["True", "False"])
        self.defaultInput.Bind(wx.EVT_CHOICE, self.OnChangeDefault)

        for idx, x in enumerate([True, False]):
            if x == self.feature.default:
                self.defaultInput.SetSelection(idx)
                break
        self.setLayout()

    def addTooltips(self):
        pass

    def OnChangeDefault(self, event):
        name = self.defaultInput.GetStringSelection()
        self.feature.default = name

    def is_valid(self):
        return False


class StringFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def OnChangeDefault(self, event):
        self.feature.default = self.defaultInput.GetValue()


class FloatFeatureWidget(DefaultValueFeatureWidget):
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

        if self.is_valid():
            self.feature.default = float(aux_value)

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


class IntFeatureWidget(FloatFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        FloatFeatureWidget.__init__(self, parent, an, annotation,
                                    feature, id)

    def OnChangeDefault(self, event):
        new_value = self.defaultInput.GetValue()
        aux_value = ""
        for ch in new_value:
            if ch in "0123456789+-":
                aux_value += ch

        if new_value != aux_value:
            self.defaultInput.SetValue(aux_value)

        if self.is_valid():
            self.feature.default = int(aux_value)

    def is_valid(self):
        def is_number(s):
            try:
                i = int(s)
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
                            bitmap=wx.Bitmap(media("add")))
        self.addChoiceLabel = wx.StaticText(self, label="New value:")
        self.addChoiceInput = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)
        self.ChoiceLabel = wx.StaticText(self, label="Values:")
        self.ChoiceList = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                     (150, 100), self.choices,
                                     wx.LB_SINGLE | wx.EXPAND)

    def bindControls(self):
        DefaultValueFeatureWidget.bindControls(self)
        self.addChoiceButton.Bind(wx.EVT_BUTTON, self.OnAddChoice)
        self.addChoiceInput.Bind(wx.EVT_TEXT_ENTER, self.OnAddChoice)
        self.defaultInput.Bind(wx.EVT_CHOICE, self.OnChangeDefault)

    def setLayout(self, extra_values=[]):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subLeftSizer = wx.BoxSizer(wx.VERTICAL)
        self.subRightSizer = wx.BoxSizer(wx.VERTICAL)
        self.defaultSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.choicesSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.listSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.sizer, self.subSizer),

               (self.nameSizer, self.name),
               (self.nameSizer, self.removeButton),
               (self.nameSizer, self.moveDownButton),
               (self.nameSizer, self.moveUpButton),

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


class BoundingBoxFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def createControls(self):
        DefaultValueFeatureWidget.createControls(self)

        self.defaultInput.Hide()
        self.defaultLabel.Hide()
        self.validValue.Hide()

        self.UpperLeftLabel = wx.StaticText(self, label="Upper Left:  ")
        self.LowerRightLabel = wx.StaticText(self, label="Lower Right:")

        self.UpperLeftXLabel = wx.StaticText(self, label="X")
        self.UpperLeftYLabel = wx.StaticText(self, label="Y")
        self.LowerRightXLabel = wx.StaticText(self, label="X")
        self.LowerRightYLabel = wx.StaticText(self, label="Y")

        self.UpperLeftXInput = intctrl.IntCtrl(self, size=(50, -1))
        self.UpperLeftYInput = intctrl.IntCtrl(self, size=(50, -1))
        self.LowerRightXInput = intctrl.IntCtrl(self, size=(50, -1))
        self.LowerRightYInput = intctrl.IntCtrl(self, size=(50, -1))

        self.UpperLeftXInput.SetValue(self.feature.default[0][0])
        self.UpperLeftYInput.SetValue(self.feature.default[0][1])
        self.LowerRightXInput.SetValue(self.feature.default[1][0])
        self.LowerRightYInput.SetValue(self.feature.default[1][1])

    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ulSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lrSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.sizer, self.ulSizer),
               (self.sizer, self.lrSizer),

               (self.nameSizer, self.name),
               (self.nameSizer, self.removeButton),
               (self.nameSizer, self.moveDownButton),
               (self.nameSizer, self.moveUpButton),

               (self.ulSizer, self.UpperLeftLabel),
               (self.ulSizer, self.UpperLeftXLabel),
               (self.ulSizer, self.UpperLeftXInput),
               (self.ulSizer, self.UpperLeftYLabel),
               (self.ulSizer, self.UpperLeftYInput),

               (self.lrSizer, self.LowerRightLabel),
               (self.lrSizer, self.LowerRightXLabel),
               (self.lrSizer, self.LowerRightXInput),
               (self.lrSizer, self.LowerRightYLabel),
               (self.lrSizer, self.LowerRightYInput),
              ]

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def bindControls(self):
        DefaultValueFeatureWidget.bindControls(self)
        self.UpperLeftXInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)
        self.UpperLeftYInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)
        self.LowerRightXInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)
        self.LowerRightYInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)

    def OnChangeDefault(self, event):
        v = [[self.UpperLeftXInput, self.UpperLeftYInput],
             [self.LowerRightXInput, self.LowerRightYInput]
            ]
        for x in range(2):
            for y in range(2):
                if v[x][y].GetValue() < 0:
                    v[x][y].SetValue(-v[x][y].GetValue())
                self.feature.default[x][y] = v[x][y].GetValue()


class VectorFeatureWidget(BoundingBoxFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        BoundingBoxFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def createControls(self):
        BoundingBoxFeatureWidget.createControls(self)
        self.UpperLeftLabel.SetLabel("Start:")
        self.LowerRightLabel.SetLabel("End:  ")


class PointFeatureWidget(DefaultValueFeatureWidget):
    def __init__(self, parent, an, annotation, feature, id):
        DefaultValueFeatureWidget.__init__(self, parent, an, annotation,
                                           feature, id)

    def createControls(self):
        DefaultValueFeatureWidget.createControls(self)

        self.defaultInput.Hide()
        self.defaultLabel.Hide()
        self.validValue.Hide()

        self.XLabel = wx.StaticText(self, label="X")
        self.YLabel = wx.StaticText(self, label="Y")

        self.XInput = intctrl.IntCtrl(self, size=(50, -1))
        self.YInput = intctrl.IntCtrl(self, size=(50, -1))

        self.XInput.SetValue(self.feature.default[0])
        self.YInput.SetValue(self.feature.default[1])

    def setLayout(self):
        def addToSizer(sizer, item, alignment=wx.ALL):
            sizer.Add(item, 0, alignment, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pSizer = wx.BoxSizer(wx.HORIZONTAL)

        seq = [(self.sizer, self.nameSizer),
               (self.sizer, self.pSizer),

               (self.nameSizer, self.name),
               (self.nameSizer, self.removeButton),
               (self.nameSizer, self.moveDownButton),
               (self.nameSizer, self.moveUpButton),

               (self.pSizer, self.XLabel),
               (self.pSizer, self.XInput),
               (self.pSizer, self.YLabel),
               (self.pSizer, self.YInput)
              ]

        for n in seq:
            a = wx.ALL
            s = n[0]
            i = n[1]
            if len(n) == 3:
                a = n[2]
            addToSizer(s, i, a)

        self.SetSizer(self.sizer)

    def bindControls(self):
        DefaultValueFeatureWidget.bindControls(self)
        self.XInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)
        self.YInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)
        self.XInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)
        self.YInput.Bind(intctrl.EVT_INT, self.OnChangeDefault)

    def OnChangeDefault(self, event):
        v = [self.XInput, self.YInput]
        for x in range(2):
            if v[x].GetValue() < 0:
                v[x].SetValue(-v[x].GetValue())
            self.feature.default[x] = v[x].GetValue()
