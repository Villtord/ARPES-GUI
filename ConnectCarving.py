# -*- coding: utf-8 -*-
"""
Thread to get pressure values from network server located at given host, port.

Last update: 06 April 2020
Created on Wed Feb  5 15:34:14 2020

@author: Victor Rogalev
"""
import PyQt5.QtCore
import socket
import select
from PyQt5.QtCore import QObject, QRunnable, QTimer, pyqtSignal, pyqtSlot


class ConnectCarving(QObject):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.connection_flag = False
        self.host = socket.gethostbyname(socket.gethostname())  # temporary
        self.port = 63210
        print("connect carving initialized")
        if not self.connection_flag:
            print('establishing connection with Carving ', self.host)
            self.mySocket = socket.socket()
            try:
                self.mySocket.connect((self.host, self.port))
                self.connection_flag = True
                print('connection established')
            except Exception as e:
                print("no connection, ", e)
                self.connection_flag = False
                self.mySocket.close()
        else:
            print("connection already exist")
            pass

    def move_carving(self, position):
        """ Move carving to a desired position, then wait until the finished reply arrives"""
        self.position = position
        self.axis_position = ""  # (" X ", " Y ", " Z ", "Pol", "Azi", "Tilt")
        self.position_correct_flag = False
        if (float(self.position.get(" X ")) >= -15.0) and (
                float(self.position.get(" X ")) <= 15.0):
            self.axis_position += self.position.get(" X ")
            if (float(self.position.get(" Y ")) >= -10.0) and (
                    float(self.position.get(" Y ")) <= 10.0):
                self.axis_position += "," + self.position.get(" Y ")
                if (float(self.position.get(" Z ")) >= -5.0) and (
                        float(self.position.get(" Z ")) <= 202.0):
                    self.axis_position += "," + self.position.get(" Z ")
                    if (float(self.position.get(" Polar ")) >= -180.0) and (
                            float(self.position.get(" Polar ")) <= 180.0):
                        self.axis_position += "," + self.position.get(" Polar ")
                        if (float(self.position.get(" Azimuth ")) >= -90.0) and (
                                float(self.position.get(" Azimuth ")) <= 270.0):
                            self.axis_position += "," + self.position.get(" Azimuth ")
                            if (float(self.position.get(" Tilt ")) >= -32.0) and (
                                    float(self.position.get(" Tilt ")) <= 32.0):
                                self.axis_position += "," + self.position.get(" Tilt ")
                                self.position_correct_flag = True

        if self.position_correct_flag:
            try:
                print(self.mySocket.getsockname())
                print('attempt to send: ', self.axis_position)
                # self.mySocket.setblocking(0)
                try:
                    message = str(self.axis_position)
                    self.mySocket.send(message.encode())
                    print('message send')
                    timeout = 2
                    ready = select.select([self.mySocket], [], [], timeout)
                    if ready[0]:
                        response = self.mySocket.recv(1024).decode()
                        print('Received from server: ' + response)
                except Exception as e:
                    print('error here', e)
                    self.connection_flag = False
                    pass
            except:
                pass
            if self.axis_position in response:
                finished_flag = False
                while not finished_flag:
                    try:
                        finished_response = self.mySocket.recv(1024).decode()
                    except:
                        pass
                    try:
                        if finished_response == "finished":
                            print("carving movement completed", finished_response)
                            self.finished_signal.emit(True)
                    except:
                        pass

    def close(self):
        try:
            self.mySocket.close()
        except:
            pass
