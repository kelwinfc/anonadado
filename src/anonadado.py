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
        
        pnl = wx.Panel(self)
        #cbtn = wx.Button(pnl, label='Close', pos=(20, 30))
        #cbtn.Bind(wx.EVT_BUTTON, self.OnClose)

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        load_domain = fileMenu.Append(wx.ID_OPEN, 'Load Domain', 'Load Domain')
        load_instance = fileMenu.Append(wx.ID_SAVE, 'Load Instance',
                                        'Load Instance')
        new_project = fileMenu.Append(wx.ID_ANY, 'New Project', 'New Project')
        
        quit_item = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        
        self.SetMenuBar(menubar)
        
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        self.Bind(wx.EVT_MENU, self.OnLoadDomain, load_domain)
        self.Bind(wx.EVT_MENU, self.OnLoadInstance, load_instance)
        self.Bind(wx.EVT_MENU, self.OnNewProject, new_project)

        
        self.SetSize((250, 200))
        self.SetTitle('Anonadado')
        self.Centre()
        self.Show(True)
        self.Maximize(True)
    
    def OnClose(self, e):
        self.Close(True)

    def OnQuit(self, e):
        self.Close()

    def OnLoadDomain(self, e):
        dlg = wx.FileDialog(
            self, message = "Choose a file",
            defaultDir = os.getcwd(),
            defaultFile = "",
            wildcard = "Json (*.json)|*.json|" \
                       "All files (*.*)|*.*",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.am.parse_domain(path)
        dlg.Destroy()
    
    def OnLoadInstance(self, e):
        dlg = wx.FileDialog(
            self, message = "Choose a file",
            defaultDir = os.getcwd(),
            defaultFile = "",
            wildcard = "Json (*.json)|*.json|" \
                       "All files (*.*)|*.*",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.am.parse_instance(path)
        dlg.Destroy()

    def OnNewProject(self, e):
        dial = wx.MessageDialog(None, 'Are you sure to create a new project? '\
                                'You will lose your local changes.',
                                'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        r = dial.ShowModal()
        if r == wx.ID_YES:
            self.am = annotation_manager()
        elif r == wx.ID_NO:
            pass

def main():

    dargs = parse_args(sys.argv[1:])
    
    domain_filename = dargs.get("domain", None)
    instance_filename = dargs.get("instance", None)

    am = annotation_manager()

    if domain_filename is not None:
        am.parse_domain(domain_filename)
    if instance_filename is not None:
        am.parse_instance(instance_filename)
    
    app = wx.App()
    a = Anonadado(None)
    a.setAnnotator(am)
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
