# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:59:06 2024

@author: ychuang
"""

import math
import multirun as mr
import argparse

parser = argparse.ArgumentParser(description='create multiple runs')
parser.add_argument('-t','--tail', type= str, metavar='', 
                    required=True, help='series filename tail')
parser.add_argument('-c','--copy', type= str, metavar='', 
                    required=True, help='copy folder')
args = parser.parse_args()

"""
tail = 

"""



if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
      
    mr.createfile_modboundary(sim_dir = sim_dir, tail = args.tail, copy_folder = args.copy)
    
    file_list = mr.find_files(sim_dir= sim_dir, tail = args.tail)
      
    mr.change_batch(sim_dir = sim_dir, file_list = file_list, tail = args.tail)
    