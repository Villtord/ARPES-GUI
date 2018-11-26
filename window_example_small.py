# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 15:33:05 2018

@author: Victor Rogalev

02 October: vectors in more than one parameters:X,Y,Z,Theta... added
26 October: save/load options for experiment added

"""
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidget, QApplication, QMainWindow, QTableWidgetItem, QComboBox, QFileDialog
from communication_example import connection_object
from new_k_evaporation import anneal_object
import pickle

class MyTable (QTableWidget):
    def __init__(self,r,c):
        super(self.__class__, self).__init__(r,c)
        self.setup_ui()
    
    def setup_ui(self):
        self.cellChanged.connect(self.current_cell)
    
    def current_cell(self):
        row = self.currentRow()
        col = self.currentColumn()
        value = self.item(row,col)
        value = value.text()
        print(type(value))
        if "," in value:            
            print ("replacing: ", value.replace(",","."))
            value_new = QTableWidgetItem(value.replace(",","."))
            self.setCurrentCell(row,col)
            self.setItem(row,col,value_new)
        print ("value: ",value," in cell: ", row,col)
        
class Window (QtWidgets.QWidget):    
    
    can_evaporate_trigger=pyqtSignal()
    
    def __init__(self):
        
        super(self.__class__, self).__init__()
        
        self.MyProdigy = connection_object()
        self.KEvaporation = anneal_object()
        
        try:
            self.MyProdigy.prodigy_connect()
        except:
            print('did not connect')
            pass
        
        """ Create photoemission table """        
        self.ARPES_table = MyTable(1,18)
        self.ARPES_col_headers = [' Name ','Repeat',' KE_start,eV ',' KE_end,eV ',' Step (FAT),eV ',
                       ' Samples (SFAT) ',' E_pass,eV ',' Lens_mode ',
                       ' Channels: E ',' Channels: NE ',' Dwell,s ',' U_det,V ',
                       ' X ',' Y ',' Z ',' Tilt ',' Polar ',' Azimuth ']
        
        header_ARPES_table = self.ARPES_table.horizontalHeader()
        header_ARPES_table.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        
        for i in range(1,self.ARPES_table.columnCount()):
            header_ARPES_table.setSectionResizeMode(int(i),QtWidgets.QHeaderView.ResizeToContents)
        
        """ Set up default photoemission spectrum """
        self.default_spectrum = ['Default','1', '16.0','17.0','0',
                                 '1','10.0','WideAngleMode',
                                 '100','500','1','1450',
                                 '12','-8','202','0','-130','0']
        
        for i in range(len(self.default_spectrum)):
            number = QTableWidgetItem(self.default_spectrum[i])
            self.ARPES_table.setCurrentCell(0,i)
            self.ARPES_table.setItem(0,i,number)
        
        self.ARPES_table.setHorizontalHeaderLabels(self.ARPES_col_headers)
        
        self.combo_box_lens = QComboBox()
        self.lens_modes_options = ["WideAngleMode","LowAngleMode","HighMagnification", "MediumMagnification", "MeduimArea"]
        for t in self.lens_modes_options:
            self.combo_box_lens.addItem(t)
        self.ARPES_table.setCellWidget(0,7,self.combo_box_lens)
        
        
        """ Create K-dose table """
        self.K_table = MyTable(1,16)
        self.K_col_headers = ['Repeat N',
                       'Ramp to,A 1','Ramp time,s 1','Hold time,s 1',
                       'Ramp to,A 2','Ramp time,s 2','Hold time,s 2',
                       'Ramp to,A 3','Ramp time,s 3','Hold time,s 3',
                       ' X ',' Y ',' Z ',' Tilt ',' Polar ', ' Azimuth ']
        
        self.K_table.setHorizontalHeaderLabels(self.K_col_headers)
        header_K_table = self.K_table.horizontalHeader()
        for i in range(self.K_table.columnCount()):
            header_K_table.setSectionResizeMode(int(i),QtWidgets.QHeaderView.Stretch)
        
        for i in range(10,self.K_table.columnCount()):
            header_K_table.setSectionResizeMode(int(i),QtWidgets.QHeaderView.ResizeToContents)
        
        
        """ Set up default K-dose recipee """
        self.default_spectrum = ['1',
                                 '0.1','1','5',
                                 '1.0','5','5',
                                 '2.0','5','10',
                                 '0.0','0.0','0.0','0.0','0.0','90']
        for i in range(len(self.default_spectrum)):
            number = QTableWidgetItem(self.default_spectrum[i])
            self.K_table.setCurrentCell(0,i)
            self.K_table.setItem(0,i,number)
        
        """ GUI Layout """
        self.K_table.setMaximumHeight(55)
        self.h_layout_1 = QtWidgets.QHBoxLayout()
        self.k_radiobutton = QtWidgets.QRadioButton('Use K-dope')
        self.load_button = QtWidgets.QPushButton ('Load')
        self.save_button = QtWidgets.QPushButton ('Save')
        self.h_layout_1.addWidget(self.k_radiobutton)
        self.h_layout_1.addStretch()
        self.h_layout_1.addWidget(self.save_button)
        self.h_layout_1.addWidget(self.load_button)
        
        self.h_layout_2 = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton('Start')
        self.ksave_button = QtWidgets.QPushButton('Save')
        self.kload_button = QtWidgets.QPushButton ('Load')
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
        self.k_radiobutton.clicked.connect(self.disable_k_table)
        
        self.start_button.clicked.connect(self.start)  
        self.can_evaporate_trigger.connect(self.start_evaporation)        
        "measure spectra when evaporation is done"
        self.KEvaporation.evaporation_end_trigger.connect(self.evaporation_end)
        self.MyProdigy.communication_end_trigger.connect(self.main_end_measurement)
        
        self.save_button.clicked.connect(self.save_file)
        self.load_button.clicked.connect(self.load_file)
        
        self.show()
    
    def load_file(self):
        """ read values from saved file to a dictionary and then load it to GUI """
        load_file_name = QFileDialog.getOpenFileName(self, 'Open file', '','*.pkl')
        
        with open(load_file_name[0], 'rb') as f:
            self.loaded_settings_ARPES = pickle.load(f)
            self.loaded_settings_K = pickle.load(f)
            
        
        f.close()
#        print(self.loaded_settings)
        for col in range(self.ARPES_table.columnCount()):
            number = QTableWidgetItem(self.loaded_settings_ARPES[self.ARPES_col_headers[col]])
            self.ARPES_table.setCurrentCell(0,int(col))
            self.ARPES_table.setItem(0,int(col),number)
            
        for col in range(self.K_table.columnCount()):
            number = QTableWidgetItem(self.loaded_settings_K[self.K_col_headers[col]])
            self.K_table.setCurrentCell(0,int(col))
            self.K_table.setItem(0,int(col),number)
        
        self.combo_box_lens.setCurrentText(self.loaded_settings_ARPES[' Lens_mode '])
        self.k_radiobutton.setChecked(self.loaded_settings_ARPES[' K_radiobutton '])

        
    def save_file(self):
        """ write values from table to a dictionary and then save it to a .pkl file """
        self.save_string={}
        
        """ Read spectra parameters from the table """
        self.ARPES_values = [self.ARPES_table.item(0,int(col)).text() for col in range(self.ARPES_table.columnCount())]
        
        """ Read K-dope parameters from the table and add them to spectra parameters list"""
        self.K_values = [self.K_table.item(0,int(col)).text() for col in range(self.K_table.columnCount())]
      
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
        self.fake_flag = False
        self.k_wait_flag = False
        self.dimension_info = {"Axis":[],"3D_min":[],"3D_delta":[],"Steps":[]}
        self.k_counter=0
        self.steps_counter=0
        self.dimension_steps=1
        
        """ these are to account for measurement repeat cycles"""
        self.repeat_counter = 1
        
        """ Check if files already exist - and delete them if yes !!! """
        """ Make a dialog or choice in which directory to save !!!"""
        
        if self.start_button.text() =='Start':
            self.start_button.setText('Stop')
            self.ARPES_table.setEnabled(False)
            
            """ Read spectra parameters from the table and make a dictionary out of them """
            self.values = [self.ARPES_table.item(0,int(col)).text() for col in range(self.ARPES_table.columnCount())]
            self.spectra_dictionary_original = dict(zip(self.ARPES_col_headers, self.values))
            
            self.spectra_dictionary_original[' Lens_mode '] = self.combo_box_lens.currentText()
            
            """ Read K-dope parameters from the table and make a dictionary out of them """
            self.values = [self.K_table.item(0,int(col)).text() for col in range(self.K_table.columnCount())]
            self.k_dictionary = dict(zip(self.K_col_headers, self.values))
            
            """ Check if the data that one needs to measure are 3D data: make self.dimension_info in a
            form of a dictionary with list of arguments self.dimension_info == {"Axis":["X"],"3D_min":[0],"3D_delta":[1],"Steps":[1]}
            3D data in a table must be in a form: X_start:X_delta:X_end """
      
            for i,j in self.spectra_dictionary_original.items():
                key = str(i)
                value = str(j)
                if ":" in value:
                    values_list = value.split(":")
                    steps = int((float(values_list[2])-float(values_list[0]))/float(values_list[1])+1)
                    self.dimension_info["Axis"].append(key)
                    self.dimension_info["3D_min"].append(values_list[0])
                    self.dimension_info["3D_delta"].append(values_list[1])
                    self.dimension_info["Steps"].append(steps)
#                    self.dimension_info["Axis"].append({"Axis":key,"3D_min":values_list[0],"3D_delta":values_list[1],"Steps":steps})
            
            """ Set up quicker spectra for k-doping manipulator move - fake spectra """
            if self.k_radiobutton.isChecked():
                
#                self.dimension_info.append({"Axis":"K-dose","3D_min":0,"3D_delta":1,"Steps":self.k_dictionary.get("Repeat N")})
                self.dimension_info["Axis"].append("K-dose")
                self.dimension_info["3D_min"].append(0)
                self.dimension_info["3D_delta"].append(1)
                self.dimension_info["Steps"].append(self.k_dictionary.get("Repeat N"))
                
                self.spectra_dictionary_K = self.spectra_dictionary_original.copy()
                
                for i in [' X ',' Y ',' Z ',' Tilt ',' Polar ', ' Azimuth ']:
                    self.spectra_dictionary_K[i]=self.k_dictionary[i]
                
                if (float(self.spectra_dictionary_original.get(" Step (FAT),eV ")) >= 0.001) and (float(self.spectra_dictionary_original.get(" Step (FAT),eV ")) <= 10.0):
                    self.spectra_dictionary_K[' Step (FAT),eV '] = float(self.spectra_dictionary_original.get(' KE_end,eV '))-\
                    float(self.spectra_dictionary_original.get(' KE_start,eV '))
                
                if (int(self.spectra_dictionary_original.get(" Samples (SFAT) ")) >= 1) and (int(self.spectra_dictionary_original.get(" Samples (SFAT) ")) <= 10000):
                    self.spectra_dictionary_K[' Dwell,s '] = 0
                
                print (" Spectra dictionary for K-dose: ", self.spectra_dictionary_K)
            
            print (" Spectra dictionary ORIGINAL: ", self.spectra_dictionary_original)
            print ("3D dimension: ", self.dimension_info)
            self.main_measure_spectra()
        
        else:
            self.start_button.setText('Start')
            self.ARPES_table.setEnabled(True)
            self.main_stop_measurement()
        

    def main_measure_spectra(self):
        print ("prepare to measure spectra")
        self.spectra_dictionary = self.spectra_dictionary_original.copy()
        
        """ Check if the data that one needs to measure are 3D data: positions vector or K-dope active """
        try:
            self.dimension_steps = int(self.dimension_info.get("Steps")[0])
        except:
            self.dimension_steps = 0
            pass
        
        if (self.dimension_steps > 0) and not self.k_radiobutton.isChecked():
            """ Set up one of the 3D data measurements steps """
            for i in range(len(self.dimension_info["Axis"])):
                try:
                    self.spectra_dictionary[self.dimension_info.get("Axis")[i]]=\
                    self.steps_counter*float(self.dimension_info.get("3D_delta")[i])+float(self.dimension_info.get("3D_min")[i])
                except:
                    print ("error setting up spectra dictionary from 3D info")
                    pass        
            print ("set up one spectra: ", self.spectra_dictionary)
        
        """ Set up manipulator positon and proceed further with spectra validation and mesurement """        
        self.MyProdigy.position_carving(self.spectra_dictionary_original, self.spectra_dictionary, self.fake_flag, self.dimension_info, self.repeat_counter)

    def move_to_evaporation(self):
                 
        if self.k_counter < int(self.k_dictionary.get("Repeat N")):
            """ Move to evap. position and make quick fake spectra,
            start evaporation and after finished - start photoemission measurement"""
            print ("moving to evaporation position")
            self.k_wait_flag = True
            self.MyProdigy.position_carving(self.spectra_dictionary_original, self.spectra_dictionary_K, self.fake_flag, self.dimension_info, self.repeat_counter)
            " wait until move is finished "
        else:
            print ("K-dose experiment ACHIEVED")
            self.main_stop_measurement()
            pass
        
    def start_evaporation(self):
        "evaporate potassium"
        self.k_counter +=1
        self.KEvaporation.start(self.k_dictionary)
    
    def evaporation_end(self):
        self.k_wait_flag = False
        self.main_measure_spectra()    
        
    def main_end_measurement(self):
        """ after each measured spectra self.fake_flag must change if k-dope is active """
        if self.k_radiobutton.isChecked() and self.repeat_counter >= int(self.spectra_dictionary_original.get("Repeat")):
            self.fake_flag = not(self.fake_flag)
            print ("Fake flag state at the end of measurement: ", self.fake_flag)
        
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
                        self.main_measure_spectra()
                else:
                    self.repeat_counter +=1
                    self.main_measure_spectra()
            else:
                self.can_evaporate_trigger.emit()
                   
    def main_stop_measurement(self):        
        self.start_button.setText('Start')
        self.ARPES_table.setEnabled(True)
        
        try:
            self.MyProdigy.communicate('Abort')
        except:
            pass
        
#        try:
#            self.MyProdigy.communicate('SetSafeState')
#        except:
#            pass
        
        try:
            self.KEvaporation.stop()
        except:
            pass
    
    def closeEvent(self, event):
        self.MyProdigy.prodigy_disconnect()
        event.accept()


    
def main():
    app = QApplication(sys.argv)  # A new instance of QApplication
    MainWindow = Window()               # We set the form to be our ExampleApp (design)
    MainWindow.setWindowTitle("EP4 Lab Photoemission Experiment GUI")
    MainWindow.resize (1250,275)
    MainWindow.show()                         # Show the form
    sys.exit(app.exec_())

if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                              # run the main function