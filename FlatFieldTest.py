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
import cv2
import numpy as np

working_directory = os.getcwd()

layout = [[sg.Text('Pick DICOM: ')],
    [sg.InputText(key = '-FILE_PATH-', enable_events=True),
     sg.FileBrowse(initial_folder = working_directory, file_types=[('DICOM files', '*.dcm')])],
    [sg.Button('View image', key = '-VIEW_IMAGE-')],
    [sg.Button('Analyze', key = '-ANALYZE-')]    
    ]

window = sg.Window('Flat Field Test', layout, size = (500, 400))


class mammo_image:
    def __init__(self, address):
        self.address = address
        self.dataset = pydicom.dcmread(address)
        self.image = self.dataset.pixel_array
        self.frame = self.image
        
    def show(self):
        plt.figure()
        plt.axis('off')
        plt.title('Image', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.image, cmap='Greys_r', vmin=460, vmax=500)
        
    def analyze(self):
       self.max = np.max(self.frame)
       self.min = np.min(self.frame)
       self.std = round(self.frame.std(), 2)
       self.avg = round(self.frame.mean(), 2)
       self.SNR = round(self.avg/self.std, 2)
       
       print(f' mean: {self.avg}, std: {self.std}, SNR: {self.SNR}, Max: {self.max}, Min: {self.min}')
       
    def frame_index(self, i1, i2, j1, j2):
       self.frame = self.image[j1:j2, i1:i2]
       self.i1 = i1
       self.i2 = i2
       self.j1 = j1
       self.j2 = j2
       
    def frameshow(self):
        img = self.image
        cv2.rectangle(img, (self.i1, self.j1), (self.i2, self.j2), (0,0,255), -1)
        plt.figure()
        plt.title('Image', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.frame, cmap='Greys_r', vmin=460, vmax=500)#, cmap='Greys_r', vmin=460, vmax=500)
        
    def Max(self):
       return self.max
   
    def Min(self):
       return self.min
   
    def std(self):
       return self.std
   
    def avg(self):
       return self.avg
   
    def snr(self):
       return self.SNR 
        
    
'''
class frame:
    def __init__(self, image):
        self.image = image #image should be a numpy array.
        
    def analyze(self):
        self.max = np.argmax(self.image)
        self.min = np.argmin(self.image)
        self.std = round(self.image.std(), 2)
        self.avg = round(self.image.mean(), 2)
        self.SNR = round(self.avg/self.std, 2)
        
    def Max(self):
        return self.max
    
    def Min(self):
        return self.min
    
    def std(self):
        return self.std
    
    def avg(self):
        return self.avg
    
    def snr(self):
        return self.SNR
    
        

class pixel:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
'''            

while True:
    
    event, values = window.read()
    
    if event == '-FILE_PATH-':
        
        try: 
            mammo_image = mammo_image(values['-FILE_PATH-'])
        
        except:
            pass
    
    if event == '-VIEW_IMAGE-':
        try:
            mammo_image.show()
        
        except:
            print("Could not open DICOM")
        
    if event == '-ANALYZE-':
        #try:
        mammo_image.analyze()
        mammo_image.frame_index(0,48,0,48)
        mammo_image.analyze()
        mammo_image.frameshow()
        mammo_image.frame_index(0,49,49,97)
        mammo_image.analyze()
        mammo_image.frameshow()
        mammo_image.frame_index(0,48,98,146)
        mammo_image.analyze()
        mammo_image.frameshow()
        #except:
           #3# print("Could not analyze")
            
    if event == sg.WIN_CLOSED:
        break
    
window.close()