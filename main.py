# -*- coding: utf-8 -*-
"""
Photoemission experiment GUI.
Requirements: SpecsLab Prodigy with enabled remote-in option, Specs Carving manipulator.
3D data in a table must be in a form: X_start:X_end:X_number_of_points

Last Updated: 30 July 2020
Created on Wed Sep  5 15:33:05 2018

@author: Victor Rogalev

02 October: vectors in more than one parameters:X,Y,Z,Theta... added
26 October: save/load options for experiment added

"""
import pickle
import sys

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QComboBox, QFileDialog

from carving_object import CarvingObject
from my_table import MyTable
from new_k_evaporation import AnnealObject
from prodigy_object import ProdigyObject


class Window(QtWidgets.QWidget):
    can_evaporate_trigger = pyqtSignal()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.MyProdigy = ProdigyObject()
        self.MyCarving = CarvingObject()
        # self.Doping = AnnealObject()

        self.MyProdigy.prodigy_connect()
        self.MyProdigy.communication_end_trigger.connect(self.check_what_to_do_next)

        self.MyCarving.finished_signal.connect(self.check_what_to_do_next)

        self.can_evaporate_trigger.connect(self.start_evaporation)
        "measure spectra when evaporation is done"
        # self.Doping.evaporation_end_trigger.connect(self.evaporation_end)
        # self.MyCarving.signals.progress.connect (self.reply_from_carving)

        self.setup_interface()

    def setup_interface(self):
        """ Create photoemission experiment table """
        self.ARPES_table = MyTable(1, 18)
        self.ARPES_col_headers = [
            ' Name ', 'Repeat', ' KE_start,eV ', ' KE_end,eV ', ' Step (FAT),eV ',
            ' Samples (SFAT) ', ' E_pass,eV ', ' Lens_mode ',
            ' Channels: E ', ' Channels: NE ', ' Dwell,s ', ' U_det,V ',
            ' X ', ' Y ', ' Z ', ' Polar ', ' Azimuth ', ' Tilt '
        ]
        header_ARPES_table = self.ARPES_table.horizontalHeader()
        header_ARPES_table.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        for i in range(1, self.ARPES_table.columnCount()):
            header_ARPES_table.setSectionResizeMode(int(i), QtWidgets.QHeaderView.ResizeToContents)

        """ Set up default photoemission spectrum """
        self.default_spectrum = [
            'TestTest', '10', '16.0', '17.0', '0',
            '1', '10.0', 'WideAngleMode',
            '100', '500', '1', '1450',
            '8', '-8', '202', '-130', '0', '-5:5:21'
        ]

        for i in range(len(self.default_spectrum)):
            number = QTableWidgetItem(self.default_spectrum[i])
            self.ARPES_table.setCurrentCell(0, i)
            self.ARPES_table.setItem(0, i, number)

        self.ARPES_table.setHorizontalHeaderLabels(self.ARPES_col_headers)

        self.combo_box_lens = QComboBox()
        self.lens_modes_options = ["WideAngleMode", "LowAngleMode", "HighMagnification", "MediumMagnification",
                                   "MeduimArea"]
        for t in self.lens_modes_options:
            self.combo_box_lens.addItem(t)
        self.ARPES_table.setCellWidget(0, 7, self.combo_box_lens)

        """ Create K-dose table """
        self.K_table = MyTable(1, 16)
        self.K_col_headers = [
            'Repeat N',
            'Ramp to,A 1', 'Ramp time,s 1', 'Hold time,s 1',
            'Ramp to,A 2', 'Ramp time,s 2', 'Hold time,s 2',
            'Ramp to,A 3', 'Ramp time,s 3', 'Hold time,s 3',
            ' X ', ' Y ', ' Z ', ' Polar ', ' Azimuth ', ' Tilt '
        ]

        self.K_table.setHorizontalHeaderLabels(self.K_col_headers)
        header_K_table = self.K_table.horizontalHeader()
        for i in range(self.K_table.columnCount()):
            header_K_table.setSectionResizeMode(int(i), QtWidgets.QHeaderView.Stretch)

        for i in range(10, self.K_table.columnCount()):
            header_K_table.setSectionResizeMode(int(i), QtWidgets.QHeaderView.ResizeToContents)

        """ Set up default K-dose recipee """
        self.default_spectrum = [
            '1',
            '0.1', '1', '5',
            '1.0', '5', '5',
            '2.0', '5', '10',
            '0.0', '0.0', '0.0', '0.0', '90', '0.0'
        ]
        for i in range(len(self.default_spectrum)):
            number = QTableWidgetItem(self.default_spectrum[i])
            self.K_table.setCurrentCell(0, i)
            self.K_table.setItem(0, i, number)

        """ GUI Layout """
        self.K_table.setMaximumHeight(55)
        self.h_layout_1 = QtWidgets.QHBoxLayout()
        self.k_radiobutton = QtWidgets.QRadioButton('Use K-dope')
        self.load_button = QtWidgets.QPushButton('Load')
        self.save_button = QtWidgets.QPushButton('Save')
        self.h_layout_1.addWidget(self.k_radiobutton)
        self.h_layout_1.addStretch()
        self.h_layout_1.addWidget(self.save_button)
        self.h_layout_1.addWidget(self.load_button)

        self.h_layout_2 = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton('Start')
        self.ksave_button = QtWidgets.QPushButton('Save')
        self.kload_button = QtWidgets.QPushButton('Load')
        self.h_layout_2.addWidget(self.start_button)
        self.h_layout_2.addStretch()
        self.h_layout_2.addWidget(self.ksave_button)
        self.h_layout_2.addWidget(self.kload_button)

        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.addWidget(self.ARPES_table)
        self.v_layout.addLayout(self.h_layout_1)
        self.v_layout.addWidget(self.K_table)
        self.v_layout.addLayout(self.h_layout_2)

        self.setLayout(self.v_layout)

        self.K_table.setEnabled(False)

        "Connect all signals and slots for buttons"
        self.k_radiobutton.clicked.connect(self.disable_k_table)
        self.start_button.clicked.connect(self.start)
        self.save_button.clicked.connect(self.save_file)
        self.load_button.clicked.connect(self.load_file)

        self.show()

    def load_file(self):
        """ read values from saved file to a dictionary and then load it to GUI """
        load_file_name = QFileDialog.getOpenFileName(self, 'Open file', '', '*.pkl')

        with open(load_file_name[0], 'rb') as f:
            self.loaded_settings_ARPES = pickle.load(f)
            self.loaded_settings_K = pickle.load(f)

        f.close()
        #        print(self.loaded_settings)
        for col in range(self.ARPES_table.columnCount()):
            number = QTableWidgetItem(self.loaded_settings_ARPES[self.ARPES_col_headers[col]])
            self.ARPES_table.setCurrentCell(0, int(col))
            self.ARPES_table.setItem(0, int(col), number)

        for col in range(self.K_table.columnCount()):
            number = QTableWidgetItem(self.loaded_settings_K[self.K_col_headers[col]])
            self.K_table.setCurrentCell(0, int(col))
            self.K_table.setItem(0, int(col), number)

        self.combo_box_lens.setCurrentText(self.loaded_settings_ARPES[' Lens_mode '])
        self.k_radiobutton.setChecked(self.loaded_settings_ARPES[' K_radiobutton '])

    def save_file(self):
        """ write values from table to a dictionary and then save it to a .pkl file """
        self.save_string = {}

        """ Read spectra parameters from the table """
        self.ARPES_values = [self.ARPES_table.item(0, int(col)).text() for col in range(self.ARPES_table.columnCount())]

        """ Read K-dope parameters from the table and add them to spectra parameters list"""
        self.K_values = [self.K_table.item(0, int(col)).text() for col in range(self.K_table.columnCount())]

        """ Write a dictionary of column headers and parameters """
        self.ARPES_save_string = dict(zip(self.ARPES_col_headers, self.ARPES_values))
        self.K_save_string = dict(zip(self.K_col_headers, self.K_values))
        """ Add some missing parameters """
        self.ARPES_save_string[' Lens_mode '] = self.combo_box_lens.currentText()
        self.ARPES_save_string[' K_radiobutton '] = self.k_radiobutton.isChecked()
        #        print ("saving string: ", self.ARPES_save_string)

        save_file_string = QFileDialog.getSaveFileName(self, 'Save file as', '')

        if save_file_string[0].endswith('.pkl'):
            with open(save_file_string[0], 'wb') as f:
                pickle.dump(self.ARPES_save_string, f)
                pickle.dump(self.K_save_string, f)
        else:
            with open(save_file_string[0] + '.pkl', 'wb') as f:
                pickle.dump(self.save_string, f)
                pickle.dump(self.K_save_string, f)
        f.close()

    def disable_k_table(self):
        if self.k_radiobutton.isChecked():
            self.K_table.setEnabled(True)
        else:
            self.K_table.setEnabled(False)

    def start(self):
        """ Main action when user press the Start/Stop button. So far reads only first row from the table. Define
         analyser dictionary with settings, manipulator positions dictionary and file details, then proceed further.
         """
        """ TODO: Check if files already exist - and delete them if yes !!! """
        """ TODO: Make a dialog or choice in which directory to save !!!"""
        """ these are to account for measurement repeat cycles"""

        if self.start_button.text() == 'Start':
            self.start_button.setText('Stop')
            self.ARPES_table.setEnabled(False)

            self.positions_counter = 1  # global counter for positions
            self.repeat_counter = 1     # global repeat counter

            """ Read all spectra parameters from the first row of the table and make a dictionary out of them """
            """ TODO: Accept more than one row in ARPES table !!!"""
            self.values = [self.ARPES_table.item(0, int(col)).text() for col in range(self.ARPES_table.columnCount())]
            self.spectra_dictionary_original = dict(zip(self.ARPES_col_headers, self.values))
            self.spectra_dictionary_original[' Lens_mode '] = self.combo_box_lens.currentText()

            # """Make a dictionary with file name and repeat cycles"""
            # self.file_settings_dict = {key: self.spectra_dictionary_original[key] for key in
            #                            self.ARPES_col_headers[0:2]}
            #
            # """Make a dictionary with analyser settings only"""
            # self.analyser_settings_dict = {key: self.spectra_dictionary_original[key] for key in
            #                                self.ARPES_col_headers[2:12]}

            """ Make carving positions list for each point to measure: the arrays of positions for each axis. 
            Number of points in each axis is either 1 or consistent in other axes maximum number.
            TODO: include option to set up multi-axis-map measurement"""
            self.axis_range = 0
            self.carving_positions_dict = {}
            for key in self.ARPES_col_headers[12:]:
                if ":" in str(self.spectra_dictionary_original[key]):
                    v = str(self.spectra_dictionary_original[key]).split(":")
                    self.carving_positions_dict[key] = np.linspace(float(v[0]), float(v[1]), int(v[2]))
                    self.axis_range = len(self.carving_positions_dict[key])
                else:
                    self.carving_positions_dict[key] = np.linspace(float(self.spectra_dictionary_original[key]),
                                                                   float(self.spectra_dictionary_original[key]),
                                                                   1)
            print("max number of points for 1 axis: ", self.axis_range)
            if self.axis_range > 0:
                for key in self.carving_positions_dict.keys():
                    print (self.carving_positions_dict[key])
                    if len(self.carving_positions_dict[key]) == 1:
                        self.carving_positions_dict[key] = np.linspace(
                            self.carving_positions_dict[key][0],
                            self.carving_positions_dict[key][0],
                            int(self.axis_range)
                        )

            """ Read K-dope parameters from the table and make a dictionary out of them """
            self.values = [self.K_table.item(0, int(col)).text() for col in range(self.K_table.columnCount())]
            self.k_dictionary = dict(zip(self.K_col_headers, self.values))

            """ Set up k-doping manipulator move """
            if self.k_radiobutton.isChecked():
                "TODO: add functionality!"
                pass

            print("Spectra dictionary ORIGINAL: ", self.spectra_dictionary_original)
            print("Carving positions: ", self.carving_positions_dict)
            self.main_start_measure_spectra()

        else:
            self.start_button.setText('Start')
            self.ARPES_table.setEnabled(True)
            self.main_stop_measurement()

    def main_start_measure_spectra(self):
        """ Move manipulator to the measurement position and proceed with analyser settings """
        """ Set up analyser settings"""
        self.set_analyser_check = self.MyProdigy.set_analyzer_parameters(self.spectra_dictionary_original)
        """ Set up spectrum settings"""
        if self.set_analyser_check:
            self.set_spectrum_check = self.MyProdigy.define_spectra(self.spectra_dictionary_original)
            if self.set_spectrum_check:
                print ("Analyser and Spectra set up SUCCESSFUL")
                """Set up manipulator to the starting position and proceed further with spectra validation and 
                measurement """
                self.first_position = {key:self.carving_positions_dict[key][0] for key in
                                       self.carving_positions_dict.keys()}
                self.MyCarving.move_carving(self.first_position)

    def check_what_to_do_next(self):
        if self.repeat_counter <= int(self.spectra_dictionary_original['Repeat']):
            "repeat measurement"
            self.repeat_counter += 1
            self.MyProdigy.start_measurement(self.spectra_dictionary_original,self.carving_positions_dict)
        else:
            'move to the next carving position'
            self.repeat_counter = 1
            self.positions_counter += 1
            "check if all manipulator positions were measured"
            if self.positions_counter <= self.axis_range:
                self.next_position = {key:self.carving_positions_dict[key][self.positions_counter-1] for key in
                                       self.carving_positions_dict.keys()}
                self.MyCarving.move_carving(self.next_position)
            else:
                self.main_stop_measurement()
            pass

    def move_to_evaporation(self):

        if self.k_counter < int(self.k_dictionary.get("Repeat N")):
            """ Move to evap. position and make quick fake spectra,
            start evaporation and after finished - start photoemission measurement"""
            print("moving to evaporation position")
            self.k_wait_flag = True
            self.MyProdigy.position_carving(self.spectra_dictionary_original, self.spectra_dictionary_K, self.fake_flag,
                                            self.carving_positions_dict, self.repeat_counter)
            " wait until move is finished "
        else:
            print("K-dose experiment ACHIEVED")
            self.main_stop_measurement()
            pass

    def start_evaporation(self):
        "evaporate potassium"
        self.k_counter += 1
        # self.Doping.start(self.k_dictionary)

    def evaporation_end(self):
        self.k_wait_flag = False
        self.main_start_measure_spectra()

    def main_end_measurement(self):
        """ after each measured spectra self.fake_flag must change if k-dope is active """
        if self.k_radiobutton.isChecked() and self.repeat_counter >= int(
                self.spectra_dictionary_original.get("Repeat")):
            self.fake_flag = not (self.fake_flag)
            print("Fake flag state at the end of measurement: ", self.fake_flag)

        if self.k_radiobutton.isChecked() and self.fake_flag:
            self.move_to_evaporation()
        else:
            if not self.k_wait_flag:
                if self.repeat_counter >= int(self.spectra_dictionary_original.get("Repeat")):
                    self.steps_counter += 1
                    self.repeat_counter = 1
                    if (self.steps_counter >= self.dimension_steps):
                        self.main_stop_measurement()
                    else:
                        self.main_start_measure_spectra()
                else:
                    self.repeat_counter += 1
                    self.main_start_measure_spectra()
            else:
                self.can_evaporate_trigger.emit()

    def main_stop_measurement(self):
        self.start_button.setText('Start')
        self.ARPES_table.setEnabled(True)

        try:
            self.MyProdigy.communicate('Abort')
        except Exception as e:
            print (e)
            pass

    def closeEvent(self, event):
        self.MyProdigy.prodigy_disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)  # A new instance of QApplication
    MainWindow = Window()  # We set the form to be our ExampleApp (design)
    MainWindow.setWindowTitle("EP4 Lab Photoemission Experiment GUI")
    MainWindow.resize(1250, 275)
    MainWindow.show()  # Show the form
    sys.exit(app.exec_())


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
