# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 09:19:25 2022

@author: Jostein Steffensen
Purpose: GUI for reading csv results from filtermatching_NPS.py. GUI displays best filtermatch to chosen scanner, reconstruction
and filter. Images from both chosen filter and best match can be displayed. 
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import PySimpleGUI as sg
import pydicom
import glob
import numpy as np
import time 

#HEAD EXAMINATION
scanner_h = ['Siemens AS+', 'Siemens Flash', 'Canon Prime']

#Head reconstructions
rec_h_siemens_as = ['FBP', 'IR1', 'IR2', 'IR4']
rec_h_siemens_flash = ['FBP', 'IR1', 'IR2']
rec_h_canon = ['ORG', 'AIDR 3D STD', 'AIDR 3D eSTD']

#Head filters
filter_FBP_siemens = ['H10s', 'H20s', 'H30s', 'H37s', 'H40s', 'H50s', 'H60s', 'H70h']
filter_IR_siemens = ['J30s', 'J37s', 'J40s', 'J45s', 'J49s', 'J70h', 'Q30s', 'Q33s']
filter_canon = ['FC20', 'FC21', 'FC22', 'FC23', 'FC24', 'FC25', 'FC26']

#BODY EXAMINATION
scanner_b = ['Siemens AS+', 'Siemens Flash', 'Canon Prime', 'GE revolution']

#Body reconstruction
rec_b_siemens = ['FBP', 'IR1', 'IR2']
rec_b_canon = ['ORG', 'AIDR 3D STD', 'AIDR 3D STR', 'AIDR 3D eSTD', 'UE0', 'AIDR 3D STD-UE0', 'AIDR 3D STR-UE0', 'AIDR 3D eSTD-UE0']
rec_b_GE = ['FBP','ASIR_50','TF High','TF High med lungefilter','TF Low med lungefilter']

#Body filters
filter_GE = ['BONE', 'BONEPLUS', 'CHEST', 'DETAIL', 'EDGE', 'LUNG', 'SOFT', 'STANDARD', 'ULTRA']
filter_b_FBP_siemens_AS = ['B10f', 'B26f', 'B30f', 'B31f', 'B40f', 'B50f', 'B70f']
filter_b_IR_siemens_AS = ['I26f', 'I30f', 'I31f', 'I40f', 'I50f', 'I70f']
filter_b_FBP_siemens_flash = ['B10f', 'B26f', 'B30f', 'B31f', 'B40f', 'B45f', 'B50f', 'B70f', 'D33f']
filter_b_IR_siemens_flash = ['I26f', 'I30f', 'I31f', 'I40f', 'I50f', 'I70f', 'Q33f']
filter_b_canon = ['FC08','FC18','FC26','FC43','FC51','FC52']
filter_b_canon_FC51 = ['FC51']
filter_b_GE = ['BONE','BONEPLUS','CHEST','DETAIL','EDGE','LUNG','SOFT','STANDARD','ULTRA']
filter_b_GE_std = ['STANDARD']

##############################################
#Layout
##############################################
layout = [
    #head or body
    [sg.Text("Choose examination: ")],
    [sg.Combo(["Head", "Body"], enable_events=True, key = 'examination', size=(15,0))],
    #scanners
    [sg.Text("Choose scanner: "), sg.Push(), sg.Text("Choose scanner to match:"), sg.Push()], 
    [sg.Combo([], enable_events = True, key='scanner', size=(15,0)), sg.Push(), sg.Combo([], enable_events = True, key='scanner2', size=(15,0)), sg.Push()],
    #reconstructions
    [sg.Text("Choose reconstruction: ")],
    [sg.Combo([], enable_events = True, key='rec_type', size = (20,0))],
    #All filters available
    [sg.Text("Choose filter: "), sg.Push(), sg.Text('', key = '-OUTPUT-', font = ("Arial", 15)), sg.Push()], 
    [sg.Combo([], key='filter_type', size=(20,0))],
    #Show image
    [sg.Button('Test image', key='-IMAGE-', disabled = True, size = (15,2)), sg.Push(), 
     sg.Button('Test image 2', key='-IMAGE2-', disabled = True, size = (15,2)), sg.Push()],
    [sg.Button('Find best filter match', key='-FILTERMATCH-', disabled = True, size=(15,2))]
    
]

