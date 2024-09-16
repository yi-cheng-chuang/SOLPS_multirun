# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 17:44:02 2024

@author: ychuang
"""

import multirun_set as ms
import os

# simu_loc, simu_case, case_loc = td.test_dir()

# simu_loc = 'C:/Users/ychuang/Documents/SOLPS_data/simulation_data/mast/027205'
# simu_case = 'org_automatic_tool_testcase'
# case_loc = '{}/{}'.format(simu_loc, simu_case)


def flag_filter(flag_dic):

    mod_dic = {}
    
    for aa in list(flag_dic.keys()):
        
        if flag_dic[aa] == True:
            mod_dic[aa] = True
        
        elif flag_dic[aa] == False:
            pass
    
    return mod_dic
        
        

# b2mn_loc = '{}/{}'.format(case_loc, 'b2mn.dat')
    


def b2mn_modifier(b2mn_loc, case_loc, run_type):
    
    with open(b2mn_loc) as f:
         lines = f.readlines()
    
    b2mn_flagdictpl_dic = ms.b2mn_set(run_type)
    
    
    for dickey in b2mn_flagdictpl_dic.keys():
        
        flagdictpl = b2mn_flagdictpl_dic[dickey]
        
        modb2mn_dic = flag_filter(flag_dic = flagdictpl[0])
        b2mnvalue_dic = flagdictpl[1]
        
        
        for j, string in enumerate(lines):
            
            for aa in list(modb2mn_dic.keys()):
                
                if aa in string:
                    # print('{} is on line {}'.format(aa, str(j)))
                    
                    if dickey == 'basicrun':
                        
                        writelist = ''.join('\'{}\''.format(aa) + "\t\t\t" + "   " + '\'{}\''.format(b2mnvalue_dic[aa]))
                        lines[j] = writelist + "\n"
                        print('{} is currently {}'.format(aa, b2mnvalue_dic[aa]))
                    
                    elif dickey == 'output':
                        
                        writelist = ''.join('\'{}\''.format(aa) + "\t\t" + "       " + '\'{}\''.format(b2mnvalue_dic[aa]))
                        lines[j] = writelist + "\n"
                        
                        print('{} is currently {}'.format(aa, b2mnvalue_dic[aa]))
                        
    
    
    # m_gfile = '{}/prac_b2mn.dat'.format(case_loc)


    with open(b2mn_loc,'w') as g:
        for i, line in enumerate(lines):         ## STARTS THE NUMBERING FROM 1 (by default it begins with 0)    
            g.writelines(line)
    
    # f_dir = os.getcwd()
    
    print('new b2mn is created in {}'.format(case_loc))
        
        
# b2mn_modifier()        


def batch_modifier(batch_loc, fname, case_loc):
    
    with open(batch_loc) as f:
         lines = f.readlines()
    
    key_list = ['#SBATCH --job-name', '#SBATCH -t', '#SBATCH --mail-user']
    
    email = 'ychuang@wm.edu'
    
    
    index_dic = {}
    
    for j, string in enumerate(lines):
        
        for aa in key_list:
                      
            if aa in string:
                print('{} is on line {}'.format(aa, str(j)))
                index_dic[aa] = j
    
    print(index_dic)
    
    k1 = index_dic['#SBATCH --job-name']
    
    list3 = lines[k1].split('=')
    

    list3[1] = '{}'.format(fname)
        
  
    writelist = ''.join(list3[0] + '=' + list3[1])
    lines[k1] = writelist + "\n"
    print('{} is currently {}'.format('#SBATCH --job-name', fname))
    

    k2 = index_dic['#SBATCH -t']

    list1 = lines[k2].split()
    list1[2] = '27:00:00'
    
    print(list1)
    
    
    writelist = ''.join(x + ' ' for x in list1)
    lines[k2] = writelist + "\n"
    print('{} is currently {}'.format('#SBATCH -t', fname))
           
    
    k4 = index_dic['#SBATCH --mail-user']

    list2 = lines[k4].split('=')
    list2[1] = email
       
    
    writelist = ''.join('#SBATCH --mail-user' + '=' + list2[1])
    lines[k4] = writelist + "\n"
    print('{} is currently {}'.format('#SBATCH --mail-user', email))
    
    with open(batch_loc,'w') as g:
        for i, line in enumerate(lines):         ## STARTS THE NUMBERING FROM 1 (by default it begins with 0)    
            g.writelines(line)
    
    # f_dir = os.getcwd()
    
    print('new batch is created in {}'.format(case_loc))




def SN_b2boundary_modifier(b2boundary_loc, case_loc, bound_list):
    
    with open(b2boundary_loc) as f:
         lines = f.readlines()
    
    
    key_list = ['bcene', 'bceni', 'enepar(1,1)', 'enipar(1,1)', 'bccon(0,1)', 'conpar(0,1,1)']
    
    index_dic = {}
    
    for j, string in enumerate(lines):
        
        for aa in key_list:
                      
            if aa in string:
                print('{} is on line {}'.format(aa, str(j)))
                index_dic[aa] = j
    
    print(index_dic)
    
    def substitute_bondpos(lines, index_dic, keys, sub_pos, sub_str):
    
        k1 = index_dic[keys]
        listsp = lines[k1].split()
        print('{} line split is:'.format(ki))
        print(listsp)
        listsp[sub_pos] = sub_str
        writelist = ''.join(' '+ x + ' ' for x in listsp)
        lines[k1] = writelist + "\n"
        print('{} core boundary is currently {}'.format(keys, sub_str))
    
    
    def writelist_attempt(keys, listsp):
        
        if keys == 'enepar(1,1)' or keys == 'enipar(1,1)':
            writelist = ''.join(' ' + '{}'.format(listsp[0]) + ' ' + '{}'.format(listsp[1]) 
         + '  ' + '{}'.format(listsp[2]) + '    ' + '{}'.format(listsp[3]) + '  ' 
         + '{}'.format(listsp[4]) + '    ' + '{}'.format(listsp[5]))
        elif keys == 'conpar(0,1,1)':
            writelist = ''.join(' ' + '{}'.format(listsp[0]) + '  ' + '{}'.format(listsp[1]) + '    ' 
                + '{}'.format(listsp[2]) + ' ' + '{}'.format(listsp[3]))
        else:
            print('keys!!')
        
        return writelist
    
    
    
    
    def substitute_bondvalue(lines, index_dic, keys, sub_pos, sub_val, sub_pw):
    
        k1 = index_dic[keys]
        listsp = lines[k1].split()
        print('{} line split is:'.format(ki))
        print(listsp)
        sep_list = listsp[sub_pos].split('E')
        print('{} value split is:'.format(ki))
        print(sep_list)
        joint = ''.join('{}'.format(sub_val) + 'E'+ '{}'.format(sub_pw) + ',')
        print(joint)
        listsp[sub_pos] = joint
        
        # writelist = ''.join(' '+ x + ' ' for x in listsp)
        
        writelist = writelist_attempt(keys = keys, listsp = listsp)
        # print(adj_writelist)
        
        
        lines[k1] = writelist + "\n"
        print('{} core boundary is currently {}'.format(keys, joint))
    
    for ki in key_list:
        
        if ki == 'bcene':
            substitute_bondpos(lines = lines, index_dic = index_dic, keys = ki, 
                       sub_pos = 1, sub_str = '16,')
        
        elif ki == 'bceni':
            substitute_bondpos(lines = lines, index_dic = index_dic, keys = ki, 
                       sub_pos = 1, sub_str = '24,')
        
        elif ki == 'enepar(1,1)':
            substitute_bondvalue(lines = lines, index_dic = index_dic, keys = ki, 
                       sub_pos = 1, sub_val = '{:.3f}'.format(bound_list[1]), sub_pw = '+05')
        
        elif ki == 'enipar(1,1)':
            
            substitute_bondvalue(lines = lines, index_dic = index_dic, keys = ki, 
                       sub_pos = 1, sub_val = '{:.3f}'.format(bound_list[1]), sub_pw = '+05')
        
        elif ki == 'bccon(0,1)':
            substitute_bondpos(lines = lines, index_dic = index_dic, keys = ki, 
                       sub_pos = 2, sub_str = '22,')
        
        elif ki == 'conpar(0,1,1)':
            substitute_bondvalue(lines = lines, index_dic = index_dic, keys = ki, 
                       sub_pos = 3, sub_val = '{:.3f}'.format(bound_list[0]), sub_pw = '+20')
        


    with open(b2boundary_loc,'w') as g:
        for i, line in enumerate(lines):         ## STARTS THE NUMBERING FROM 1 (by default it begins with 0)    
            g.writelines(line)
    
    # f_dir = os.getcwd()
    
    print('new b2mn is created in {}'.format(case_loc))
    




"""

    # k1 = index_dic['bcene']
    # listsp_1 = lines[k1].split()
    # listsp_1[1] = '5,'
    # writelist = ''.join(x + ' ' for x in listsp_1)
    # lines[k1] = writelist + "\n"
    # print('{} is currently {}'.format('bcene core boundary', '5,'))
    
    
    
    
    
    
    
    # writelist = ''.join(x + ' ' for x in list1)
    # lines[k2] = writelist + "\n"
    # print('{} is currently {}'.format('Initiated', fname))
           
    
    # writelist = ''.join('cd' + ' ' + case_loc)
    # lines[k3] = writelist + "\n"
    # print('{} is currently {}'.format('cd', fname))
     
    
    # writelist = ''.join(x + ' ' for x in list2)
    # lines[k4] = writelist + "\n"
    # print('{} is currently {}'.format('completed', fname))





"""
    
        
        
        