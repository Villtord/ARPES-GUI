# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 15:05:58 2018

@author: Victor Rogalev
"""
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from data_saver import save_slice
import socket
import select
import numpy as np
from ConnectCarving import ConnectCarving


class connection_object(QObject):
    carving_finished_moving_signal = pyqtSignal(bool)
    communication_end_trigger = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.MyCarving = ConnectCarving()
        host = socket.gethostname()
        port = 7010
        print('establishing connection')
        print('host is ', host)
        self.mySocket = socket.socket()
        self.mySocket.connect((host, port))
        self.mySocket.setblocking(0)
        self.counter = 0
        self.end_of_data = False
        self.get_data_flag = False
        self.MyCarving.finished_signal.connect(self.define_spectra)

    def recvall(self, sock, buffer_size=4096):
        """ Special modification to get large data through TCP """
        buf = sock.recv(buffer_size)
        while buf:
            msg = bytearray()
            msg.extend(buf)
            yield buf
            """ check if this is the raw data stream that has ] at the end """
            if self.get_data_flag:
                if "]" in msg.decode("utf-8"):
                    self.end_of_data = True
                    break
            else:
                if len(buf) < buffer_size:
                    self.end_of_data = True
                    break
            buf = sock.recv(buffer_size)

    def communicate(self, message):
        self.end_of_data = False
        reply = ''
        self.counter += 1
        prefix = '?' + str(hex(self.counter))[2:].zfill(4) + ' '
        message = prefix + message + '\n'
        print("sending message: ", message)
        try:
            self.mySocket.send(message.encode())
            timeout = 5
            ready = select.select([self.mySocket], [], [], timeout)
            if ready[0]:
                reply = b''.join(self.recvall(self.mySocket))
        except:
            print("socket communication error occured")
            pass
        return reply.decode("utf-8")

    def prodigy_connect(self):
        message = ("Connect")
        reply = self.communicate(message)
        print("reply from server: ", reply)

    def prodigy_disconnect(self):
        message = ("Disconnect")
        reply = self.communicate(message)
        print("reply from server: ", reply)
        self.mySocket.close()

    def position_carving(self, spectra_dictionary_original, spectra_dictionary, fake_flag, dimension_info,
                         repeat_counter):
        """
        When this function is called, Carving server emits the finished signal once manipulator finishes moving.
        Once finished_signal received - the define spectra starts automatically.
        Flag to now that we are going to receive a large amount of data with ] at the end
        """
        self.get_data_flag = False

        print("setting up manipulator position ")

        """ Fake flag is True if you need just to move manipulator - the measured spectra will not be saved """
        self.fake_flag_local = fake_flag
        self.dimension_info = dimension_info
        self.spectra_dictionary = spectra_dictionary
        print (self.spectra_dictionary)
        self.spectra_dictionary_original = spectra_dictionary_original
        self.repeat_counter = repeat_counter

        clear_reply = self.communicate('ClearSpectrum')
        # if "OK" in clear_reply:
        #     self.MyCarving.move_carving(self.spectra_dictionary)

        self.MyCarving.move_carving(self.spectra_dictionary)  # TEST!"!TEST!!!TEST!!! REMOVE!!!

    def define_spectra(self):
        print("trying to validate spectra")
        self.communicate('ClearSpectrum')
        define_reply = ""
        message = ""

        if (float(self.spectra_dictionary.get(" Step (FAT),eV ")) >= 0.001) and (
                float(self.spectra_dictionary.get(" Step (FAT),eV ")) <= 10.0):

            print('This is FAT spectrum!')

            message = 'DefineSpectrumFAT StartEnergy:' + str(self.spectra_dictionary.get(" KE_start,eV ")) \
                      + ' EndEnergy:' + str(self.spectra_dictionary.get(" KE_end,eV ")) + ' StepWidth:' + str(
                self.spectra_dictionary.get(" Step (FAT),eV ")) \
                      + ' DwellTime:' + str(self.spectra_dictionary.get(" Dwell,s ")) + ' PassEnergy:' + str(
                self.spectra_dictionary.get(" E_pass,eV ")) \
                      + ' LensMode:"' + str(self.spectra_dictionary.get(" Lens_mode ")) + '"' + ' ScanRange:'
            if float(self.spectra_dictionary.get(" KE_end,eV ")) > 1400:
                message += '"3.5kV"'
            elif float(self.spectra_dictionary.get(" KE_end,eV ")) > 60 and float(
                    self.spectra_dictionary.get(" KE_end,eV ")) <= 1400:
                message += '"1.5kV"'
            elif float(self.spectra_dictionary.get(" KE_end,eV ")) > 8 and float(
                    self.spectra_dictionary.get(" KE_end,eV ")) <= 60:
                message += '"100V"'
            elif float(self.spectra_dictionary.get(" KE_end,eV ")) <= 8:
                message += '"10V"'

        if (int(self.spectra_dictionary.get(" Samples (SFAT) ")) >= 1) and (
                int(self.spectra_dictionary.get(" Samples (SFAT) ")) <= 10000):

            print('This is Snapshot (SFAT) spectrum!')

            message = 'DefineSpectrumSFAT StartEnergy:' + str(self.spectra_dictionary.get(" KE_start,eV ")) \
                      + ' EndEnergy:' + str(self.spectra_dictionary.get(" KE_end,eV ")) + ' Samples:' + str(
                self.spectra_dictionary.get(" Samples (SFAT) ")) \
                      + ' DwellTime:' + str(self.spectra_dictionary.get(" Dwell,s ")) \
                      + ' LensMode:"' + str(self.spectra_dictionary.get(" Lens_mode ")) + '"' + ' ScanRange:'
            if float(self.spectra_dictionary.get(" KE_end,eV ")) > 1400:
                message += '"3.5kV"'
            elif float(self.spectra_dictionary.get(" KE_end,eV ")) > 60 and float(
                    self.spectra_dictionary.get(" KE_end,eV ")) <= 1400:
                message += '"1.5kV"'
            elif float(self.spectra_dictionary.get(" KE_end,eV ")) > 8 and float(
                    self.spectra_dictionary.get(" KE_end,eV ")) <= 60:
                message += '"100V"'
            elif float(self.spectra_dictionary.get(" KE_end,eV ")) <= 8:
                message += '"10V"'

        define_reply = self.communicate(message)
        print("Spectrum Define reply from server: ", define_reply)

        if (define_reply[6:8]) == "OK":
            self.set_analyzer_parameters(self.spectra_dictionary)

    def set_analyzer_parameters(self, spectra_dictionary):

        self.spectra_dictionary = spectra_dictionary

        EC_reply = ""
        NEC_reply = ""
        Udet_reply = ""

        if (int(self.spectra_dictionary.get(" Channels: E ")) >= 1) and (
                int(self.spectra_dictionary.get(" Channels: E ")) <= 1325):
            message = 'SetAnalyzerParameterValue ParameterName:"NumEnergyChannels" Value:' + str(
                int(self.spectra_dictionary.get(" Channels: E ")))
            print(message)
            EC_reply = self.communicate(message)
            print("Setting E channels reply from server: ", EC_reply)
            if (EC_reply[6:8]) == "OK" and (int(self.spectra_dictionary.get(" Channels: NE ")) >= 1) and (
                    int(self.spectra_dictionary.get(" Channels: NE ")) <= 1000):
                message = 'SetAnalyzerParameterValue ParameterName:"NumNonEnergyChannels" Value:' + str(
                    int(self.spectra_dictionary.get(" Channels: NE ")))
                print(message)
                NEC_reply = self.communicate(message)
                print("Setting Non-E channels reply from server: ", NEC_reply)
                if (NEC_reply[6:8]) == "OK" and (float(self.spectra_dictionary.get(" U_det,V ")) >= 0.0) and (
                        float(self.spectra_dictionary.get(" U_det,V ")) <= 1500.0):
                    message = 'SetAnalyzerParameterValue ParameterName:"Detector Voltage" Value:' + str(
                        float(self.spectra_dictionary.get(" U_det,V ")))
                    print(message)
                    Udet_reply = self.communicate(message)
                    print('Setting up detector voltage reply from server: ', Udet_reply)
                    if (Udet_reply[6:8]) == "OK":
                        self.start_measurement()

    def start_measurement(self):
        validation_reply = ""
        start_reply = ""

        validation_reply = self.communicate('ValidateSpectrum')
        print("Validation reply from server: ", validation_reply)

        if (validation_reply[6:8]) == "OK":

            self.spectra_dictionary_original[" E_pass,eV "] = \
            validation_reply.split('PassEnergy:')[1].split(' LensMode')[0]
            self.spectra_dictionary_original[" Step (FAT),eV "] = \
            validation_reply.split('StepWidth:')[1].split(' Samples')[0]

            message = 'Start SetSafeStateAfter:"false"'
            start_reply = self.communicate(message)
            print("Start measurement: ", start_reply)

            if (start_reply[6:8]) == "OK":

                print("Starting repeated timer")
                try:
                    self.annoying_timer.timeout.connect(self.update_acquisition)
                    self.annoying_timer.start(1500)
                    print("timer already exist")
                except:
                    self.annoying_timer = QTimer(self)
                    self.annoying_timer.timeout.connect(self.update_acquisition)
                    self.annoying_timer.start(1500)

    def update_acquisition(self):
        get_status_reply = ""
        message = "GetAcquisitionStatus"
        get_status_reply = self.communicate(message)
        print(get_status_reply)
        try:
            acquired_points = int(
                get_status_reply[(get_status_reply.find("NumberOfAcquiredPoints:") + len("NumberOfAcquiredPoints:")):])
        #            print ("acquired poins: ", acquired_points)
        except:
            pass
        #        if acquired_points >=1:
        #            message_get_data = "GetAcquisitionData FromIndex:0 ToIndex:" + str(acquired_points-1)
        #            data = self.communicate(message_get_data)
        #            print ("data length:", len(data))
        #            print (data)

        if "ControllerState:finished" in get_status_reply:
            self.annoying_timer.stop()
            self.annoying_timer.disconnect()

            data_raw = ""
            message_get_data = "GetAcquisitionData FromIndex:0 ToIndex:" + str(acquired_points - 1)
            print("message to get data: ", message_get_data)
            self.get_data_flag = True
            data_raw = self.communicate(message_get_data)
            #            print (data_raw)

            if (data_raw[6:8]) == "OK" and self.end_of_data:
                print("end of data flag: ", self.end_of_data)

                try:
                    data_numpy = np.array(data_raw.split("[")[1].split("]")[0].split(","), dtype=np.float64)
                except:
                    print("raw data to numpy converision error")

                print("emitting spectra measurement end trigger")
                print("LOCAL Fake flag state at the end of measurement: ", self.fake_flag_local)

                """ Check if this is a fake spectra (just to move manipulator) or not """
                if not self.fake_flag_local:
                    save_slice(self.spectra_dictionary_original, data_numpy, self.dimension_info, self.repeat_counter)
                else:
                    pass

                self.communication_end_trigger.emit()
            else:
                print("reply to get data did not contain OK phrase")

        else:
            pass
