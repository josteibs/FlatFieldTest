# -*- coding: utf-8 -*-
"""
Created on Wed July 28 13:19:17 2021

@author: Vilde Ragnvaldsen


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
#Updated for 22 project, 'CT filtermatching on head' by Jostein B. Steffensen (JBS)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Sommarjobb Medisinsk fysikk
Prosjekt: Filtermatching på gjennomsnitt NPS
"""
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import time

#### CHOOSE PARAMETERS ####
FOV = 220 #Reconstruction diameter (mm)
R = 400 # Viewing distancce (mm)
D = 300 #Size of displayed image (mm)

N = 12 #Number of image slices to include in analysis 

#### CHOOSE WHICH TWO SCANNERS AND RECONSTRUCTION METHODS TO COMPARE ####
# (OBS: MAKE SURE TO WRITE EXACTLY AS IN FOLDER)
#Scanner1: "Old scanner" - Scanner to match
scanner1 = "Siemens AS+" 
recon1 = "all"  #Write "ALL" to include FBP and all levels of iterative reconstruction

#Scanner2: "New scanner" - Scanner to find matching filters of
scanner2 = "Siemens Flash"
recon2 = "all" #Write "ALL" to include FBP and all levels of iterative reconstruction

#### WHERE TO SAVE RESULTS ####
folder1 = "../Results AVG"
folder2 = "Matching "+scanner1+' '+recon1
folder3 = "With "+scanner2+' '+recon2
#date = time.strftime("%Y-%m-%d") #todays date (automatic)
path = os.path.join(folder1, folder2, folder3)#, date)

#Create folderpath if not already present
try:
    os.makedirs(path)
except OSError:
    if  not os.path.isdir(path):
        raise

################# DEFINING FUNCTIONS TO BE USED LATER #############################
#From a dataframe (NPS-data) remove data with f higher than 1.2 (Nyquist), remove column NPSTOT (avg) and
#remove columns that exceed the chosen number of slices (N). Add column with AVG of the remaining columns.
def fix(data, number):
    #data = NPS table as dataframe; number = N (defined above)
    ind = data.index.get_loc(1.2)
    data = data.head(n=ind)
    data = data.drop(['NPSTOT'], axis = 1, errors ='ignore')
    if len(data.columns) > number: 
        data = data.iloc[:, :number]
    data['AVG'] = data.mean(axis=1)
    return data

#Normalising a list of numbers such that the area under the curve is 1
def normalise(f, datalist):
    area = np.trapz(datalist, x=f) #Trapez method to calculate area under the curve
    datalist = datalist/area 
    return datalist

#Normalise a list of numbers to its maximum value
def normalise_V(datalist):
    datalist = (datalist - np.min(datalist))/(np.max(datalist) - np.min(datalist))
    return datalist

#Visual response function (Eq 2 in Samei et al 2012)
def V(f, fov, r, d):
    rho = (f * (fov*r*np.pi)/(d*180)) 
    #a1 = 1.5; a2 = 0.98; a3 = 0.68
    V_rho = (np.abs(rho**1.5 * np.exp(-0.98*rho**0.68)))**2
    return normalise_V(V_rho) #Return V as a normalised list of numbers

#Filtrate data by multiplying with Visual responce function
def filtrate(f, datalist):
    V_rho = V(f, FOV, R, D)
    datalist = np.multiply(datalist, np.abs(V_rho)**2)
    return datalist
        
def analyse(f, data1, data2):
    #data1, data2: numpy list of AVG NPS 
    #RMSD
    sd = 0
    n = 0
    for v1, v2 in zip(data1, data2):
        sd += (v1-v2)**2 #Find the distance between two datapoints, square and add to sum
        n += 1 #Counting number of datapoints
    rmsd = np.sqrt(sd/n) #Divide sd by n to get mean, and calculate the root = RMSD
    #PFD
    peak1 = data1.argmax()
    PF1 = f[peak1]
    peak2 = data2.argmax()
    PF2 = f[peak2]
    pfd = np.abs(PF1-PF2)
    return rmsd, pfd

#Plot NPS curves from data (Excel file with ImageQC NPS data)
def plot_NPS(data, title):
    data.plot() #Tar med labels frå kolonner
    plt.ylabel('NPS')
    plt.xlabel('Spatial frequency (mm$^{-1}$)')
    plt.title('Noise Power Spectrum for {}'.format(title))
    #plt.show()
    plt.close()
    return 0

