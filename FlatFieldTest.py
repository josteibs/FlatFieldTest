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
import os
import time

#from celluloid import Camera


working_directory = os.getcwd()

layout = [[sg.Text('Pick DICOM: ')],
    [sg.InputText(key = '-FILE_PATH-', enable_events=True),
     sg.FileBrowse(initial_folder = working_directory, file_types=[('DICOM files', '*.dcm')])],
    [sg.Button('View image', key = '-VIEW_IMAGE-')],
    [sg.Button('Analyze', key = '-ANALYZE-')],
    [sg.Button('View color plot', key = '-CMAP_IMAGE-')]    
    ]

window = sg.Window('Flat Field Test', layout, size = (500, 400))

class _Image:
    def __init__(self, image):
        self.data_array = image
        
        #calculate mean and std once.
        mean_temp = np.mean(image)
        SD_temp = np.std(image)
        
        #image stats
        self.max = np.max(image)
        self.min = np.min(image)
        self.mean = round(mean_temp, 2)
        self.SD = round(SD_temp, 2)
        self.SNR = round(mean_temp/SD_temp, 2)
        
    def show(self):
        #Function that displays the image
        plt.figure()
        plt.axis('off')
        plt.title('Image', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.data_array, cmap='Greys_r', vmin=self.min, vmax=self.max)
        
    def show_cmap(self):
        #Color map of image
        plt.figure()
        plt.axis('off')
        plt.title('Color map')
        
        #Make average pixel value be the center of the color bar
        top_bar = np.abs(self.max - self.mean)
        bottom_bar = np.abs(self.mean - self.min)
        
        if(top_bar >= bottom_bar):
            cbar_max = self.max
            cbar_min = self.mean - top_bar
        else:
           cbar_max = self.mean + bottom_bar
           cbar_min = self.min
           
        im = plt.imshow(self.data_array, cmap='seismic', vmin=cbar_min, vmax=cbar_max)
        plt.colorbar(im)
        
        #Printing average values
        print(f'Average pixel value: {self.mean}')
        print(f'Maximum pixel value: {self.max}')
        print(f'Minimum pixel value: {self.min}')

