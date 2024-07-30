# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 21:27:02 2024

@author: ychuang
"""

import math
import multirun as mr
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-t','--tail', type= str, metavar='', required=True, help='series run name tail')
args = parser.parse_args()

"""

run_type_list = ['longrun', 'ioutrun', 'testrun']

"""



if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
    file_list = mr.find_files(sim_dir= sim_dir, tail= args.tail)
    
    mr.change_b2boundary(sim_dir = sim_dir, file_list = file_list, tail = args.tail)