#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from annotations import *
import wx

class DomainPanel(wx.Panel):

    def __init__(self, parent, an):

        wx.Panel.__init__(self, parent=parent, id=wx.NewId())
        self.top_app = an
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(left_sizer, 0, wx.ALL, 5)
        sizer.Add(right_sizer, 0, wx.ALL, 5)

        # Add label form
        saveButton = wx.BitmapButton(self, id=wx.ID_ANY, style=wx.NO_BORDER,
                                          bitmap=wx.Bitmap('media/add.png'))
        label = wx.StaticText(self, label="Label:")
        self.labelTextCtrl = wx.TextCtrl(self, value="",
                                         style=wx.TE_PROCESS_ENTER)
        self.labelTextCtrl.Bind(wx.EVT_TEXT_ENTER, self.add_label)
        
        form_sizer = wx.BoxSizer(wx.HORIZONTAL)
        form_sizer.Add(label, 0, wx.ALL, 5)
        form_sizer.Add(self.labelTextCtrl, 0, wx.ALL, 5)
        form_sizer.Add(saveButton, 0, wx.ALL, 5)
        saveButton.Bind(wx.EVT_BUTTON, self.add_label)

        left_sizer.Add(form_sizer, 0, wx.ALL, 5)

        # List of domain labels
        self.domain_labels = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition,
                                        (200, 150),
                                        [], wx.LB_SINGLE|wx.EXPAND)
        self.domain_labels.SetSelection(0)
        self.domain_labels.Bind(wx.EVT_LISTBOX, self.OnSelect)

        left_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Domain labels"))
        left_sizer.Add(self.domain_labels, wx.ID_ANY, wx.ALL)

        # Global commands (Load, Save, New)
        commands_sizer = wx.BoxSizer(wx.HORIZONTAL)

        open_domain = wx.BitmapButton(self, id=wx.ID_ANY,
                                      bitmap=wx.Bitmap('media/open.png'),
                                      style=wx.NO_BORDER,
                                      pos=(10, 10))
        save_domain = wx.BitmapButton(self, id=wx.ID_ANY,
                                      bitmap=wx.Bitmap('media/save.png'),
                                      style=wx.NO_BORDER,
                                      pos=(10, 10))

        open_domain.Bind(wx.EVT_BUTTON, self.top_app.OnLoadDomain)
        save_domain.Bind(wx.EVT_BUTTON, self.top_app.OnSaveDomain)

        commands_sizer.Add(open_domain, 0, wx.ALL, 5)
        commands_sizer.Add(save_domain, 0, wx.ALL, 5)

        left_sizer.Add(commands_sizer, 0, wx.ALL, 5)

        self.SetSizer(sizer)
        self.load_domain()

    def OnSelect(self, event):
        index = event.GetSelection()

        print index

    def add_label(self, event):
        name = self.labelTextCtrl.GetValue()
        if name != "":
            self.top_app.am.domain[name] = annotation({"name":name})
            self.load_domain()

    def load_domain(self):
        self.domain_labels.Set([])

        if self.top_app.am is not None:
            for k in self.top_app.am.domain.keys():
                self.domain_labels.Append(k)