# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:38:26 2024

@author: ychuang
"""

import math
import autorun_test as att
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-r','--runtype', type= str, metavar='', required=True, help='b2mn modify')
args = parser.parse_args()

"""

run_type_list = ['longrun', 'ioutrun', 'testrun']

"""



if __name__ == '__main__':
      
    sim_dir = att.find_dir()
    file_list = att.find_files(sim_dir= sim_dir)
    
    att.mod_runtype_and_play(sim_dir = sim_dir, file_list = file_list, run_type = args.runtype)
    