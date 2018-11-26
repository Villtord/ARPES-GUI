# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:17:36 2018

@author: Victor
"""


import time
from PyQt5.QtCore import pyqtSignal, QTimer, QObject

import lambda_commands as command
from datetime import datetime

com_port_name = "COM8"
time_factor = 1000         # 1 second in [milliseconds]
ramp_time_delay = 300

class anneal_object (QObject):
    """ This class defines the anneal process itself """
    global com_port_name, time_factor, ramp_time_delay

    evaporation_end_trigger = pyqtSignal()
       
    def __init__(self, *args, **kwargs):      

        super(self.__class__, self).__init__()
        
        print ("anneal initializeed")
        
        try:
            command.anneal_command("CH 1",com_port_name)
            time.sleep(0.5)
        except:
            print ("error in remote control")
        
        try:
            command.anneal_command("SO:CO 0.1",com_port_name)
            time.sleep(0.5)
        except:
            print ("error in setting zero")
      
    def start(self, k_dictionary):
        self.k_dictionary = k_dictionary

        self.ramp_time = []
        self.ramp_current = []
        self.hold_time = []
        self.counter = -1
        self.starting_current = 0.1
        
        try:
            command.anneal_command("SO:CO 0.1",com_port_name)
            time.sleep(0.5)
        except:
            print ("error in setting output")
                
        for i in self.k_dictionary.keys(): 
            if 'Ramp to,A' in str(i):
                self.ramp_time.append( int(self.k_dictionary['Ramp time,s '+str(i)[-1]]))
                self.hold_time.append( float(self.k_dictionary['Hold time,s '+str(i)[-1]]))
                self.ramp_current.append (float(self.k_dictionary[i]))
            else:
                pass
        print ('Ramp current list', self.ramp_current)
        print ('Ramp time list', self.ramp_time)
        print ('Hold time list', self.hold_time)
        
        self.control_start()
        
    def control_start(self):
        self.counter +=1
        if self.counter < len(self.ramp_current):
            
            """ shoot current """
            
            print ("******evaporation ", str(self.counter), " started")
            print(str(datetime.now()))
            
            self.delta = (self.ramp_current[int(self.counter)]-self.starting_current)/\
            (self.ramp_time[self.counter]*time_factor)*(ramp_time_delay+25)         # step during ramp includes time for serial connection 25ms
            
            print ("delta current", self.delta)
            print ("ramp time delay ", ramp_time_delay)
            
            self.variable_current = self.starting_current
            
#            try:
#                self.timer_1.timeout.connect(self.ramp_signal_anneal)
#                self.timer_1.start(ramp_time_delay)
#                print ("timer_1 already exist")
#            except:
            self.timer_1 = QTimer(self)
            self.timer_1.timeout.connect(self.ramp_signal_anneal)
            self.timer_1.start(ramp_time_delay)
        
        else:
            self.end_signal_anneal()

    
    def ramp_signal_anneal(self):
        print ("ramp loop")
        if (self.variable_current < self.ramp_current[self.counter]):
            print ("checking condition for ramp: ", self.variable_current, " <? ", self.ramp_current[self.counter] )
            self.variable_current += self.delta
            try:
                print ('setting current', self.variable_current)
                command.anneal_command("SO:CO "+ "{0:.3f}".format(self.variable_current),com_port_name)
            except:
                print ("error in setting ramp1 current")
        else:
        
            try:
                self.timer_1.stop()
                self.timer_1.disconnect()
            except:
                print ("no timer for ramp1")
            
            self.starting_current = self.ramp_current[self.counter]
            print ('near hold loop')
            try:
                command.anneal_command("SO:CO "+ "{0:.3f}".format(self.ramp_current[self.counter]),com_port_name)
            except:
                print ("error in setting final ramp1(2) current")
            
            print ("starting delay timer, ",str(datetime.now()))
            

#            try:
#                self.timer_10.timeout.connect(self.control_start)
#                self.timer_10.start(self.hold_time[self.counter]*time_factor)
#                print ("timer_10 already exist")
#            except:
            self.timer_10 = QTimer(self)
            self.timer_10.setSingleShot(True)
            self.timer_10.timeout.connect(self.control_start)
            self.timer_10.start(self.hold_time[self.counter]*time_factor)
                        
            
   
    def end_signal_anneal(self):

        print ("***evaporaiton finished")
        print(str(datetime.now()))
        """ Here deactivate power supply """
        try:
            command.anneal_command("SO:CO 0",com_port_name)
        except:
            print ("error in setting 0")
        
        try:
            self.timer_1.stop()
            self.timet_1.disconnect()
            self.timer_1.deleteLater()
        except:
            pass
        
        try:
            self.timer_10.stop()
            self.timet_10.disconnect()
            self.timer_10.deleteLater()
        except:
            pass
    
        self.evaporation_end_trigger.emit()
    
    def stop(self):

        print ("anneal interrupted")
        """Deactivate here"""
        try:
            command.anneal_command("SO:CO 0",com_port_name)
        except:
            print ("error in setting 0")
        
        try:
            self.timer_1.stop()
            self.timet_1.disconnect()          
            self.timer_1.deleteLater()
        except:
            pass
        
        try:
            self.timer_10.stop()
            self.timet_10.disconnect()
            self.timer_10.deleteLater()
        except:
            pass
