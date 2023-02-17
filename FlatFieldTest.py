# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 12:47:30 2022

@author: Jostein B. Steffensen
Purpose: Do flatfield-test for mammography
"""

import os
import PySimpleGUI as sg
import time

from image_analyzis import MammoImage

current_file_analyzed = ''
working_directory = os.getcwd()

layout = [
    # Upload file
    [sg.Text('Pick DICOM: ', font=('Cambria', 16))],
    [sg.InputText(key = '-FILE_PATH-', enable_events=True),
     sg.FileBrowse(initial_folder = working_directory, file_types=[('DICOM files', '*.dcm')])],
    # View image
    [sg.Button('View image', key = '-VIEW_IMAGE-', disabled = True), sg.Push(), sg.Text('Insert pixel offset:', font=('Cambria', 12))],
    # View pixel heatmap
    [sg.Button('View pixel heatmap', key = '-PIXEL_HEATMAP-', disabled = True), sg.Push(), 
    # Pixel offset 
     sg.Input('--', size=(5,1), key='-pxoffset-', enable_events=True, disabled=True), sg.Button('Add', key='-ADDpxoffset-', size=(5,1), disabled=True)],
    # Analyze
    [sg.Button('Analyze', font=('Times New Roman', 15),  key = '-ANALYZE-', disabled = True, size=(10, 1), button_color='red'), sg.Push(),
    # Remove corner sqare
     sg.Button('Corner Square', key = '-CORNER_SQUARE-')],
    # ROI heatmap
    [sg.Button('View SNR ROI heatmap', key = '-SNR_HEATMAP-', disabled = True)],
    # avg pixel heatmap
    [sg.Button('View pixel average heatmap', key = '-PIXEL_AVERAGE_HEATMAP-', disabled = True)]
    ]

window = sg.Window('Flat Field Test', layout, size = (500, 300))

# GUI control
while True:
    event, values = window.read()
    
    # Opening the file
    if event == '-FILE_PATH-':
        # Making sure the SNR and avg pixel heat map is only available if the analyze is already done to this file
        if(current_file_analyzed != values['-FILE_PATH-']):
            window['-SNR_HEATMAP-'].update(disabled = True)
            window['-PIXEL_AVERAGE_HEATMAP-'].update(disabled = True)
            
        # Making the MammoImage object
        try: 
            mammo_image = MammoImage(values['-FILE_PATH-'])
            # Enable buttons
            window['-VIEW_IMAGE-'].update(disabled = False)
            window['-ANALYZE-'].update(disabled = False)
            window['-PIXEL_HEATMAP-'].update(disabled = False)
            window['-pxoffset-'].update(disabled = False)
            window['-pxoffset-'].update('0')
            window['-ADDpxoffset-'].update(disabled = False)
        except:
            pass
    
    # View the dicom image
    if event == '-VIEW_IMAGE-':
        try:
            mammo_image.show()
        except:
            print("Could not open DICOM")
    
    # Dicom image as a heatmap
    if event == '-PIXEL_HEATMAP-':
        try:
            mammo_image.show_pix_hmap()
        except:
            print('Something went wrong. Troubleshoot the show_pix_hmap()-function in the _Image class.')
            print('--------------------------------------------')
    
    # Include a pixel offset
    if event == '-pxoffset-':
        # make sure there is max 2 characters. 
        if len(values['-pxoffset-'])>2:
            window.Element('-pxoffset-').Update(values['-pxoffset-'][:2])
    
    # Include a pixel offset
    if event == '-ADDpxoffset-':
        # Update background color if the number is valid/not valid.  
        if values['-pxoffset-'].isdigit():
            window['-pxoffset-'].Update(background_color='green')
            mammo_image.update_pixel_offset(int(values['-pxoffset-']))
        else:
            window['-pxoffset-'].Update(background_color='red')
    # Remove corner square 
    if event == '-CORNER_SQUARE-':
        mammo_image.corner_square()
        
    ### FLAT FIELD TEST        
    # Doing the flat field test on image     
    if event == '-ANALYZE-':
        # try:
        st = time.time()
        mammo_image.analyze()
        success = mammo_image.analyze_full()
        et = time.time()
        exc_time = round(et-st, 2)
        print(f"Execution time: {exc_time} sec")
        print('--------------------------------------------')
        
        # Enable buttons that use data from analyse if analyze was successfull.
        if(success):
            window['-SNR_HEATMAP-'].update(disabled = False)
            window['-PIXEL_AVERAGE_HEATMAP-'].update(disabled = False)
            current_file_analyzed = values['-FILE_PATH-'] # Notes the path of file analyzed
    
    # SNR in ROI as heatmap
    if event == '-SNR_HEATMAP-':
        mammo_image.show_snr_hmap()
        
    # Pixel average as heatmap    
    if event == '-PIXEL_AVERAGE_HEATMAP-':
        mammo_image.show_pix_avg_hmap()    
            
    if event == sg.WIN_CLOSED:
        break
    
window.close()