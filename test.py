# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:31:14 2018

@author: Victor
"""

K_col_headers = ['Repeat N',
                       'Ramp to,A 1','Ramp time,s 1','Hold time,s 1',
                       'Ramp to,A 2','Ramp time,s 2','Hold time,s 2',
                       'Ramp to,A 3','Ramp time,s 3','Hold time,s 3',
                       ' X ',' Y ',' Z ',' Tilt ',' Polar ', 'Azimuth']
default_spectrum = ['5',
                                 '0.1','1','10',
                                 '3.0','5','15',
                                 '7.0','5','30',
                                 '0.0','0.0','0.0','0.0','0.0','90']
k_dictionary = dict(zip(K_col_headers,default_spectrum))

ramp_time = []
ramp_current = []
hold_time = []

for i in k_dictionary.keys(): 
    if 'Ramp to,A' in str(i):
        ramp_time.append( int(k_dictionary['Ramp time,s '+str(i)[-1]]))
        hold_time.append( float(k_dictionary['Hold time,s '+str(i)[-1]]))
        ramp_current.append (float(k_dictionary[i]))
    else:
        pass
print ('Ramp current list', ramp_current)
print ('Ramp time list', ramp_time)
print ('Hold time list', hold_time)