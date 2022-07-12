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
from celluloid import Camera

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
       
       print(f' i: {self.i1}, j: {self.j1}, mean: {self.avg:.2f}, std: {self.std:.2f}, SNR: {self.SNR}, Max: {self.max}, Min: {self.min}')
       
       
    def frame_index(self, i1, i2, j1, j2):
       self.frame = self.image[i1:i2+1, j1:j2+1]
       self.i1 = i1
       self.i2 = i2
       self.j1 = j1
       self.j2 = j2

    def full_analyze(self):
        '''
        imCopy = np.copy(self.image)
        fig = plt.figure()
        camera = Camera(fig)
        '''
        pixel_step = 49
        i_steps = self.image.shape[0] // pixel_step
        j_steps = self.image.shape[1] // pixel_step
        
        #starting frame
        i_start = 0
        j_start = 0
        i_end = 48
        j_end = 48
        
        f = open('FlatFieldTest.txt', 'w')
        
        f.write(f'    i \t j \t mean \t std \t SNR \t Max \t Min \n')
        
        while (j_end < pixel_step*j_steps):
            while (i_end < pixel_step*i_steps):
                self.frame_index(i_start, i_end, j_start, j_end)
                self.analyze()
                
                f.write(f'{self.i1:5} \t {self.j1:5} \t {self.avg:.2f} \t {self.std:.2f} \t {self.SNR:.2f} \t {self.max} \t {self.min} \n')
                
                i_start += pixel_step
                i_end += pixel_step
                
                
                
                
                
                #figure stuff
                '''
                rect = cv2.rectangle(imCopy, (self.j1, self.i1), (self.j2, self.i2), (0,0,255), -1)
                plt.ioff()
                plt.gcf().set_facecolor("black")
                plt.imshow(rect, cmap='Greys_r', vmin=460, vmax=500)#, cmap='Greys_r', vmin=460, vmax=500)
                camera.snap()
                '''
            j_start += pixel_step
            j_end += pixel_step
            i_start = 0
            i_end = 48
    
        
        #animation = camera.animate()
        #animation.save('image_analyze.gif', writer ='imagemagick')
        f.close()
       
    def frameshow(self):
        plt.figure()
        plt.title('pre rec', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.frame, cmap='Greys_r', vmin=460, vmax=500)#, cmap='Greys_r', vmin=460, vmax=500)
        
        img = self.image
        rect = cv2.rectangle(img, (self.i1, self.j1), (self.i2, self.j2), (0,0,255), -1)
        print(rect.shape)
        plt.figure()
        plt.title('post_rec', color = 'white')
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
        #mammo_image.analyze()
        #mammo_image.full_analyze()
        
        mammo_image.frame_index(2801,2850,0,48)
        mammo_image.analyze()
        mammo_image.frameshow()
        '''
        mammo_image.frame_index(0,48,49,97)
        mammo_image.analyze()
        mammo_image.frameshow()
        
        mammo_image.frame_index(0,48,49,97)
        mammo_image.analyze()
        mammo_image.frameshow()
        '''
        #except:
           #3# print("Could not analyze")
            
    if event == sg.WIN_CLOSED:
        break
    
window.close()