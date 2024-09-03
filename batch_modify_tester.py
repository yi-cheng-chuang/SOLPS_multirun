# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 13:08:14 2024

@author: ychuang
"""

import file_modifier as fm
import os

b_loc = r"C:/Users/ychuang/Documents/batch_test"

batch_name = 'run_job'
c_loc = '{}/{}'.format(b_loc, batch_name)
fn = 'batch_test'

fm.batch_modifier(batch_loc = c_loc, fname = fn, case_loc = b_loc)