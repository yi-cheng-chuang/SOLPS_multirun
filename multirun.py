# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 17:09:42 2024

@author: ychuang
"""

#Import os module
import os
import re
import file_modifier as fm
import numpy as np


"""
envir_name = os.environ['OS']
print(envir_name)

"""


def find_dir():
    
    sim_dir = os.getcwd()

    #Print current working directory
    print("Current directory:" , os.getcwd())
    
    return sim_dir



def find_files(sim_dir, tail):
    
    file_list = os.listdir(sim_dir)
    
    filter_list = []
    
    for fname in file_list:
        
        if tail in fname:
            
            filter_list.append(fname)
    
    print(filter_list)
    
    return filter_list


       

def last10_plot(case_loc, name_last10):
    
    os.chdir(case_loc)
    os.system('2d_profiles')
    os.system('xyplot < {}.last10 &'.format(name_last10))
    


def multi_runjob_copy(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        print(case_loc)
        os.system('cp ../org_std/run_job .')
        print('copy run_job')


def multi_boundary_copy(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        print(case_loc)
        os.system('cp ../org_std/b2.boundary.parameters .')
        print('copy b2.boundary.parameters')


def multi_transportinput_copy(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        print(case_loc)
        os.system('cp ../org_std/b2.transport.inputfile .')
        print('copy b2.boundary.parameters')




def run_multi_PB2(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        print(case_loc)
        os.system('python3 ../../../../../repository/stop/PB2.py')
        print('run PB2 for {}'.format(fname))


def run_multi_EB2(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        print(case_loc)
        os.system('python3 ../../../../../repository/stop/EB2.py')
        print('run EB2 for {}'.format(fname))



def multi_plot(sim_dir, file_list, scenario_type):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            # b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
            
            
            
            if scenario_type == 'plot_last10':
                
                last10_plot(case_loc = case_loc, name_last10 = 'ne3da')
            
            
            elif scenario_type == 'runxport':
                
                os.chdir(case_loc)
                
                os.system('python3 ../../../../SOLPSxport/SOLPSxport_dr.py -g ../../gnpfiles/g027205.00275 -p ../../gnpfiles/fit_027205_275.dat -t 275 -f 0.5 -sh 0')
                
            
            elif scenario_type == 'no':
                pass

"""
sep_type_list = ['nesepm', 'tesepm']




"""


def multi_plot_sep(sim_dir, file_list, sep_type):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        os.system('2dt {} &'.format(sep_type))
        


def multi_resall(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        os.system('resall_D &')          
            



def multi_plot_last10(sim_dir, file_list, last10_fname):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            # b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
               
            last10_plot(case_loc = case_loc, name_last10 = last10_fname)



def squrescan_filecreater(gen_folder, tail, shotnum_st, denscan_list, tempscan_list):
    
    
    for den in denscan_list:
        
        for tem in tempscan_list:
        
            new_folder = '{}_nf{:.3f}tf{:.3f}_{}'.format(shotnum_st, den, tem, tail)
            
            os.system('cp -r {} {}'.format(gen_folder, new_folder))
            
            shotnum_st = shotnum_st + 1
    
    

def change_b2mn(sim_dir, file_list, run_type):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
                
            os.chdir(case_loc)
            
            fm.b2mn_modifier(b2mn_loc = b2mn_loc, case_loc = case_loc, 
                              run_type = run_type)
        
        else:
            pass
        
            

def change_batch(sim_dir, file_list, tail):
    
    for fname in file_list:
        
            
        case_loc = '{}/{}'.format(sim_dir, fname)
        # b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
        batch_loc = '{}/{}'.format(case_loc, 'run_job')
        
        # multifile_creater(gen_folder = gen_folder)
        
                 
        if tail in fname:
            
            fm.batch_modifier(batch_loc = batch_loc, fname = fname, 
                           case_loc = case_loc)


def change_b2boundary(sim_dir, file_list, tail):
    
    
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        bbp_loc = '{}/{}'.format(case_loc, 'b2.boundary.parameters')
        sp = fname.split('_')[1]
        print(sp)
        L = re.findall('\d+\.\d+', sp)
        print(L)
        bound_list = []
        for ii in L:
            bound_list.append(float(ii))
        
        print(bound_list)
            
            
        fm.SN_b2boundary_modifier(b2boundary_loc = bbp_loc, case_loc = case_loc,
                                      bound_list = bound_list)
        

            
"""

