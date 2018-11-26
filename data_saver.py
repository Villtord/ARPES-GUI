# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 14:14:56 2018

@author: ARPES
"""
""" dimension_info comes in a form of list of dictionaries of empty [{"Axis":"None","3D_min":0,"3D_delta":1,"Steps":1}, ]"""
def save_slice(spectra_dictionary_original, data_numpy, dimension_info, repeat_counter):
       
    import numpy as np
    import h5py
    from time import gmtime, strftime
    from pathlib import Path
    

    """ Resize data to a 2D array according to NE channels """        
    
    print ("SAVING DATA!!!")
    try:
        raws = int (spectra_dictionary_original.get(" Channels: NE "))
        columns = int (np.size(data_numpy)/raws)
        print ("raw data size: ", np.size(data_numpy))
        print ("data size: ", raws," ", columns)
        data_numpy = data_numpy.reshape((raws,columns))
    except:
        print ("error while reshaping 1D data to a 2D ")
        pass
    
    fileNameHDF5 = spectra_dictionary_original.get(" Name ")+".hdf5"
    fileNameHDF5_path = Path(fileNameHDF5)
    
    """ Check if file already exist"""       
    if fileNameHDF5_path.is_file():
        
        """ Resize dataset (increase 3rd dimension to +1) and add new 2D data """
        f = h5py.File(fileNameHDF5, "r+")
        data_set = f["Data"]
        if repeat_counter == 1:
            new_shape = data_set.shape[:-1]+(data_set.shape[-1]+1,)
            data_set.resize(new_shape)
            data_set[:,:,new_shape[-1]-1]=data_numpy
        else:
            if len(data_set.shape) == 2:
                data_set[:,:]+=data_numpy
            else:
                data_set[:,:,-1]+=data_numpy
        f.close()
 
        """ If file does not exist- make it """
    else:
 
        f = h5py.File(fileNameHDF5, "w")
        
        timestamp=strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        f.attrs['default']          = 'entry'
        f.attrs['file_name']        = fileNameHDF5
        f.attrs['file_time']        = timestamp
        f.attrs['instrument']       = 'SPECS Prodigy'
        f.attrs['HDF5_Version']     = h5py.version.hdf5_version
        f.attrs['h5py_version']     = h5py.version.version
           
        
        """ Here make variable-length dataset and write data to a HDF5 file """
        if (dimension_info.get("Axis") == []):
            ds = f.create_dataset ("Data",data=data_numpy, dtype = 'Float64')
        else:
            ds = f.create_dataset ("Data", shape=(raws, columns, 1), maxshape=(raws,columns,None),dtype = 'Float64')
            ds[:,:,0] = data_numpy
        
#            f.swmr_mode = True           
        Wave_Note=[""]
        for i,j in spectra_dictionary_original.items():
            print (i, " = ",j)
            Wave_Note[0] += str(i)+" = "+str(j)+", \n"
#        print (Wave_Note)
        
        Wave_Note_ascii = [n.encode("ascii", "ignore") for n in Wave_Note]
        
        ds.attrs['IGORWaveNote'] = Wave_Note_ascii
        
        if "WideAngleMode" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 14.59*2
        elif "LowAngleMode" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 7*2
        elif "HighMagnification" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 1
        elif "MeduimMagnification" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 1
        elif "LowMagnification" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 1
        elif "MediumArea" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 1
        elif "SmallArea" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 1
        elif "LargeArea" in spectra_dictionary_original.get(" Lens_mode "):
            wide_angle = 1
        
        if (dimension_info.get("Axis") != []):
            z_min = float(dimension_info.get("3D_min")[0])
            z_delta = float (dimension_info.get("3D_delta")[0])
            
        """ Calculate scaling parameteres for plot axis """
#        
#        if (float(spectra_dictionary_original.get(" Step (FAT),eV ")) >= 0.001) and (float(spectra_dictionary_original.get(" Step (FAT),eV ")) <= 10.0):
                
#        print ('This is FAT spectrum!')
        if (dimension_info.get("Axis") != []):
            ds.attrs['IGORWaveScaling'] = [[0,0],
                     [float(wide_angle/int(spectra_dictionary_original.get(" Channels: NE "))),-wide_angle/2],
                     [float(spectra_dictionary_original.get(" Step (FAT),eV ")),float(spectra_dictionary_original.get(" KE_start,eV "))],
                     [z_delta,z_min]]
        else:
            ds.attrs['IGORWaveScaling'] = [[0,0],
                     [float(wide_angle/int(spectra_dictionary_original.get(" Channels: NE "))),-wide_angle/2],
                     [float(spectra_dictionary_original.get(" Step (FAT),eV ")),float(spectra_dictionary_original.get(" KE_start,eV "))]]


        f.close()