class MammoImage:
    def __init__(self, address):
        self.address = address
        self.dataset = pydicom.dcmread(address)
        self.image = _Image(self.dataset.pixel_array) #make image object to make it easier to analyze. 
        self.image_data = self.image.data_array
        
    def analyze(self):
        self.df = pd.DataFrame({'X': int(self.image_data.shape[1]),
                           'Y': int(self.image_data.shape[0]),
                           'Mean': [self.image.mean],
                           'SD': [self.image.SD],
                           'SNR': [self.image.SNR],
                           'Max': [self.image.max],
                           'Min': [self.image.min]                
            })
        
        #print('{:<5}{:<5}{:<10}{:<10}{:<10}{:<10}{:<10}'.format('X', 'Y', 'Mean', 'SD', 'SNR', 'Max', 'Min'))
        #print('{:<5}{:<5}{:<10}{:<10}{:<10}{:<10}{:<10}'.format('all', 'all', self.image.mean, self.image.SD, self.image.SNR, self.image.max, self.image.min))
        #print('-----------------------------------------------------')
        
    def analyze_area(self, j1, j2, i1, i2):
        #Analyze image area through the image class.
        #i and j for matrix handling. Input and output is x and y. x=j and y=i.
        image_area = _Image(self.image_data[i1:i2+1, j1:j2+1])
        
        #New row of statistics is added to the dataframe
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
        #print('{:<5}{:<5}{:<10}{:<10}{:<10}{:<10}{:<10}'.format(j1, i1, image_area.mean, image_area.SD, image_area.SNR, image_area.max, image_area.min))
    
    def analyze_full(self):
        #Highest possible x/y-value is image size - 1.
        x_max = self.image_data.shape[1] - 1
        y_max = self.image_data.shape[0] - 1
        
        x_start = 0
        y_start = 0
        
        #INCREMENT is the numer of pixels the ROI is moved
        #SIZE is the number of pixels in the ROI (in 1D)
        ROI_INCREMENT = 49
        ROI_SIZE = 98
        
        x_steps = np.arange(x_start, x_max-ROI_SIZE-25, ROI_INCREMENT)
        y_steps = np.arange(y_start, y_max-ROI_SIZE-25, ROI_INCREMENT)
        
        # 1. ROIs for left, top and center of image
        #####################################################
        for x in x_steps:
            for y in y_steps:
                self.analyze_area(x, x + ROI_SIZE, y, y + ROI_SIZE)  
          
        # 2. ROIs for right side frame
        #####################################################
        x, y = x_max - (ROI_SIZE+1), 0
        while(y + ROI_SIZE <= y_max-25):     
            self.analyze_area(x, x + ROI_SIZE, y, y + ROI_SIZE)
            y += ROI_INCREMENT
        
        # 3. ROIs for bottom frame
        #####################################################
        x, y = 0, y_max - (ROI_SIZE+1)
        while(x + ROI_SIZE <= x_max-25):
            self.analyze_area(x, x + ROI_SIZE, y, y + ROI_SIZE)   
            x += ROI_INCREMENT
        
        # 4. Last ROI in the bottom right corner
        #####################################################
        self.analyze_area(x_max - (ROI_SIZE+1), x_max-1, y_max - (ROI_SIZE+1), y_max-1)
        
        #
        #
        #
        #
        #save data
        #
        #
        #
        #
        
        # Converting some of the doubles to integers
        self.df = self.df.astype({'X': 'int', 'Y': 'int', 'Max': 'int', 'Min': 'int'})
        #save as csv. Sep and decimal is choosen to fit excel
        self.df.to_csv('mammo_image_data.csv', sep=';', decimal=',')  
        
        # calculating the mean SNR in all ROIs
        SNR_ROI_mean = round(self.df['SNR'].mean(), 2)
        print(f'SNR mean in ROIs: {SNR_ROI_mean}')
        
        # Finding ROIs with pixels or SNR that deviates more than 15% from the average
        DEVIATION_MAX = 15
        df_dev = pd.DataFrame(columns = ['X', 'Y', 'Mean', 'SD', 'SNR', 'Max', 'Min'])
        for i, row in self.df.iterrows():
            mean_pixel = row['Mean']
            ROI_SNR = row['SNR']
            
            if(abs(mean_pixel-self.image.mean)/self.image.mean*100 >= DEVIATION_MAX):
                df_dev = df_dev.append(row, ignore_index=True)
            
            elif(abs(ROI_SNR-SNR_ROI_mean)/SNR_ROI_mean*100 >= DEVIATION_MAX):
                df_dev = df_dev.append(row, ignore_index=True)
                
        # Coverting doubles and saving file with deviating ROIs        
        df_dev = df_dev.astype({'X': 'int', 'Y': 'int', 'Max': 'int', 'Min': 'int'})
        df_dev.to_csv('mammo_image_deviating_ROIs.csv', sep=';', decimal=',')
            
        
    def show(self):
        # Displays the image by using the show() function of the Image class. 
        self.image.show()
  
    def show_cmap(self):
        # Displays 3D plot of image from same function in the Image class
        self.image.show_cmap()

#GUI control
while True:
    
    event, values = window.read()
    
    if event == '-FILE_PATH-':
        try: 
            mammo_image = MammoImage(values['-FILE_PATH-'])
        except:
            pass
    
    if event == '-VIEW_IMAGE-':
        try:
            mammo_image.show()
        except:
            print("Could not open DICOM")
        
    if event == '-ANALYZE-':
        #try:
        st = time.time()
        mammo_image.analyze()
        mammo_image.analyze_full()
        et = time.time()
    
    if event == '-CMAP_IMAGE-':
        mammo_image.show_cmap()
        
    try:
        print(f"Execution time: {et-st}")
    except:
        pass
           #3# print("Could not analyze")
            
    if event == sg.WIN_CLOSED:
        break
    
window.close()