# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 19:06:09 2024

@author: ychuang
"""

import math
import multirun as mr
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-t','--tail', type= str, metavar='', required=True, help='series run name tail')
# parser.add_argument('-sh','--shot', type= str, metavar='', required=True, help='discharge number')
args = parser.parse_args()

"""

run_type_list = ['longrun', 'ioutrun', 'testrun']

"""



if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
    file_list = mr.find_files(sim_dir= sim_dir, tail= args.tail)
      
    mr.create_output(sim_dir = sim_dir, file_list = file_list)
    
    # mr.mod_b2mn_and_play(sim_dir = sim_dir, file_list = file_list, run_type = args.runtype)