# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 13:07:16 2022

@author: josste
Purpose: Explore pysimplegui. Try to make simple program.
Inspiration from https://csveda.com/python-combo-and-listbox-with-pysimplegui/
"""

import PySimpleGUI as psg

psg.theme('SandyBeach')

#define layout
layout = [
        #Scanner 1
        [psg.Text('Select scanner 1', size=(20,1), font='Lucida')],
        [psg.Combo(['Siemens AS+', 'Siemens FLASH', 'Toshiba Prime'], default_value='Siemens AS+', key='scanner1')],
        #Select filter
        [psg.Text('Select filter', size=(20,1), font='Lucida')],
        [psg.Combo(['H10','H20', 'H30', 'H37', 'H40', 'H50', 'H60', 'H70'], default_value='H30', key='filter')],
        #select reconstruction
        [psg.Text('Select reconstruction', size=(20,1), font='Lucida')],
        [psg.Combo(['FBP', 'IR1', 'IR2'], default_value='FBP', key='rec')],
        #Select dose
        [psg.Text('Select dose', size=(20,1), font='Lucida')],
        [psg.Combo(['40 mGy', '60 mGy', '80 mGy'], default_value='60 mGy', key='dose')],
        #Scanner to compare
        [psg.Text('select scanner to find equivalent filter and dose', size=(20,1), font='Lucida')],
        [psg.Combo(['Siemens AS+', 'Siemens FLASH', 'Toshiba Prime'], key='scanner2')],
        #Buttons
        [psg.Button('NEXT', font=('Times New Roman',12)),psg.Button('CANCEL', font=('Times New Roman',12))]
]
win = psg.Window('CT filter match', layout, size=(500,350))

e,v= win.read()

win.close()

strx=""
for val in v:
    strx = strx + " " + val + ","
    
psg.popup('The best settings to match '+ v['scanner1'] + ' with filter ' + v['filter'] + ', reconstruction ' + v['rec'] + " and dose " + 
          v['dose'] + 'with ' + v['scanner2'] + '. Is to use filter: XXX, reconstruction: YYY and dose: ZZZ')

