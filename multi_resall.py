# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 13:23:34 2024

@author: ychuang
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 08:46:41 2024

@author: user
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
      
    mr.multi_resall(sim_dir = sim_dir, file_list = file_list)