run_type_list = ['longrun', 'ioutrun', 'testrun']


"""


def mod_b2mn_and_play(sim_dir, file_list, run_type):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
            batch_loc = '{}/{}'.format(case_loc, 'run_job')
                
            os.chdir(case_loc)
            
            fm.b2mn_modifier(b2mn_loc = b2mn_loc, case_loc = case_loc, 
                              run_type = run_type)
            
            fm.batch_modifier(batch_loc = batch_loc, fname = fname, 
                           case_loc = case_loc)
            
            os.system('cp b2fstate b2fstati')
            os.system('rm b2mn.prt')
            os.system('sbatch run_job')
        
        else:
            pass



def sqscancpfile_modboundary(sim_dir, tail, copy_folder, start_num, ds_dic, ts_dic):
    
    
    ds_start_num = ds_dic['start']
    ds_stop_num = ds_dic['stop']
    ds_space_num = ds_dic['space']
    
    ds_list = np.linspace(ds_start_num, ds_stop_num, ds_space_num)
    
    ts_start_num = ts_dic['start']
    ts_stop_num = ts_dic['stop']
    ts_space_num = ts_dic['space']
    
    ts_list = np.linspace(ts_start_num, ts_stop_num, ts_space_num)
    
    
    squrescan_filecreater(gen_folder = copy_folder, tail = tail, 
                        shotnum_st = start_num, denscan_list = ds_list, 
                        tempscan_list = ts_list)
    



def remove_file(file_list):
    
    
    for fname in file_list:
        
            
        os.system('rm -r {}'.format(fname))
        print('{} is removed'.format(fname))
    
    
    

def create_output(sim_dir, file_list):
    
    for fname in file_list:
                 
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        atp_num = fname.split('_')[0]
        print(atp_num)
        
        os.chdir(case_loc)
        
        os.system('pwd')
        os.system('OutputGen')
        # os.system('{}'.format(shot_num))
        # os.system('{}'.format(atp_num))
        os.system('pwd')
        os.system('EirOutputGen')
        # os.system('{}'.format(shot_num))
        # os.system('{}'.format(atp_num))
    



def multi_ioutrun(sim_dir, file_list):
    
    for fname in file_list:
        
        case_loc = '{}/{}'.format(sim_dir, fname)
        
        os.chdir(case_loc)
        os.system('b2run b2mn > run.log')


"""

#Create a new directory
os.mkdir("test_folder")

#Change current working directory
os.chdir("test_folder")

#Print current working directory
print("Current directory now:" , os.getcwd())


os.system('cp b2fstate b2fstati')
os.system('rm b2mn.prt')


def multi_run(sim_dir, file_list, scenario_type):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
            batch_loc = '{}/{}'.format(case_loc, 'batch_example')
            
            if scenario_type == 'ioutrun':
                
                os.chdir(case_loc)
                
                fm.b2mn_modifier(b2mn_loc = b2mn_loc, case_loc = case_loc, 
                                  run_type = 'ioutrun')
                
                
                os.system('cp b2fstate b2fstati')
                os.system('rm b2mn.prt')
                os.system('qsub batch_example')
                
            elif scenario_type == 'change batch':
                
                tk = fname.split('_')[-1]
                
                if tk == 'tttest':
                    
                    fm.batch_modifier(batch_loc = batch_loc, fname = fname, 
                                   case_loc = case_loc, idchange = True)
            
            elif scenario_type == 'change_b2mn':
                
                os.chdir(case_loc)
                
                fm.b2mn_modifier(b2mn_loc = b2mn_loc, case_loc = case_loc, 
                                  run_type = 'longrun')
            
            elif scenario_type == 'longrun':
                
                os.chdir(case_loc)
                
                fm.b2mn_modifier(b2mn_loc = b2mn_loc, case_loc = case_loc, 
                                  run_type = 'longrun')
                
                
                os.system('cp b2fstate b2fstati')
                os.system('rm b2mn.prt')
                os.system('qsub batch_example')
                
            
            elif scenario_type == 'more to discover':
                pass




"""





