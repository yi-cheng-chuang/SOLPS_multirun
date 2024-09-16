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
parser.add_argument('-s','--start', type= int, metavar='', 
                    required=True, help='attampt file start number')
args = parser.parse_args()

"""


"""



if __name__ == '__main__':
      
    sim_dir = mr.find_dir()
    
    denscan_dic = {'start': 5.512, 'stop': 9.512, 'space': 5}
    tempscan_dic = {'start': 4.115, 'stop': 8.115, 'space': 5}
    
    mr.sqscancpfile_modboundary(sim_dir = sim_dir, tail = args.tail, copy_folder = args.copy, 
                        start_num = args.start, ds_dic = denscan_dic, ts_dic = tempscan_dic)
    
    file_list = mr.find_files(sim_dir= sim_dir, tail = args.tail)
      
    mr.change_batch(sim_dir = sim_dir, file_list = file_list, tail = args.tail)
    