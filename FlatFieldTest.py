# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 12:47:30 2022

@author: Jostein B. Steffensen
Purpose: Do flatfield-test for mammography
"""

import PySimpleGUI as sg
import pydicom
import matplotlib.pyplot as plt
import os, csv 

working_directory = os.getcwd()

layout = [[sg.Text('Pick DICOM: ')],
    [sg.InputText(key = '-FILE_PATH-'),
     sg.FileBrowse(initial_folder = working_directory, file_types=[('DICOM files', '*.dcm')])],
    [sg.Button('View image', key = '-VIEW_IMAGE-')]    
    ]

window = sg.Window('Flat Field Test', layout, size = (500, 400))


class mammo_analyze:
    def __init__(self, address):
        self.address = address
        self.dataset = pydicom.dcmread(address)
        self.image = self.dataset.pixel_array
        
    def show(self):
        plt.axis('off')
        plt.title('Image', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.image, cmap='Greys_r', vmin=460, vmax=500)

class frame:
    def __init__(self, image):
        self.image = image
        
    def analyze(self):
        self.max = #claculate
        self.min = #calculate
        self.sdd = #calculate
        self.avg = #calulate average pixel value
        self.SNR = self.avg/self.sdd
        
    def Max(self):
        return self.max
    
    def Min(self):
        return self.min
    
        

class pixel:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
            

while True:
    
    event, values = window.read()
    
    if event == '-VIEW_IMAGE-':
        mammo_image = mammo_analyze(values['-FILE_PATH-'])
        mammo_image.show()
        
    
    
    if event == sg.WIN_CLOSED:
        break
    
window.close()