# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 15:18:07 2018

@author: Victor
"""
from PyQt5.QtCore import QCoreApplication
import sys
from new_k_evaporation import AnnealObject

app = QCoreApplication(sys.argv)


K_col_headers = ['Repeat N',
                       'Ramp to,A 1','Ramp time,s 1','Hold time,s 1',
                       'Ramp to,A 2','Ramp time,s 2','Hold time,s 2',
                       'Ramp to,A 3','Ramp time,s 3','Hold time,s 3',
                       'Ramp to,A 4','Ramp time,s 4','Hold time,s 4',
                       ' X ',' Y ',' Z ',' Tilt ',' Polar ', 'Azimuth']
default_spectrum = ['5',
                                 '0.2','1','5',
                                 '1.0','5','5',
                                 '2.0','5','10',
                                 '3.0','5','10',
                                 '0.0','0.0','0.0','0.0','0.0','90']
k_dictionary = dict(zip(K_col_headers,default_spectrum))



test = AnnealObject()
test.start(k_dictionary)


app.exec_()