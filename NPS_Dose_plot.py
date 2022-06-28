# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 09:19:25 2022

@author: Jostein Steffensen
Purpose: Open ods files and plot NPS curves. 
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import PySimpleGUI as sg
import pydicom
import glob

layout = [
    #reconstructions available
    [sg.Text("Pick scanner: ")], 
    [sg.Combo(['Siemens AS+', 'Siemens Flash'], default_value = 'Siemens AS+', key='scanner')],
    [sg.Text("Choose reconstruction: ")],
    [sg.Combo(['FBP', 'IR1', 'IR2', 'IR4'], default_value = 'FBP', key='rec_type')],
    #All filters available
    [sg.Text("Choose filter: ")], 
    [sg.Combo(['H10s', 'H20s', 'H30s', 'H37s', 'H40s', 'H50s', 'H60s', 'H70h'], default_value = 'H10s', key='filter_type'), 
     sg.Combo(['J30s', 'J37s', 'J40s', 'J45s', 'J49s', 'J70h', 'Q30s', 'Q33s'], default_value = 'J30s', key='filter_type_IR')], 
    [sg.Button('Plot NPS', key='-NPS_BUTTON-')],
    [],
    [sg.Button('Plot all FBP', key='-FBP_ALL-'), sg.Button('Plot all IR1', key='-IR1_ALL-'), sg.Button('Plot all IR2', key='-IR2_ALL-'), sg.Button('Plot all IR4', key='-IR4_ALL-')],
    [sg.Text("Choose dose level: "), sg.Combo(['40 mGy', '60 mGy', '80 mGy', 'ALL'], default_value = 'ALL', key='dose_level'), sg.Button('Test image', key='-IMAGE-')]
    
]

dose_dict = {
    "40 mGy": "CTDI1",
    "60 mGy": "CTDI2",
    "80 mGy": "CTDI3" 
    
}

window = sg.Window('NPS vs Dose', layout, size=(500,350)).Finalize()


##############################################
#NPS FUNCTIONS
##############################################
def plot_NPS_dose(scanner_name, filter_name, reconstruction, onePlot=True, index=0):
    #NOTE: The onePlot parameter is used to make sure all plots are placed on the same figure, when several gaphs are plotted.
    #the index parameter is used to place the plot within the subfigure
    
    #File path to dose folders level 1, 2 and 3.
    dose1_path = r"../NPS tabeller 22/"+scanner_name+"/CTDI1/"
    dose2_path = r"../NPS tabeller 22/"+scanner_name+"/CTDI2/"
    dose3_path = r"../NPS tabeller 22/"+scanner_name+"/CTDI3/"
    
    #Loading dose data 
    df1 = pd.read_excel(dose1_path + reconstruction + '/' + filter_name + '.ods')
    df2 = pd.read_excel(dose2_path + reconstruction + '/' + filter_name + '.ods')
    df3 = pd.read_excel(dose3_path + reconstruction + '/' + filter_name + '.ods')
    
    #Plotting NPS curves
    if onePlot==True:   
        plt.figure()
        plt.title(filter_name + ' with ' + reconstruction)
    if onePlot==False:
        plt.subplot(2,4,index)
        plt.title(filter_name)
    plt.plot(df1['F'], df1['NPSTOT'], label='40 mGy', color='green')
    plt.plot(df1['F'], df2['NPSTOT'], label='60 mGy', color='steelblue')
    plt.plot(df1['F'], df3['NPSTOT'], label='80 mGy', color='purple')
    
    
    plt.grid() 
    
    plt.ylabel('NPS')
    plt.xlabel(r'fq (mm$^{-1})$')
    
    plt.legend()
    if onePlot==True:
        plt.show()
    
def plot_NPS_dose_FBP_all():
    #Plotting all NPS vs Dose for FBP
    onePlot=False
    fig = plt.figure()
    fig.suptitle(value['scanner'] + ' with ' + 'FBP', fontsize=16)
    #
    plot_NPS_dose(value['scanner'], 'H10s', 'FBP', onePlot, 1)
    plot_NPS_dose(value['scanner'], 'H20s', 'FBP', onePlot, 2)
    plot_NPS_dose(value['scanner'], 'H30s', 'FBP', onePlot, 3)
    plot_NPS_dose(value['scanner'], 'H37s', 'FBP', onePlot, 4)
    plot_NPS_dose(value['scanner'], 'H40s', 'FBP', onePlot, 5)
    plot_NPS_dose(value['scanner'], 'H50s', 'FBP', onePlot, 6)
    plot_NPS_dose(value['scanner'], 'H60s', 'FBP', onePlot, 7)
    plot_NPS_dose(value['scanner'], 'H70h', 'FBP', onePlot, 8)
    plt.show()
    
def plot_NPS_dose_IR1_all():
    #Plotting all NPS vs Dose for IR1
    onePlot=False
    fig = plt.figure()
    fig.suptitle(value['scanner'] + ' with ' + 'IR1', fontsize=16)
    #
    plot_NPS_dose(value['scanner'], 'J30s', 'IR1', onePlot, 1)
    plot_NPS_dose(value['scanner'], 'J37s', 'IR1', onePlot, 2)
    plot_NPS_dose(value['scanner'], 'J40s', 'IR1', onePlot, 3)
    plot_NPS_dose(value['scanner'], 'J45s', 'IR1', onePlot, 4)
    plot_NPS_dose(value['scanner'], 'J49s', 'IR1', onePlot, 5)
    plot_NPS_dose(value['scanner'], 'J70h', 'IR1', onePlot, 6)
    plot_NPS_dose(value['scanner'], 'Q30s', 'IR1', onePlot, 7)
    plot_NPS_dose(value['scanner'], 'Q33s', 'IR1', onePlot, 8)
    plt.show()
    
