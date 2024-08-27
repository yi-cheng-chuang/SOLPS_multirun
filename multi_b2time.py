# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 16:21:37 2024

@author: ychuang
"""

import argparse
import textwrap
import plot_b2time as pbt
import multirun as mr


parser = argparse.ArgumentParser()
parser.add_argument('-t','--tail', type= str, metavar='', required=True, help='series run name tail')
parser.add_argument('-p','--plotvars',  type = str, help = 'List of variables to plot from b2time.nc')
args = parser.parse_args()




if __name__ == '__main__':
    

    sim_dir = mr.find_dir()
    file_list = mr.find_files(sim_dir= sim_dir, tail= args.tail)
      
    pbt.load_b2time(plotvars= args.plotvars)