# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 11:18:33 2023

@author: Jostein B. Steffensen
Classes used for Flat field test.
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pydicom
import seaborn as sns

class _Image:
    def __init__(self, image):
        self.data_array = image
        
        # calculate mean and std once.
        mean_temp = np.mean(image)
        SD_temp = np.std(image)
        
        # image stats
        self.max = np.max(image)
        self.min = np.min(image)
        self.mean = round(mean_temp, 2)
        self.median = np.median(image)
        self.SD = round(SD_temp, 2)
        self.SNR = round(mean_temp/SD_temp, 2)
        
        print(self.mean)
        print(self.median)
        
        # Window min and max
        self.Wmax = self.max
        self.Wmin = self.min
        self.Wcenter = self.mean
        
    def show(self):
        # Function that displays the image
        plt.figure(figsize=(10,10))
        plt.axis('off')
        plt.title('Image', color = 'white')
        plt.gcf().set_facecolor("black")
        plt.imshow(self.data_array, cmap='Greys_r', vmin=self.Wmin, vmax=self.Wmax)
        
    def new_window(self):
        self.Wcenter = self.median
        self.Wmax = self.Wcenter + (self.Wcenter - self.Wmin)
            
    def show_pix_hmap(self):
        # Pixel heatmap of image
        plt.figure(figsize=(12,12))
        plt.title('Pixel heatmap')
        
        # Make average pixel value be the center of the color bar
        top_bar = np.abs(self.Wmax - self.Wcenter)
        bottom_bar = np.abs(self.Wcenter - self.Wmin)
        
        if(top_bar >= bottom_bar):
            cbar_max = self.Wmax
            cbar_min = self.Wcenter - top_bar
        else:
           cbar_max = self.Wcenter + bottom_bar
           cbar_min = self.Wmin
        
        # Make image figure with deiverging colors.
        plt.xlabel('X')
        plt.ylabel('Y')
        im = plt.imshow(self.data_array, cmap='seismic', vmin=cbar_min-1, vmax=cbar_max+1) # +/- 1 to make sure line shows on color bar
        
        # Color bar and its specs
        cbar = plt.colorbar(im)
        cbar.ax.hlines(self.max, cbar_min, cbar_max, colors='cyan', linestyles='dotted', label=f'Max PV: {self.max}')
        cbar.ax.hlines(self.mean, cbar_min, cbar_max, colors='darkorange', label=f'Avg PV: {self.mean}')
        cbar.ax.hlines(self.min, cbar_min, cbar_max, colors='magenta', linestyles='dashed', label=f'Min PV: {self.min}')
        cbar.ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))


