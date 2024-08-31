# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 14:44:56 2024

@author: ychuang
"""



import math
import plot_b2ftrace_resall_D as pbrd
import multirun as mr
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-t','--tail', type= str, metavar='', required=True, help='series run name tail')
parser.add_argument('-l','--label', type= str, metavar='', required=True, help='what residual to plot')
args = parser.parse_args()

"""

args_dic = {'conD0': 2, 'conD1': 3, 'momD0': 4, 'momD1': 5, 'totmom': 6,
                    'ee': 7, 'ei': 8, 'phi': 9}

"""



if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
    file_list = mr.find_files(sim_dir= sim_dir, tail= args.tail)
      
    pbrd.plot_multiple_residual(sim_dir = sim_dir, file_list = file_list, label = args.label)