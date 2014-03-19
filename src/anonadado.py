#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import numpy as np
import cv2.cv as cv
import wx
import os
import wx.lib.agw.multidirdialog as MDD

from annotations import *
from domain import DomainPanel
from instance import InstancePanel

def parse_args(a):
    def check(i, a, n, s):
        if a[i] == s and i + 1 < n:
            return True
        else:
            return False
    
    d = {}
    n = len(a)
    
    for i in xrange(n):
        if check(i, a, n, "--domain"):
            d["domain"] = a[i + 1]
        elif check(i, a, n, "--instance"):
            d["instance"] = a[i + 1]
        elif check(i, a, n, "--out-domain"):
            d["out-domain"] = a[i + 1]
        elif check(i, a, n, "--out-instance"):
            d["out-instance"] = a[i + 1]
    
    return d

class Anonadado(wx.Frame):
    
    def __init__(self, *args, **kw):
        super(Anonadado, self).__init__(*args, **kw)
        self.am = None
        self.InitUI()
        
    def setAnnotator(self, am):
        self.am = am
    
    def InitUI(self):
        
        pnl = wx.Panel(self, -1)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        nestedNotebook = wx.Notebook(pnl, wx.NewId())
        self.domainTab = DomainPanel(nestedNotebook, self)
        self.instanceTab = InstancePanel(nestedNotebook, self)
        nestedNotebook.AddPage(self.domainTab, "Domain")
        nestedNotebook.AddPage(self.instanceTab, "Instance")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nestedNotebook, 1, wx.ALL|wx.EXPAND, 5)
        
        pnl.SetSizer(sizer)
        
        self.SetTitle('Anonadado - Annotation Tool')
        self.Centre()
        self.Show(True)
        self.Maximize(True)
    
    def OnClose(self, e):
        self.Close(True)

    def OnQuit(self, e):
        self.Close()

    def get_file_dialog(self):
        return wx.FileDialog(self, message = "Choose a file",
                             defaultDir = os.getcwd(),
                             defaultFile = "",
                             wildcard = "Json (*.json)|*.json|" \
                                        "All files (*.*)|*.*",
                             style=wx.OPEN
                            )
    
    def OnLoadDomain(self, e):
        dlg = self.get_file_dialog()
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.am.parse_domain(path)
            self.domainTab.load_domain()
        dlg.Destroy()

        if len(self.am.domain.keys()) > 0:
            self.domainTab.select_label(0)
    
    def OnLoadInstance(self, e):
        dlg = self.get_file_dialog()
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.am.parse_instance(path)
        dlg.Destroy()
    
    def OnSaveDomain(self, e):
        dlg = wx.FileDialog(self, message = "Save domain",
                            defaultDir = os.getcwd(),
                            defaultFile = "",
                            wildcard = "Json (*.json)|*.json|" \
                                       "All files (*.*)|*.*",
                            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
                           )
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]

            f  = open(path, 'w')
            json.dump(self.am.domain_to_json(), f, indent = 4)
            f.close()
        
        dlg.Destroy()

    def OnSaveInstance(self, e):
        pass
    
    def OnNewProject(self, e):
        dial = wx.MessageDialog(None, 'Are you sure to create a new project? '\
                                'You will lose your local changes.',
                                'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        r = dial.ShowModal()
        if r == wx.ID_YES:
            self.am = annotation_manager()
            self.domainTab.load_domain()
        elif r == wx.ID_NO:
            pass
    
    def OnNewInstance(self, e):
        pass
    
    # TODO: remove occurences of this label in the instance
    def OnRemoveLabel(self, e):
        dial = wx.MessageDialog(None, 'Are you sure to remove this label?',
                                'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        r = dial.ShowModal()

        if r == wx.ID_YES:
            sannotation = self.domainTab.domainLabelsList.GetSelection()
            name = self.domainTab.domainLabelsList.GetString(sannotation)
            self.am.domain.pop(name, None)
            self.domainTab.load_domain()
        elif r == wx.ID_NO:
            pass

def main():

    dargs = parse_args(sys.argv[1:])
    
    domain_filename = dargs.get("domain", None)
    instance_filename = dargs.get("instance", None)
    
    am = annotation_manager()

    
    app = wx.App()
    a = Anonadado(None)
    a.setAnnotator(am)
    if domain_filename is not None:
        am.parse_domain(domain_filename)
        a.domainTab.load_domain()
    
    if instance_filename is not None:
        am.parse_instance(instance_filename)
    
    app.MainLoop()
    
    if "out-domain" in dargs:
        f  = open(dargs["out-domain"], 'w')
        json.dump(am.domain_to_json(), f, indent = 4)
        f.close()
    
    if "out-instance" in dargs:
        f  = open(dargs["out-instance"], 'w')
        json.dump(am.instance_to_json(), f, indent = 4)
        f.close()

if __name__ == '__main__':
    main()