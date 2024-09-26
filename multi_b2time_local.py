# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:55:30 2024

@author: ychuang
"""


import argparse
import textwrap
import plot_b2time as pbt
import multirun as mr
import glob


gbase = r"C:/Users/ychuang/Documents/SOLPS_data/simulation_data/mast/027205/org_new25scan_fast"
gdir = glob.glob('{}/*{}'.format(gbase, 'fast_a'))


print(gdir)

filename_list = []

for p in gdir:
    k = p.split('\\')[-1]
    filename_list.append(k)



print(filename_list[5])
    

special_fileloc = '{}/{}'.format(gbase, filename_list[5])



timesa, myvar = pbt.load_b2time_local(file_loc = special_fileloc, plotvars = 'nesepm')

print(type(timesa))
print(type(myvar))


pbt.plot_b2time_local(plotvars = 'nesepm', file_loc = special_fileloc, series = False)


# pbt.load_b2time(plotvars= nesepm)