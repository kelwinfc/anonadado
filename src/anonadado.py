#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from annotations import *
import numpy as np
import cv2
import cv2.cv as cv
import wx
import os
import wx.lib.agw.multidirdialog as MDD
from anonadado_domain import DomainPanel
from anonadado_instance import InstancePanel

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
                             style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
                            )
    
    def OnLoadDomain(self, e):
        dlg = self.get_file_dialog()
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.am.parse_domain(path)
            self.domainTab.load_domain()
        dlg.Destroy()
    
    def OnLoadInstance(self, e):
        dlg = self.get_file_dialog()
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.am.parse_instance(path)
        dlg.Destroy()

    def OnSaveDomain(self, e):
        pass

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
    
    # TODO: remove occurences of this label in the instance
    def OnRemoveLabel(self, e):
        dial = wx.MessageDialog(None, 'Are you sure to remove this label?',
                                'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        r = dial.ShowModal()

        if r == wx.ID_YES:
            selected_annotation = self.domainTab.domainLabelsList.GetSelection()
            name = self.domainTab.domainLabelsList.GetString(selected_annotation)
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

    if "out-instance" in dargs:
        f  = open(dargs["out-instance"], 'w')
        json.dump(am.instance_to_json(), f, indent = 4)

if __name__ == '__main__':
    main()

#cap = cv2.VideoCapture('test/0.mpg')

#counter = 0
#while(cap.isOpened()):
    #ret, frame = cap.read()
    #if not ret:
        #break
    
    #counter += 1
    
    ##cv2.imshow('frame', frame)
    ##if cv2.waitKey(1) & 0xFF == ord('q'):
        ##break
    
    #if counter % 100 == 0:
        #print counter, cap.get(cv.CV_CAP_PROP_FRAME_COUNT)

#print counter

#cap.release()
#cv2.destroyAllWindows()