window = sg.Window('CT filtermatching', layout, size=(500, 350)).Finalize()


##############################################
#Image functions
##############################################
def sortImages(pathname):
    '''Function from Vilde
    Sort images in same directory'''
    sortDict = {}
    for path in glob.glob(pathname):
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        sortDict[ds.SliceLocation] = path
        mpl.rc('figure', max_open_warning = 0)
    sortedKeys = sorted(sortDict.keys())
    return sortDict, sortedKeys 

#Scroll through images
def image_scroll(scanner_name, filter_name, reconstruction):
    #this function is inspired by https://matplotlib.org/stable/gallery/event_handling/image_slices_viewer.html     
    image_path = f"../CT bilder av Catphan/{values['examination']}/{scanner_name}/{reconstruction}/{filter_name}/*" #220623 JBS Changed from *.dcm to * to include other image formats. 
    
    try:
        sortDict, sortedKeys = sortImages(image_path) #Sort images
    except:
        print(f'File for {scanner_name}, {reconstruction} and {filter_name} is missing.')
        return
   
    try:
        dataset = pydicom.dcmread(sortDict[sortedKeys[0]])
    except:
        print(f"File for {values['examination']}, {scanner_name}, {reconstruction} and {filter_name} is missing.")
        return
    
    image = dataset.pixel_array * dataset.RescaleSlope + dataset.RescaleIntercept
    
    #dimentions of image cube
    z_dimention = len(sortedKeys)
    x_dimention = image.shape[0]
    y_dimention = image.shape[1]
    
    #Collecting all dcm files from same series in the same numpy cube
    image_cube = np.empty([x_dimention, y_dimention, z_dimention])
    i = 0
    for key in sortedKeys:
        dataset = pydicom.dcmread(sortDict[key])
        image = dataset.pixel_array * dataset.RescaleSlope + dataset.RescaleIntercept
        image_cube[:,:,i] = image
        i += 1
        
    class IndexTracker:
        def __init__(self, ax, X):
            self.ax = ax
            ax.set_title('use scroll wheel to navigate images')

            self.X = X
            rows, cols, self.slices = X.shape
            self.ind = self.slices//2
            plt.gcf().set_facecolor("black")
            self.im = ax.imshow(self.X[:, :, self.ind], cmap='Greys_r', vmin=-100, vmax=200)
            self.update()

        def on_scroll(self, event):
            if event.button == 'up':
                self.ind = (self.ind + 1) % self.slices
            else:
                self.ind = (self.ind - 1) % self.slices
            self.update()

        def update(self):
            self.im.set_data(self.X[:, :, self.ind])
            self.ax.set_ylabel('slice %s' % self.ind)
            self.im.axes.figure.canvas.draw()

    fig, ax = plt.subplots(1, 1)
    X = image_cube
    tracker = IndexTracker(ax, X)
    
    return fig, ax, tracker
    
##############################################
#Find best filtermatch
##############################################
def find_best_match(scanner1, scanner2):
    file_path = f'../Results AVG/{values["examination"]}/Matching {scanner1} all/With {scanner2} all/'
    
    #Opening csv file from filtermatching_NPS.py
    df = pd.read_csv(f'{file_path}Matching table {scanner1}all-{scanner2}all.csv', sep=';',header=None)
    
    #merging rec and filter
    rec_filter = f"{values['rec_type']} {values['filter_type']}"
    
    index=0
    for element in df.values[:,1]:
        if element == rec_filter:
            return df.values[index,2]
        index+=1
    return 0