def plot_NPS_dose_IR2_all():
    #Plotting all NPS vs Dose for IR2
    onePlot=False
    fig = plt.figure()
    fig.suptitle(value['scanner'] + ' with ' + 'IR2', fontsize=16)
    #
    plot_NPS_dose(value['scanner'], 'J30s', 'IR2', onePlot, 1)
    plot_NPS_dose(value['scanner'], 'J37s', 'IR2', onePlot, 2)
    plot_NPS_dose(value['scanner'], 'J40s', 'IR2', onePlot, 3)
    plot_NPS_dose(value['scanner'], 'J45s', 'IR2', onePlot, 4)
    plot_NPS_dose(value['scanner'], 'J49s', 'IR2', onePlot, 5)
    plot_NPS_dose(value['scanner'], 'J70h', 'IR2', onePlot, 6)
    plot_NPS_dose(value['scanner'], 'Q30s', 'IR2', onePlot, 7)
    plot_NPS_dose(value['scanner'], 'Q33s', 'IR2', onePlot, 8)
    plt.show()
    
def plot_NPS_dose_IR4_all():
    #Plotting all NPS vs Dose for IR2
    onePlot=False
    fig = plt.figure()
    fig.suptitle(value['scanner'] + ' with ' + 'IR4', fontsize=16)
    #
    plot_NPS_dose(value['scanner'], 'J30s', 'IR4', onePlot, 1)
    plot_NPS_dose(value['scanner'], 'J37s', 'IR4', onePlot, 2)
    plot_NPS_dose(value['scanner'], 'J40s', 'IR4', onePlot, 3)
    plot_NPS_dose(value['scanner'], 'J45s', 'IR4', onePlot, 4)
    plot_NPS_dose(value['scanner'], 'J49s', 'IR4', onePlot, 5)
    plot_NPS_dose(value['scanner'], 'J70h', 'IR4', onePlot, 6)
    plot_NPS_dose(value['scanner'], 'Q30s', 'IR4', onePlot, 7)
    plot_NPS_dose(value['scanner'], 'Q33s', 'IR4', onePlot, 8)
    plt.show()

##############################################
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
##############################################

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

def show_dicom(scanner_name, filter_name, reconstruction, dose_level):
    '''
    Displays the 6th image in a sequence for a certain dose, filter and reconstruction.
    '''
    image_path = "../CT bilder av Catphan/"+ scanner_name +"/" + dose_dict[dose_level] + " " + reconstruction + "  3.0  " + filter_name + "/*" #220623 JBS Changed from *.dcm to * to include other image formats. 
    
    print(image_path)
    sortDict, sortedKeys = sortImages(image_path) #Sort images
    
    print(sortDict)
    final_path = sortDict[sortedKeys[5]]
    
    dataset = pydicom.dcmread(final_path)
    image = dataset.pixel_array * dataset.RescaleSlope + dataset.RescaleIntercept
    plt.axis('off')
    plt.title(dose_level, color = 'white')
    plt.gcf().set_facecolor("black")
    plt.imshow(image, cmap='Greys_r', vmin=-100, vmax=200) #Greys_r for reversed color bar. -1000 HU should be black and not white. 

def show_dicom_all_dose():
    fig = plt.figure()
    filter_name = ''
    if value['rec_type']=='FBP':
        filter_name = value['filter_type']
    else:
        filter_name = value['filter_type_IR']
        
    fig.suptitle(f"{value['scanner']} with {value['rec_type']} and {filter_name}" , color='white', fontsize=16)
    plt.subplot(1,3,1)
    show_dicom(value['scanner'], filter_name, value['rec_type'], '40 mGy')
    plt.subplot(1,3,2)
    show_dicom(value['scanner'], filter_name, value['rec_type'], '60 mGy')
    plt.subplot(1,3,3)
    show_dicom(value['scanner'], filter_name, value['rec_type'], '80 mGy')
    
##############################################
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
##############################################

    
while True:
    event,value= window.read()
    
    #if value['rec_type'] == 'IR1' or value['rec_type'] == 'IR1':
        
    #For spesific NPS-button press. 
    if event == '-NPS_BUTTON-':
        #Make sure file exist.
        if value['rec_type']=='FBP':
            plot_NPS_dose(value['scanner'], value['filter_type'], value['rec_type'])
            
        else:
            plot_NPS_dose(value['scanner'], value['filter_type_IR'], value['rec_type'])
            
    #When one of the "plot all"-buttons are pressed.
    if event == '-FBP_ALL-':
        plot_NPS_dose_FBP_all()
    
    if event == '-IR1_ALL-':
        plot_NPS_dose_IR1_all()
    
    if event == '-IR2_ALL-':
        plot_NPS_dose_IR2_all()
    
    if event == '-IR4_ALL-':
        plot_NPS_dose_IR4_all()
        
    #IMAGES FOR CERTAIN DOSE
    if event == '-IMAGE-' and not value['dose_level']=='ALL':
        #Make sure file exist
        plt.figure()
        if value['rec_type']=='FBP':
            show_dicom(value['scanner'], value['filter_type'], value['rec_type'], value['dose_level'])
        else:
            show_dicom(value['scanner'], value['filter_type_IR'], value['rec_type'], value['dose_level'])
    
    #IMAGES FOR ALL DOSES
    if event == '-IMAGE-' and value['dose_level']=='ALL':
        show_dicom_all_dose()
    
    #break
    if event == sg.WIN_CLOSED:
        break
    
window.close()



