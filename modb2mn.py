# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:09:27 2024

@author: ychuang
"""

import math
import multirun as mr
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-r','--runtype', type= str, metavar='', required=True, help='b2mn modify')
parser.add_argument('-t','--tail', type= str, metavar='', required=True, help='series run name tail')
args = parser.parse_args()

"""

run_type_list = ['longrun', 'ioutrun', 'testrun']

"""



if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
    file_list = mr.find_files(sim_dir= sim_dir, tail= args.tail)
      
    mr.change_b2mn(sim_dir = sim_dir, file_list = file_list, run_type = args.runtype)
    
    # mr.mod_b2mn_and_play(sim_dir = sim_dir, file_list = file_list, run_type = args.runtype)
    