###############################################################################
###############################################################################
###############################################################################
###############################################################################    
###############################################################################
# GUI action
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################    
while True:
    event, values = window.read()
    
    ##############################################################
    #Update GUI
    ##############################################################
    
    #examination choice
    if event == 'examination':
        
        #Available scanners for head examinations
        if values[event] == 'Head':
            window['scanner'].update(value='', values=scanner_h)
            window['scanner2'].update(value='', values=scanner_h)
            
        #Available scanners for body examinations
        elif values[event] == 'Body':
            window['scanner'].update(value='', values=scanner_b)
            window['scanner2'].update(value='', values=scanner_b)  
            
        window['-IMAGE-'].update(disabled = True)
        window['-FILTERMATCH-'].update(disabled = True)
    
    
    #Scanner choice 
    if event == 'scanner':
        
        if values['examination']=='Head':
            
            #available reconstructions for Siemens AS+ head examinations
            if values[event] == 'Siemens AS+':
                rec_liste = rec_h_siemens_as
                window['rec_type'].update(value = '', values = rec_liste)
                window['filter_type'].update(value = '', values = [])
             
            #available reconstructions for Siemens Flash head examinations
            elif values[event] == 'Siemens Flash':
                rec_list = rec_h_siemens_flash
                window['rec_type'].update(value = '', values = rec_list)
                window['filter_type'].update(value ='', values = [])
                
            #available reconstructions for Canon Prime head examinations
            elif values[event] == 'Canon Prime':
                rec_liste = rec_h_canon
                window['rec_type'].update(value = '', values = rec_liste)
                window['filter_type'].update(value ='', values = [])  
        
        
        elif values['examination']=='Body':
            
            #available reconstructions for Siemens AS+ body examinations
            if values[event] == 'Siemens AS+':
                rec_liste = rec_b_siemens
                window['rec_type'].update(value = '', values = rec_liste)
                window['filter_type'].update(value = '', values = [])
                
            #available reconstructions for Siemens Flash body examinations
            elif values[event] == 'Siemens Flash':
                rec_list = rec_b_siemens
                window['rec_type'].update(value = '', values = rec_list)
                window['filter_type'].update(value ='', values = [])
                
            #available reconstructions for Canon Prime body examinations     
            elif values[event] == 'Canon Prime':
                rec_list = rec_b_canon
                window['rec_type'].update(value = '', values = rec_list)
                window['filter_type'].update(value ='', values = [])
                
            #available reconstructions for GE revolution body examinations    
            elif values[event] == 'GE revolution':
                rec_list = rec_b_GE
                window['rec_type'].update(value = '', values = rec_list)
                window['filter_type'].update(value ='', values = [])              
                
        window['-IMAGE-'].update(disabled = True)
        window['-FILTERMATCH-'].update(disabled = True) 
    
        
    #Reconstruction choice 
    if event == 'rec_type':
        
        if values['examination']=='Head':
            
            #Available filters for Siemens head examinations
            if (values['scanner']=='Siemens AS+' or values['scanner']=='Siemens Flash'):
                
                if values[event] == 'FBP':
                    filter_list = filter_FBP_siemens
                    window['filter_type'].update(value = filter_list[0], values = filter_list)
                else:
                    filter_list = filter_IR_siemens
                    window['filter_type'].update(value = filter_list[0], values = filter_list)   
                    
            #Available filters for Canon Prime head examinations        
            elif values['scanner']=='Canon Prime':
                filter_list = filter_canon
                window['filter_type'].update(value = filter_list[0], values = filter_list)
       
        elif values['examination']=='Body':
            
            #Available filters for Siemens AS+ body examinations
            if values['scanner']=='Siemens AS+':
                
                if values[event] == 'FBP':
                    filter_list = filter_b_FBP_siemens_AS
                    window['filter_type'].update(value = filter_list[0], values = filter_list)
                else:
                    filter_list = filter_b_IR_siemens_AS
                    window['filter_type'].update(value = filter_list[0], values = filter_list)
            
            #Available filters for Siemens Flash body examinations
            if values['scanner']=='Siemens Flash':
                
                if values[event] == 'FBP':
                    filter_list = filter_b_FBP_siemens_flash
                    window['filter_type'].update(value = filter_list[0], values = filter_list)    
                else:
                    filter_list = filter_b_IR_siemens_flash
                    window['filter_type'].update(value = filter_list[0], values = filter_list)
            
            #Available filters for Canon Prime body examinations
            elif values['scanner']=='Canon Prime':
                
                if values[event] == 'ORG' or values[event] == 'AIDR 3D STD' or values[event] == 'AIDR 3D STR' or values[event] == 'AIDR 3D eSTD': 
                    filter_list = filter_b_canon
                else:
                    filter_list = filter_b_canon_FC51
                    
                window['filter_type'].update(value = filter_list[0], values = filter_list)
             
            #available filters for GE revolution body examinations
            elif values['scanner']=='GE revolution':
                
                if values[event] == 'TF High' or values[event] == 'TF High med lungefilter' or values[event] == 'TF Low med lungefilter': 
                    filter_list = filter_b_GE_std
                else:
                    filter_list = filter_b_GE
                    
                window['filter_type'].update(value = filter_list[0], values = filter_list)
            
        #Enables button if rec and filter is choosen.
        window['-IMAGE-'].update(disabled = False)
            
        #Check if matching scanner is chosen before making button available. 
        if values['scanner2'] != '':
            window['-FILTERMATCH-'].update(disabled = False)
    
        
    #Update button for filtermatching when matching scanner is chosen.
    if event == 'scanner2':
        if values['filter_type'] != '':
            window['-FILTERMATCH-'].update(disabled = False)
        else:
            window['-FILTERMATCH-'].update(disabled = True)
            
        window['-IMAGE2-'].update(disabled = True)
    
    ##############################################################
    #FILTER MATCHING
    ############################################################## 
    if event == '-FILTERMATCH-':
        
        #Make sure the scanner is set to match itself. 
        if values['scanner'] != values['scanner2']:
            #Finds best match between scanner 1 and scanner 2
            best_rec_filter = find_best_match(values['scanner'], values['scanner2'])
            
            #Update output and enables IMAGE 2 button. 
            window['-OUTPUT-'].update(best_rec_filter)  
            window['-IMAGE2-'].update(disabled = False) #enables test image for matching scanner
        else:
            window['-OUTPUT-'].update('Pick different scanner.')
              
    ##############################################################
    #IMAGES
    ##############################################################
    
    #IMAGE for scanner 1
    if event == '-IMAGE-':
        
        try:
            #making new tracker ID in order to open several images.
            ID = time.time()
            #image scroll function
            fig, ax, globals()[f'tracker{ID}'] = image_scroll(values['scanner'], values['filter_type'], values['rec_type']) 
            fig.suptitle(f"{values['scanner']} with {values['rec_type']} and {values['filter_type']}" , color='white', fontsize=16)
            #scroll event
            fig.canvas.mpl_connect('scroll_event', globals()[f'tracker{ID}'].on_scroll)
            plt.show() 
        except:
            print('An error occurred')
       
    #IMAGE for scanner 2
    if event == '-IMAGE2-':
        
        try:
            #imports best reconstruction and filtermatch
            best_rec_filter = window['-OUTPUT-'].get().split()
            #Fixing if the reconstruction name has more than one word. Imports rec and filter to two separate variables. 
            best_rec = ' '.join(best_rec_filter[:-1]) 
            best_filter = best_rec_filter[-1]
            
            #making new tracker ID in order to open several images.
            ID = time.time()
            #image scroll funtion
            fig2, ax2, globals()[f'tracker{ID}'] = image_scroll(values['scanner2'], best_filter, best_rec)
            fig2.suptitle(f"{values['scanner2']} with {best_rec} and {best_filter}" , color='white', fontsize=16)
            #scroll event
            fig2.canvas.mpl_connect('scroll_event', globals()[f'tracker{ID}'].on_scroll)
            plt.show()
        except:
            print('An error occurred')
    
    #break
    if event == sg.WIN_CLOSED:
        break
    
window.close()



