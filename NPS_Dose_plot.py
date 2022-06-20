# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 09:19:25 2022

@author: Jostein Steffensen
Purpose: Open ods files and plot NPS curves. 
"""

import matplotlib.pyplot as plt
import pandas as pd
import PySimpleGUI as sg

layout = [
    #reconstructions available
    [sg.Text("Choose reconstruction: ")],
    [sg.Combo(['FBP', 'IR1', 'IR2'], key='rec_type')],
    #All filters available
    [sg.Text("Choose filter: ")], 
    [sg.Combo(['H10s', 'H20s', 'H30s', 'H37s', 'H40s', 'H50s', 'H60s', 'H70h', 
              'J30s', 'J37s', 'J40s', 'J45s', 'J49s', 'J70h', 'Q30s', 'Q33s'], key='filter_type')],
    [sg.Button('Plot NPS', key='-NPS_BUTTON-')],
    [],
    [sg.Button('Plot all FBP', key='-FBP_ALL-'), sg.Button('Plot all IR1', key='-IR1_ALL-'), sg.Button('Plot all IR2', key='-IR2_ALL-')]
    
]


window = sg.Window('NPS vs Dose', layout, size=(500,350))

def plot_NPS_dose(filter_name, reconstruction, onePlot=True, index=0):
    #NOTE: The onePlot parameter is used to make sure all plots are placed on the same figure, when several gaphs are plotted.
    #the index parameter is used to place the plot within the subfigure
    
    #File path to dose folders level 1, 2 and 3.
    dose1_path = r"../NPS tabeller 22/Siemens AS+/CTDI1/"
    dose2_path = r"../NPS tabeller 22/Siemens AS+/CTDI2/"
    dose3_path = r"../NPS tabeller 22/Siemens AS+/CTDI3/"
    
    #Loading dose data 
    df1 = pd.read_excel(dose1_path + reconstruction + '/' + filter_name + '.ods')
    df2 = pd.read_excel(dose2_path + reconstruction + '/' + filter_name + '.ods')
    df3 = pd.read_excel(dose3_path + reconstruction + '/' + filter_name + '.ods')
    
    #Plotting NPS curves
    if onePlot==True:   
        plt.figure()
    if onePlot==False:
        plt.subplot(2,4,index)
    plt.plot(df1['F'], df1['NPSTOT'], label='Dose1', color='green')
    plt.plot(df1['F'], df2['NPSTOT'], label='Dose2', color='steelblue')
    plt.plot(df1['F'], df3['NPSTOT'], label='Dose3', color='purple')
    
    plt.title(filter_name + ' with ' + reconstruction)
    plt.grid() 
    
    plt.ylabel('NPS')
    plt.xlabel(r'fq (mm$^{-1})$')
    
    plt.legend()
    if onePlot==True:
        plt.show()
    
def plot_NPS_dose_FBP_all():
    #Plotting all NPS vs Dose for FBP
    onePlot=False
    plt.figure()
    plot_NPS_dose('H10s', 'FBP', onePlot, 1)
    plot_NPS_dose('H20s', 'FBP', onePlot, 2)
    plot_NPS_dose('H30s', 'FBP', onePlot, 3)
    plot_NPS_dose('H37s', 'FBP', onePlot, 4)
    plot_NPS_dose('H40s', 'FBP', onePlot, 5)
    plot_NPS_dose('H50s', 'FBP', onePlot, 6)
    plot_NPS_dose('H60s', 'FBP', onePlot, 7)
    plot_NPS_dose('H70h', 'FBP', onePlot, 8)
    plt.show()
    

def plot_NPS_dose_IR1_all():
    #Plotting all NPS vs Dose for IR1
    onePlot=False
    plt.figure()
    plot_NPS_dose('J30s', 'IR1', onePlot, 1)
    plot_NPS_dose('J37s', 'IR1', onePlot, 2)
    plot_NPS_dose('J40s', 'IR1', onePlot, 3)
    plot_NPS_dose('J45s', 'IR1', onePlot, 4)
    plot_NPS_dose('J49s', 'IR1', onePlot, 5)
    plot_NPS_dose('J70h', 'IR1', onePlot, 6)
    plot_NPS_dose('Q30s', 'IR1', onePlot, 7)
    plot_NPS_dose('Q33s', 'IR1', onePlot, 8)
    plt.show()
    
def plot_NPS_dose_IR2_all():
    #Plotting all NPS vs Dose for IR2
    onePlot=False
    plt.figure()
    plot_NPS_dose('J30s', 'IR2', onePlot, 1)
    plot_NPS_dose('J37s', 'IR2', onePlot, 2)
    plot_NPS_dose('J40s', 'IR2', onePlot, 3)
    plot_NPS_dose('J45s', 'IR2', onePlot, 4)
    plot_NPS_dose('J49s', 'IR2', onePlot, 5)
    plot_NPS_dose('J70h', 'IR2', onePlot, 6)
    plot_NPS_dose('Q30s', 'IR2', onePlot, 7)
    plot_NPS_dose('Q33s', 'IR2', onePlot, 8)
    plt.show()

while True:
    event,value= window.read()
    
    #For spesific button press. 
    if event == '-NPS_BUTTON-': 
        plot_NPS_dose(value['filter_type'], value['rec_type'])
    
    #When one of the "plot all"-buttons are pressed.
    if event == '-FBP_ALL-':
        plot_NPS_dose_FBP_all()
    
    if event == '-IR1_ALL-':
        plot_NPS_dose_IR1_all()
    
    if event == '-IR2_ALL-':
        plot_NPS_dose_IR2_all()
    
    #break
    if event == sg.WIN_CLOSED:
        break
    
window.close()