def plot_two_avg(f, data1, data2, label1, label2):
    plt.figure()
    plt.plot(f, data1, label="{}".format(label1))  #scanner1 +' '+
    plt.plot(f, data2, label="{}".format(label2)) #scanner2 +' '+ 
    plt.xlabel('Spatial frequency (mm$^{-1}$)')
    plt.ylabel('NPS')
    plt.title('Noise Power Spectrum') 
    plt.legend()
    plt.savefig(os.path.join(path, "NPS - {}.png".format(label1 +' - '+ label2)), dpi=300, bbox_inches="tight")
    #plt.show()
    plt.close()
    return 0


####LIST DIR PATHS TO FILES THAT WILL BE INCLUDED IN THE ANALYSIS
folder_scanner1 = f'../NPS tabeller 22/{scanner1}/CTDI2'
filepathlist1 = []
if recon1 == "ALL" or recon1 == "all":
    for subdir, dirs, files in os.walk(folder_scanner1):
        for d in dirs:
            for filepath in glob.iglob(folder_scanner1+'/'+d+'/*.ods'): 
                filepathlist1.append(filepath)
else:
    for filepath in glob.iglob(folder_scanner1+'/'+recon1+'/*.ods'): 
        filepathlist1.append(filepath)

folder_scanner2 = f'../NPS tabeller 22/{scanner2}/CTDI2'
filepathlist2 = []
if recon2 == "ALL" or recon2 == "all":
    for subdir, dirs, files in os.walk(folder_scanner2):
        for d in dirs:
            for filepath in glob.iglob(folder_scanner2+'/'+d+'/*.ods'): 
                filepathlist2.append(filepath)
else:
    for filepath in glob.iglob(folder_scanner2+'/'+recon2+'/*.ods'): 
        filepathlist2.append(filepath)

number_of_filters1 = len(filepathlist1)
number_of_filters2 = len(filepathlist2)

########### HEAT MAPS #############
heatmap_rmsd = np.empty((number_of_filters1, number_of_filters2), dtype=float)
heatmap_pfd = np.empty((number_of_filters1, number_of_filters2), dtype=float)
#Empty lists, will be filled with the name of the different filters
listfilters1 = []
listfilters2 = []
#Empty lists, will be filled with the name of matching filters
listmatches = []
listRMSD = []
listPFD = []

#Import NPS-tables for the two chosen scanners 
#Iterate through all files (filters) for the two scanners, compare one and one filter,
#make heatmap and score best match

#Indices for iterating through heatmaps
i=0 #Rows: data1 (= Scanner 1)
j=0 #Columns: data2 (= Scanner 2)

for filepath1 in filepathlist1: #iterate through filters of scanner 1
    NPS_data1 = pd.read_excel(filepath1, index_col='F')
    NPS_data1 = fix(NPS_data1, N)
    freq = NPS_data1.index.to_numpy() #List of frequencies (same for data1 and data2)
    NPS_data1 = (NPS_data1['AVG']).to_numpy() #Keep only the average NPS
    NPS_data1 = filtrate(freq, normalise(freq, NPS_data1))
    
    namefilter1 = os.path.splitext(os.path.basename(filepath1))[0] #Extract name of filter from directory
    namerec1 = os.path.split(os.path.split(filepath1)[0])[1] #reconstruction name 220706 JBS
    namefilter1 = f'{namerec1} {namefilter1}'
    print('pause')
    
    listfilters1.append(namefilter1) #When iterating through filters in data1, append name of filter in list
    #Variables for scoring the best matches:
    bestRMSD = 100 
    bestPFD = 100
    bestmatch_data2 = pd.DataFrame()
    bestmatch_name = " "
    
    for filepath2 in filepathlist2: #iterate through filters of scanner 2
        NPS_data2 = pd.read_excel(filepath2, index_col='F')
        NPS_data2 = fix(NPS_data2,N)
        NPS_data2 = (NPS_data2['AVG']).to_numpy() #Keep only average NPS
        NPS_data2 = filtrate(freq, normalise(freq, NPS_data2))
    
        namefilter2 = os.path.splitext(os.path.basename(filepath2))[0]
        namerec2 = os.path.split(os.path.split(filepath2)[0])[1] #reconstruction name 220706 JBS
        namefilter2 = f'{namerec2} {namefilter2}'
        if i==0: #On first iteration through filters in data1, append name of filter in list
            listfilters2.append(namefilter2)
            
        rmsd, pfd = analyse(freq, NPS_data1, NPS_data2)
        heatmap_rmsd[i,j] = rmsd
        heatmap_pfd[i,j] = pfd
        '''
        #Print RMSD values for every match
        print('RMSD between ', namefilter1, 'and ', namefilter2, ': \n', rmsd)
        '''
        #Score best match based on RMSD (can be changed to PFD below by swapping left and right handside of #)
        if rmsd < bestRMSD: #if pfd < bestPFD:
            bestRMSD = rmsd
            bestPFD = pfd
            bestmatch_data2 = NPS_data2
            bestmatch_name = namefilter2
        j+=1 #Go to next filter for data2
    #For each filter of scanner 1, get the best match of scanner 2 and plot NPS curves for the two:f
    plot_two_avg(freq, NPS_data1, bestmatch_data2, (scanner1+' '+namefilter1), (scanner2+' '+bestmatch_name))
    #Put best match in list:
    listmatches.append(bestmatch_name)
    listRMSD.append(np.round(bestRMSD,4))
    listPFD.append(np.round(bestPFD,2))
    
    i+=1 #Go to next filter for data1
    j = 0 #Go to first filter for data2
    
