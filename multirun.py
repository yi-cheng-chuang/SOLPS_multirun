# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 17:09:42 2024

@author: ychuang
"""

#Import os module
import os
import file_modifier as fm


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
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            
            os.chdir(case_loc)
            os.system('2dt {} &'.format(sep_type))



def multi_plot_last10(sim_dir, file_list, last10_fname):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            # b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
               
            last10_plot(case_loc = case_loc, name_last10 = last10_fname)




def squrescan_filecreater(gen_folder, tail, shotnum_st, denscan_list, tempscan_list):
    
    
    for den in denscan_list:
        
        for tem in tempscan_list:
        
            new_folder = '{}_nf{:.1f}tf{:.1f}_{}'.format(shotnum_st, den, tem, tail)
            
            os.system('cp -r {} {}'.format(gen_folder, new_folder))
            
            shotnum_st = shotnum_st + 1
    
    

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


def mod_multi_runtype(sim_dir, file_list, run_type):
    
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
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            # b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
            batch_loc = '{}/{}'.format(case_loc, 'batch_example')
            
            # multifile_creater(gen_folder = gen_folder)
            
                     
            if tail in fname:
                
                fm.batch_modifier(batch_loc = batch_loc, fname = fname, 
                               case_loc = case_loc, idchange = True)


def change_b2boundary(sim_dir, file_list, tail):
    
    
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            bbp_loc = '{}/{}'.format(case_loc, 'b2.boundary.parameter')
                       
                     
            if tail in fname:
                
                fm.SN_b2boundary_modifier(b2boundary_loc = bbp_loc, case_loc = case_loc)







"""

run_type_list = ['longrun', 'ioutrun', 'testrun']



"""


def mod_runtype_and_play(sim_dir, file_list, run_type):
    
    for fname in file_list:
        
        if fname != 'baserun':
            
            case_loc = '{}/{}'.format(sim_dir, fname)
            b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
                
            os.chdir(case_loc)
            
            fm.b2mn_modifier(b2mn_loc = b2mn_loc, case_loc = case_loc, 
                              run_type = run_type)
            
            os.system('cp b2fstate b2fstati')
            os.system('rm b2mn.prt')
            os.system('qsub batch_example')
        
        else:
            pass



def squrescan_createfile(sim_dir, tail, copy_folder):
    
    st_num = 76
    ds_list = [3.4, 4.0, 5.0, 6.0, 7.0]
    ts_list = [2.5, 3.0, 4.0, 5.0, 6.0]
    
    squrescan_filecreater(gen_folder = copy_folder, tail = tail, 
                        shotnum_st = st_num, denscan_list = ds_list, 
                        tempscan_list = ts_list)
    







def remove_file(file_list):
    
    
    for fname in file_list:
        
            
        os.system('rm -r {}'.format(fname))
        print('{} is removed'.format(fname))
    


    




"""

#Create a new directory
os.mkdir("test_folder")

#Change current working directory
os.chdir("test_folder")

#Print current working directory
print("Current directory now:" , os.getcwd())


os.system('cp b2fstate b2fstati')
os.system('rm b2mn.prt')

"""





