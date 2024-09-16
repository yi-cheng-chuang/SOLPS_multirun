# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 17:00:40 2024

@author: ychuang
"""

import math
import multirun as mr
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-t','--tail', type= str, metavar='', 
                    required=True, help='series filename tail')
args = parser.parse_args()




if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
    file_list = mr.find_files(sim_dir= sim_dir, tail = args.tail)
      
    mr.multi_boundary_copy(sim_dir = sim_dir, file_list = file_list)