class MammoImage:
    def __init__(self, address):
        self.address = address
        self.path = os.path.dirname(address)
        self.dataset = pydicom.dcmread(address)
        self.image = _Image(self.dataset.pixel_array) # make image object to make it easier to analyze. 
        self.image_data = self.image.data_array
        
        # Filename/ID
        split_address = self.address.split('/')
        splitname = split_address[-1].split('_')
        self.fileID = splitname[0]
   
    def update_pixel_offset(self, offset):
        self.image = _Image(self.dataset.pixel_array-offset)
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
        
    def analyze_area(self, j1, j2, i1, i2):
        # Analyze image area through the image class.
        # i and j for matrix handling. Input and output is x and y. x=j and y=i.
        image_area = _Image(self.image_data[i1:i2+1, j1:j2+1])
        
        # New row of statistics is added to the dataframe
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
        return image_area # Possible to use this object outside the function
        
    def analyze_full(self):
        # Highest possible x/y-value is image size - 1.
        x_max = self.image_data.shape[1] - 1
        y_max = self.image_data.shape[0] - 1
        
        x_start = 0
        y_start = 0
        
        # INCREMENT is the numer of pixels the ROI is moved
        # SIZE is the number of pixels in the ROI (in 1D)
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
        x, y = x_max - (ROI_SIZE+1), 0 # Start analyze from x_max - (ROI_SIZE+1) to make results similar to original program.
        while(y + ROI_SIZE <= y_max-25):     
            self.analyze_area(x, x + ROI_SIZE+1, y, y + ROI_SIZE) # 220923 JBS Increase x with ROI_SIZE+1 to get all pixels
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
        try:
            self.df.to_csv(f'{self.path}/{self.fileID}_data.csv', sep=';', decimal=',')
        except:
            print(f'Could not save the file \"{self.fileID}_data.csv\"')
            return False        
        
        # calculating the mean SNR in all ROIs
        self.SNR_ROI_mean = round(self.df['SNR'].mean(), 2)
                
        # Finding ROIs with pixels or SNR that deviates more than 15% from the average
        # ALSO: Finding ROIs with pixels deviating more than 20% from the ROI pixel average
        DEVIATION_MAX = 15
        DEVIATION_MAX_PIXEL = 20 
        df_dev = pd.DataFrame(columns = ['X', 'Y', 'Mean', 'SD', 'SNR', 'Max', 'Min'])
        df_dev_pixel = pd.DataFrame(columns = ['X', 'Y', 'Mean', 'SD', 'SNR', 'Max', 'Min'])
        for i, row in self.df.iterrows():
            if(i==0):
                # To ignore the first row, which is the analyse of the whole image
                continue
            
            # Some of the row variables
            mean_pixel = row['Mean']
            ROI_SNR = row['SNR']
            pixel_max = row['Max']
            pixel_min = row['Min']
            
            # Checking for 15% devation within ROI compared to the whole image
            if(abs(mean_pixel-self.image.mean)/self.image.mean*100 >= DEVIATION_MAX):
                df_dev = df_dev.append(row, ignore_index=True)
            
            elif(abs(ROI_SNR-self.SNR_ROI_mean)/self.SNR_ROI_mean*100 >= DEVIATION_MAX):
                df_dev = df_dev.append(row, ignore_index=True)
              
            # Checking for 20% deviation of pixel value within ROI     
            if((pixel_max-mean_pixel)/mean_pixel*100 >= DEVIATION_MAX_PIXEL):
                df_dev_pixel = df_dev_pixel.append(row, ignore_index=True)
                
            elif((mean_pixel-pixel_min)/mean_pixel*100 >= DEVIATION_MAX_PIXEL):
                df_dev_pixel = df_dev_pixel.append(row, ignore_index=True)
        
        # Counting the number of deviating discoveries
        num_dev_ROI = len(df_dev)
        num_dev_pixel = len(df_dev_pixel)
                  
        # Coverting doubles and saving file with deviating ROIs        
        df_dev = df_dev.astype({'X': 'int', 'Y': 'int', 'Max': 'int', 'Min': 'int'})
        df_dev_pixel = df_dev_pixel.astype({'X': 'int', 'Y': 'int', 'Max': 'int', 'Min': 'int'})
        try: 
            df_dev.to_csv(f'{self.path}/{self.fileID}_deviating_ROIs.csv', sep=';', decimal=',')
            df_dev_pixel.to_csv(f'{self.path}/{self.fileID}_deviating_ROIs.csv', mode='a', sep=';', decimal=',')
        except:
            print(f'Could not save the file \"{self.fileID}_deviating_ROIs.csv\"')
            return False
        
        # Output
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print(f'FILE ID: {self.fileID}')
        print('--------------------------------------------')
        print(f'Maximum pixel value: {self.image.max}')
        print(f'Average pixel value: {self.image.mean}')
        print(f'Minimum pixel value: {self.image.min}')
        print('--------------------------------------------')
        print(f'SNR mean in ROIs: {self.SNR_ROI_mean}')
        print('--------------------------------------------')
        print(f'Deviating ROIs > 15 % from mean: {num_dev_ROI}')
        print(f'Deviating pixels > 20 % from mean in ROI: {num_dev_pixel}')
        print('--------------------------------------------')
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        return True
    
    # SHOW FUNCTIONS
    def show(self):
        # Displays the image by using the show() function of the Image class. 
        self.image.show()
  
    def show_pix_hmap(self):
        # Displays 3D plot of image from same function in the Image class
        self.image.show_pix_hmap()  
        
    def corner_square(self):
        self.image.new_window()
        
    def show_snr_hmap(self):
        # Heatmap of SNR in ROIs
        plt.figure(figsize=(10,10))
        plt.title('SNR average in ROIs')
        
        # loading data from csv file
        try:
            df_loaded = pd.read_csv(f'{self.path}/{self.fileID}_data.csv', sep=';', decimal=',')
            df_loaded = df_loaded.iloc[1:,:] # removing the first row, info about the whole image
        except:
            print(f'Could not load the file \"{self.fileID}_data.csv\"')
            print('--------------------------------------------')
            return
        
        # reshape dataframe
        data_pivoted = df_loaded.pivot('Y', 'X', 'SNR')
        # Make heatmap
        sns.heatmap(data_pivoted, cmap='seismic', center=self.SNR_ROI_mean)
        plt.show()
      
    def show_pix_avg_hmap(self):  
        # Heatmap of average pixel value in ROIs
        plt.figure(figsize=(10,10))
        plt.title('Average pixel value in ROIs')
        
        # loading data from csv file
        try:
            df_loaded = pd.read_csv(f'{self.path}/{self.fileID}_data.csv', sep=';', decimal=',')
            df_loaded = df_loaded.iloc[1:,:] # removing the first row, info about the whole image
        except:
            print(f'Could not load the file \"{self.fileID}_data.csv\"')
            print('--------------------------------------------')
            return
        
        # reshape dataframe
        data_pivoted = df_loaded.pivot('Y', 'X', 'Mean')
        # Make heatmap
        sns.heatmap(data_pivoted, cmap='seismic', center=self.image.mean)
        plt.show()
    

