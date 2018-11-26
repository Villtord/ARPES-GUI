# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 15:09:43 2018

@author: Victor Rogalev
"""

import serial.tools.list_ports
import io

def anneal_command (command, com_name):

    """ Open COM-port and send/read the command"""
    ser = serial.Serial(com_name,                   
                         baudrate=19200,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=0.025)
    
    ser_io = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1),  
                               newline = '\r',
                               line_buffering = True)
    
    """Write a command(s) """
    try:
        ser_io.write(command+"\r")
    except:
        pass
    ser.close()
    return