#MAKE TABLE FOR BEST MATCH OF SCANNER 2 GIVEN SCANNER 1
match_scanner1 = pd.DataFrame()
match_scanner1[scanner1] = listfilters1
match_scanner1[scanner2] = listmatches
match_scanner1['RMSD (mm^2)'] = listRMSD
match_scanner1['|PFD| (mm^{-1})'] = listPFD 
match_scanner1.to_csv(os.path.join(path, "Matching table "+scanner1+recon1+"-"+scanner2+recon2+".csv"), sep=';')
print(match_scanner1)

#Plot RMSD heatmaps
fig, ax = plt.subplots(figsize=(number_of_filters2+3,number_of_filters1))
im = ax.imshow(heatmap_rmsd, cmap = 'YlOrRd') #vmin=0,vmax=0.1
ax.set_xlabel(scanner2, loc='left', fontsize=20)
ax.set_ylabel(scanner1, loc='top', fontsize=20)
ax.set_yticks(np.arange(number_of_filters1))
ax.set_xticks(np.arange(number_of_filters2))
ax.set_xticklabels(listfilters2,fontsize = 15, rotation=45, ha = 'left', rotation_mode='anchor')
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_yticklabels(listfilters1, fontsize = 15)
for i in range(number_of_filters1):
    for j in range(number_of_filters2):
        text = ax.text(j,i, np.round(heatmap_rmsd[i,j],3), fontsize=12, ha="center", va="center", color="black")
cbar = fig.colorbar(im)
cbar.set_label('RMSD (mm$^2$)', fontsize=25)
cbar.ax.tick_params(labelsize=15)
fig.tight_layout()
#ax.set_title('RMSD', fontsize=30)
plt.savefig(os.path.join(path, 'Heatmap_RMSD.png'), dpi=500, bbox_inches="tight")
plt.show()

#Plot PFD heatmap
fig, ax = plt.subplots(figsize=(number_of_filters2+3,number_of_filters1))
im = ax.imshow(heatmap_pfd, cmap = 'YlOrRd')
ax.set_xlabel(scanner2, loc='left', fontsize=20)
ax.set_ylabel(scanner1, loc='top', fontsize=20)
ax.set_yticks(np.arange(number_of_filters1))
ax.set_xticks(np.arange(number_of_filters2))
ax.set_xticklabels(listfilters2, fontsize = 15, rotation=45, ha = 'left', rotation_mode='anchor')
ax.xaxis.set_label_position('top')
ax.xaxis.set_ticks_position('top')
ax.set_yticklabels(listfilters1, fontsize=15)
for i in range(number_of_filters1):
    for j in range(number_of_filters2):
        text = ax.text(j,i, np.round(heatmap_pfd[i,j],2), fontsize=12, ha="center", va="center", color="black")
cbar = fig.colorbar(im)
cbar.set_label('|PFD| (mm$^{-1}$)', fontsize=25)
cbar.ax.tick_params(labelsize=15)
fig.tight_layout()
#ax.set_title('PFD', fontsize=30)
plt.savefig(os.path.join(path, 'Heatmap_PFD.png'), dpi=500, bbox_inches="tight")
plt.show()