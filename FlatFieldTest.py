# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 12:47:30 2022

@author: Jostein B. Steffensen
Purpose: Do flatfield-test for mammography
"""

import numpy as np
import PySimpleGUI as sg
import pydicom
import matplotlib.pyplot as plt
import pandas as pd
import os, csv 
import cv2

from celluloid import Camera

working_directory = os.getcwd()

layout = [[sg.Text('Pick DICOM: ')],
    [sg.InputText(key = '-FILE_PATH-', enable_events=True),
     sg.FileBrowse(initial_folder = working_directory, file_types=[('DICOM files', '*.dcm')])],
    [sg.Button('View image', key = '-VIEW_IMAGE-')],
    [sg.Button('Analyze', key = '-ANALYZE-')]    
    ]

window = sg.Window('Flat Field Test', layout, size = (500, 400))


class _Image:
    def __init__(self, image):
        self.data_array = image
        self.max = np.max(image)
        self.min = np.min(image)
        
        #calculate mean and std once.
        mean_temp = image.mean(dtype=np.longfloat)
        SD_temp = image.std()
        
        self.mean = round(mean_temp, 2)
        self.SD = round(SD_temp, 2)
        self.SNR = round(mean_temp/SD_temp, 2)
        
    def show(self):
        #Function that displays the image
        plt.figure()
        plt.axis('off')
        plt.title('Image', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.data_array, cmap='Greys_r', vmin=460, vmax=500)


class mammo_image:
    def __init__(self, address):
        self.address = address
        self.dataset = pydicom.dcmread(address)
        self.image = _Image(self.dataset.pixel_array) #make image object to make it easier to analyze. 
        self.image_data = self.image.data_array
        
    def analyze(self):
        #print(f'Max: {self.image.max}, Min: {self.image.min}, mean: {self.image.mean}, SD: {self.image.SD}, SNR: {self.image.SNR}')
        #print('{:<5}{:<5}{:<10}{:<10}{:<10}{:<10}{:<10}'.format('X', 'Y', 'Mean', 'SD', 'SNR', 'Max', 'Min'))

        #print('{:<5}{:<5}{:<10}{:<10}{:<10}{:<10}{:<10}'.format('all', 'all', self.image.mean, self.image.SD, self.image.SNR, self.image.max, self.image.min))
        #print('-----------------------------------------------------')
        
        
        self.df = pd.DataFrame({'X': int(self.image_data.shape[1]),
                           'Y': int(self.image_data.shape[0]),
                           'Mean': [self.image.mean],
                           'SD': [self.image.SD],
                           'SNR': [self.image.SNR],
                           'Max': [self.image.max],
                           'Min': [self.image.min]                
            })
        
    def analyze_area(self, j1, j2, i1, i2):
        imCopy = np.copy(self.image_data)
        
        #i and j for matrix handling. Input and output is x and y. x=j and y=i. 
        imCopy = imCopy[i1:i2+1, j1:j2+1]
        image_area = _Image(imCopy)
        #print(f'X: {j1}, Y: {i1}, mean: {image_area.mean}, SD: {image_area.SD}, SNR: {image_area.SNR}, Max: {image_area.max}, Min: {image_area.min}')
        #print('{:<5}{:<5}{:<10}{:<10}{:<10}{:<10}{:<10}'.format(j1, i1, image_area.mean, image_area.SD, image_area.SNR, image_area.max, image_area.min))
        
        new_row = {
            'X': j1,
            'Y': i1,
            'Mean': image_area.mean,
            'SD': image_area.SD,
            'SNR': image_area.SNR,
            'Max': image_area.max,
            'Min': image_area.min                
            }
        
        self.df = self.df.append(new_row, ignore_index=True)
     
    
    def analyze_full(self):
        #Highest possible x/y-value is image size - 1.
        x_max = self.image_data.shape[1] - 1
        y_max = self.image_data.shape[0] - 1
        
        x = 0
        y = 0
        
        #INCREMENT is the numer of pixels the ROI is moved
        #SIZE is the number of pixels in the ROI (in 1D)
        ROI_INCREMENT = 49
        ROI_SIZE = 98
        
        
        while(x + ROI_SIZE <= x_max-25):
            y = 0
            while(y + ROI_SIZE <= y_max-25):
                
                self.analyze_area(x, x + ROI_SIZE, y, y + ROI_SIZE)
                
                y += ROI_INCREMENT
            
            x += ROI_INCREMENT
        
        
        
        
        x = x_max - (ROI_SIZE+1)
        y=0
        while(y + ROI_SIZE <= y_max-25):
                        
            self.analyze_area(x, x + ROI_SIZE, y, y + ROI_SIZE)
            
            y += ROI_INCREMENT
        
        
        x=0
        y = y_max - (ROI_SIZE+1)
        while(x + ROI_SIZE <= x_max-25):
            self.analyze_area(x, x + ROI_SIZE, y, y + ROI_SIZE)
                
            x += ROI_INCREMENT
        
        
        #save data
        self.df = self.df.astype({'X': 'int', 'Y': 'int', 'Max': 'int', 'Min': 'int'})
        self.df.to_csv('mammo_image_data.csv', sep=';', decimal=',')  
        
        SNR_ROI_mean = round(self.df['SNR'].mean(), 2)
        print(f'SNR mean in ROIs: {SNR_ROI_mean}')
        
        #Finding ROIs with pixels or SNR that deviates more than 15% from the average
        for i, row in self.df.iterrows():
            mean_pixel = row['Mean']
            ROI_SNR = row['SNR']
            
            if(abs(mean_pixel-self.image.mean)/self.image.mean*100 >= 15):
                print(row)
            
            elif(abs(ROI_SNR-SNR_ROI_mean)/SNR_ROI_mean >= 15):
                print(row)
            
        
    def show(self):
        #Displays the image by using the show() function in the Image class. 
        self.image.show()
'''
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
        
        #imCopy = np.copy(self.image)
        #fig = plt.figure()
        #camera = Camera(fig)
        
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
                
                #rect = cv2.rectangle(imCopy, (self.j1, self.i1), (self.j2, self.i2), (0,0,255), -1)
                #plt.ioff()
                #plt.gcf().set_facecolor("black")
                #plt.imshow(rect, cmap='Greys_r', vmin=460, vmax=500)#, cmap='Greys_r', vmin=460, vmax=500)
                #camera.snap()
                
            j_start += pixel_step
            j_end += pixel_step
            i_start = 0
            i_end = 48
          
        
        #animation = camera.animate()
        #animation.save('image_analyze.gif', writer ='imagemagick')
        f.close()
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
        mammo_image.analyze_full()
        
        #except:
           #3# print("Could not analyze")
            
    if event == sg.WIN_CLOSED:
        break
    
window.close()