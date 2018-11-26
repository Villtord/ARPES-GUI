# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 11:07:33 2018

@author: ARPES
"""
from PyQt5.QtCore import QTimer, QThread, QCoreApplication
import sys

class anneal_object (QThread):
    
    def __init__(self, *args, **kwargs):      

        super(self.__class__, self).__init__()
        
        print ("initializeed")
        
    def control_start(self):

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.make)
        self.timer.start(1000)
        
    def make(self):
        
        print ("it works!")

app = QCoreApplication(sys.argv)

new = anneal_object()

new.control_start()

app.exec_()