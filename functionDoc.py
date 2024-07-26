##########################################################################################



# Python stuff written by Eric Emdee
# His email: eemdee@pppl.gov
# Most functions written starting February 2019, some added as time went on

# Most of these functions are translations from matlab scripts written by Wouter Dekeyser
# His e-mail: wouter.dekeyser@kuleuven.be 
# But he wrote those scripts in November 2016 so good luck reaching him



##########################################################################################



import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colorsMPL
import math
import os.path

from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import scipy
from scipy import interpolate
from matplotlib import ticker
from matplotlib.patches import Ellipse

liMass = 6.941*1.66e-27
kb = 1.38064852e-23
mp=1.6726219236900001e-27
mn=mp
qe=1.6021766339999999E-019
ev=qe
eps0=8.8541878128000006E-012
me=9.10938356e-31

def stupidFunction():
# function to check if I loaded the doc correctly
	print('hey stupid')

def find_nearest(array, value):
# finds the element closest to value and returns the index of that element
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def is_number(s):
# checks to see if s is a number
# useful for parsing outputfiles
    try:
        float(s)
        return True
    except ValueError:
        return False

def nPartsFromT(T,wallArea):
    nLi = math.exp(26.9 - 18880.0/T - 0.494*math.log(T)) / (kb*T)
    nParticlesTotalFromT = wallArea * nLi * math.sqrt(8 * kb * T / (math.pi * liMass)) / 4.0
    return(nParticlesTotalFromT)

def read_field(f,fieldname,dims,intField=False):
# reads a single variable from an outputfile
# used in various read_b2f* functions
    line = f.readline().rstrip()
    # find the right field
    while fieldname not in line:
        line = f.readline().rstrip()
        if len(line) == 0:
            print('read_field: EOF reached without finding '+str(fieldname))
            print('The first variable not found is probably not in your file')
            print('Take out the search for that variable in the function doc or update your SOLPS so that the output is produced')
            return 0

    # Consistency check: number of elements specified
    # in the file should equal prod(dims)

    for i in range(len(line.split())):
        if is_number(line.split()[i]): numin = int(line.split()[i])
            
    if (numin != np.prod(dims)): 
        print(line)
        print('read_field: inconsistent number of input elements.');

    fieldVal=[]
    # collect field values
    while (len(fieldVal) != numin):
        line = f.readline().rstrip()
        for i in range(len(line.split())):
            if (intField): fieldVal.append(int(line.split()[i]))
            else:
                fieldVal.append(float(line.split()[i]))
    fieldVal=np.array(fieldVal)

    if (np.size(dims) > 1): fieldVal = fieldVal.reshape(dims,order='F').copy()
    return fieldVal

def read_ft44_field(fid,ver,fieldname,dims,intField=False):
# Auxiliary routine to read fields from fort.44 file
# Verion 20160829: field label and size are specified in fort.44
# Do consistency check on the data
    if (ver >= 20160829):
        # Search the file until identifier 'fieldname' is found
        line = fid.readline().rstrip()
        while fieldname not in line:
            line = fid.readline().rstrip()
            if len(line) == 0: print('read_ft44_field: EOF reached without finding '+str(fieldname))
        # Consistency check: number of elements specified in the file should equal
        # prod(dims)
        for i in range(len(line.split())):
            if is_number(line.split()[i]): numin = int(line.split()[i])
	
        if (numin != np.prod(dims) and 'wld' not in fieldname):
            print('issue with field '+fieldname)
            print("numin="+str(numin))
            print("np.prod(dims)="+str(np.prod(dims)))
            print('read_ft44_rfield: inconsistent number of input elements.')
            print('if this is a wall paramter, could be fine, check it.')
            print('number of walls is hardcoded in, need to fix')
        elif (numin!= np.prod(dims) and ('wldnek' in fieldname or 'wldnep' in fieldname)):
            dims = [numin]
        elif (numin!= np.prod(dims) and ('wldna' in fieldname or 'ewlda' in fieldname or 'wldnm' in fieldname or 'ewldm' in fieldname)):
            dims[1] = int(numin/dims[0])
            

    # Read the data
    fieldVal=[]
    # collect field values
    while (len(fieldVal) != numin):
        line = fid.readline().rstrip()
        if ('wld' in fieldname) and len(fieldVal)>=numin-1: break
        for i in range(len(line.split())):
            if ('wlpump' in fieldname):
                if not is_number(line.split()[i]): continue
            if (intField): fieldVal.append(int(line.split()[i]))
            else: fieldVal.append(float(line.split()[i]))
    fieldVal=np.array(fieldVal)
    if (np.size(dims) > 1 and 'wld' not in fieldname): fieldVal = fieldVal.reshape(dims,order='F').copy()
    if (np.size(dims) > 1 and 'wld' in fieldname): fieldVal = fieldVal.reshape(dims).copy() 

    return fieldVal


def read_b2fgmtry(b2fgmtryLoc):
# reads b2fgmtry and returns a class of the data
    fieldname = 'nx,ny'
    fid = open(b2fgmtryLoc)
    line = fid.readline().rstrip()#read the first line
    version = line[7:17]
    print('read_b2fgmtry -- file version '+version)#check the version
    dim = read_field(fid,'nx,ny',2,True)#check the grid size
    nx  = dim[0]
    ny  = dim[1]
    qcdim = [nx+2,ny+2]
    if (version >= '03.001.000'): qcdim = [nx+2,ny+2,2] 
    
    #initialize class that will hold all the data of b2fgmtry
    class gmtryResults:
        def __init__(self):
            
            # Read symmetry information

            self.isymm = read_field(fid,'isymm',1,True)

            # Read gmtry variables
            self.crx  = read_field(fid,'crx' ,[nx+2,ny+2,4])
            self.cry  = read_field(fid,'cry' ,[nx+2,ny+2,4])
            self.fpsi = read_field(fid,'fpsi',[nx+2,ny+2,4])
            self.ffbz = read_field(fid,'ffbz',[nx+2,ny+2,4])
            self.bb   = read_field(fid,'bb'  ,[nx+2,ny+2,4])
            self.vol  = read_field(fid,'vol' ,[nx+2,ny+2])
            self.hx   = read_field(fid,'hx'  ,[nx+2,ny+2])
            self.hy   = read_field(fid,'hy'  ,[nx+2,ny+2])
            self.qz   = read_field(fid,'qz'  ,[nx+2,ny+2,2])
            self.qc   = read_field(fid,'qc'  ,qcdim)
            self.gs   = read_field(fid,'gs'  ,[nx+2,ny+2,3])

            # Some other geometrical parameters

            self.nlreg       = read_field(fid,'nlreg',1,True)
            self.nlxlo       = read_field(fid,'nlxlo',self.nlreg,True)
            self.nlxhi       = read_field(fid,'nlxhi',self.nlreg,True)
            self.nlylo       = read_field(fid,'nlylo',self.nlreg,True)
            self.nlyhi       = read_field(fid,'nlyhi',self.nlreg,True)
            self.nlloc       = read_field(fid,'nlloc',self.nlreg,True)

            self.nncut       = read_field(fid,'nncut'    ,1,True)
            self.leftcut     = read_field(fid,'leftcut'  ,self.nncut,True)
            self.rightcut    = read_field(fid,'rightcut' ,self.nncut,True)
            self.topcut      = read_field(fid,'topcut'   ,self.nncut,True)
            self.bottomcut   = read_field(fid,'bottomcut',self.nncut,True)

            self.leftix      = read_field(fid,'leftix'   ,[nx+2,ny+2],True)
            self.rightix     = read_field(fid,'rightix'  ,[nx+2,ny+2],True)
            self.topix       = read_field(fid,'topix'    ,[nx+2,ny+2],True)
            self.bottomix    = read_field(fid,'bottomix' ,[nx+2,ny+2],True)
            self.leftiy      = read_field(fid,'leftiy'   ,[nx+2,ny+2],True)
            self.rightiy     = read_field(fid,'rightiy'  ,[nx+2,ny+2],True)
            self.topiy       = read_field(fid,'topiy'    ,[nx+2,ny+2],True)
            self.bottomiy    = read_field(fid,'bottomiy' ,[nx+2,ny+2],True)

            self.region      = read_field(fid,'region'     ,[nx+2,ny+2,3],True)
            self.nnreg       = read_field(fid,'nnreg'      ,3,True)
            self.resignore   = read_field(fid,'resignore'  ,[nx+2,ny+2,2],True)
            self.periodic_bc = read_field(fid,'periodic_bc',1,True)

            self.pbs  = read_field(fid,'pbs' ,[nx+2,ny+2,2])

            self.parg = read_field(fid,'parg',100)
    gmtry = gmtryResults()#instantiate class
    # Close file
    fid.close()
    print('done reading geometry file')
    return gmtry

def read_b2fstate(b2fstateLoc):
# reads b2fstate and returns a class of the data
    fieldname = 'nx,ny'
    fid = open(b2fstateLoc)
    line = fid.readline().rstrip()#read the first line
    version = line[7:17]
    print('read_b2fstate -- file version '+version)#check the version
    dim = read_field(fid,'nx,ny,ns',3,True)#check the grid size
    nx  = dim[0]
    ny  = dim[1]
    ns  = dim[2]
    fluxdim  = [nx+2,ny+2,2]
    fluxdimp = [nx+2,ny+2]
    fluxdims = [nx+2,ny+2,2,ns]
    if (version >= '03.001.000'):
        fluxdim  = [nx+2,ny+2,2,2]
        fluxdimp = fluxdim
        fluxdims = [nx+2,ny+2,2,2,ns]
    #initialize class that will hold all the data of b2fstate
    class stateResults:
        def __init__(self):
            # Read charges etc.

            self.zamin = read_field(fid,'zamin',ns)
            self.zamax = read_field(fid,'zamax',ns)
            self.zn    = read_field(fid,'zn',ns)
            self.am    = read_field(fid,'am',ns)

            # Read state variables

            self.na     = read_field(fid,'na',[nx+2,ny+2,ns])
            self.ne     = read_field(fid,'ne',[nx+2,ny+2])
            self.ua     = read_field(fid,'ua',[nx+2,ny+2,ns])
            self.uadia  = read_field(fid,'uadia',[nx+2,ny+2,2,ns])
            self.te     = read_field(fid,'te',[nx+2,ny+2])
            self.ti     = read_field(fid,'ti',[nx+2,ny+2])
            self.po     = read_field(fid,'po',[nx+2,ny+2])

            # Read fluxes

            self.fna    = read_field(fid,'fna',fluxdims)
            self.fhe    = read_field(fid,'fhe',fluxdim)
            self.fhi    = read_field(fid,'fhi',fluxdim)
            self.fch    = read_field(fid,'fch',fluxdim)
            self.fch_32 = read_field(fid,'fch_32',fluxdim)
            self.fch_52 = read_field(fid,'fch_52',fluxdim)
            self.kinrgy = read_field(fid,'kinrgy',[nx+2,ny+2,ns])
            self.time   = read_field(fid,'time',1)
            self.fch_p  = read_field(fid,'fch_p',fluxdimp)
            
    state = stateResults()#instantiate class
    # Close file
    fid.close()
    print('done reading state file')
    return state

def read_b2fplasmf(fileName,nx,ny,ns):
#
# Read formatted b2fplasmf file created by B2.5.
# returns class of SOME of the data (add what you want if it's not here)
    if not (os.path.isfile(fileName)): 
        print("b2fplasmf: Cannot find the filename")
        return 0
    fid = open(fileName)
    if (fid == -1): print("read_b2fplasmf: can't open file")


    # Get version of the b2fstate file

    line    = fid.readline().rstrip()
    version = line[7:17]

    print('read_b2fplasmf -- file version '+version)
    # Expected array sizes, gmtry
    qcdim = [nx+2,ny+2]
    if version >= '03.001.000': qcdim  = [nx+2,ny+2,2]


    # Expected array sizes, state
    fluxdim  = [nx+2,ny+2,2]
    fluxdims = [nx+2,ny+2,2,ns]
# Read basic data, there is more in b2fplasmf, I might grab it if I find out I need it 
# New variables also get added, this might be out of date, check the file if a var is missing
    class plasmfResults:
        def __init__(self):
            # Read gmtry variables

            self.crx  = read_field(fid,'crx' ,[nx+2,ny+2,4])
            self.cry  = read_field(fid,'cry' ,[nx+2,ny+2,4])

            # Read state variables

            self.fch    = read_field(fid,'fch'   ,fluxdim)
            self.fch0   = read_field(fid,'fch0'  ,fluxdim)
            self.fchp   = read_field(fid,'fchp'  ,fluxdim)
            self.fhe    = read_field(fid,'fhe'   ,fluxdim)
            self.fhe0   = read_field(fid,'fhe0'  ,fluxdim)
            self.fhep   = read_field(fid,'fhep'  ,fluxdim)
            self.fhet   = read_field(fid,'fhet'  ,fluxdim)
            self.fhi    = read_field(fid,'fhi'   ,fluxdim)
            self.fhi0   = read_field(fid,'fhi0'  ,fluxdim)
            self.fhip   = read_field(fid,'fhip'  ,fluxdim)
            self.fhit   = read_field(fid,'fhit'  ,fluxdim)
            self.fna    = read_field(fid,'fna'   ,fluxdims)
            self.fna0   = read_field(fid,'fna0'  ,fluxdims)
            self.fnap   = read_field(fid,'fnap'  ,fluxdims)
            self.fne    = read_field(fid,'fne'   ,fluxdim)
            self.fni    = read_field(fid,'fni'   ,fluxdim)
            self.na     = read_field(fid,'na'    ,[nx+2,ny+2,ns])
            self.na0    = read_field(fid,'na0'   ,[nx+2,ny+2,ns])
            self.nap    = read_field(fid,'nap'   ,[nx+2,ny+2,ns])
            self.ne     = read_field(fid,'ne'    ,[nx+2,ny+2])
            self.ne0    = read_field(fid,'ne0'   ,[nx+2,ny+2])
            self.ne2    = read_field(fid,'ne2'   ,[nx+2,ny+2])
            self.nep    = read_field(fid,'nep'   ,[nx+2,ny+2])
            self.ni     = read_field(fid,'ni'    ,[nx+2,ny+2,2])
            self.ni0    = read_field(fid,'ni0'   ,[nx+2,ny+2,2])
            self.pb     = read_field(fid,'pb'    ,[nx+2,ny+2])
            self.po     = read_field(fid,'po'    ,[nx+2,ny+2])
            self.po0    = read_field(fid,'po0'   ,[nx+2,ny+2])
            self.pop    = read_field(fid,'pop'   ,[nx+2,ny+2])
            self.te     = read_field(fid,'te'    ,[nx+2,ny+2])
            self.te0    = read_field(fid,'te0'   ,[nx+2,ny+2])
            self.tep    = read_field(fid,'tep'   ,[nx+2,ny+2])
            self.ti     = read_field(fid,'ti'    ,[nx+2,ny+2])
            self.ti0    = read_field(fid,'ti0'   ,[nx+2,ny+2])
            self.tip    = read_field(fid,'tip'   ,[nx+2,ny+2])
            self.ua     = read_field(fid,'ua'    ,[nx+2,ny+2,ns])
            self.ua0    = read_field(fid,'ua0'   ,[nx+2,ny+2,ns])
            self.uap    = read_field(fid,'uap'   ,[nx+2,ny+2,ns])
            self.uadia  = read_field(fid,'uadia' ,[nx+2,ny+2,2,ns])
            self.fchdia = read_field(fid,'fchdia',fluxdim)
            self.fmo    = read_field(fid,'fmo'   ,fluxdims)
            self.fna_32 = read_field(fid,'fna_32',fluxdims)
            self.fna_52 = read_field(fid,'fna_52',fluxdims)
            self.fni_32 = read_field(fid,'fni_32',fluxdim)
            self.fni_52 = read_field(fid,'fni_52',fluxdim)
            self.fne_32 = read_field(fid,'fne_32',fluxdim)
            self.fne_52 = read_field(fid,'fne_52',fluxdim)
            self.wadia  = read_field(fid,'wadia' ,[nx+2,ny+2,2,ns])
            self.vaecrb = read_field(fid,'vaecrb',[nx+2,ny+2,2,ns])
            self.facdrift     = read_field(fid,'facdrift'    ,[nx+2,ny+2])
            self.fac_ExB      = read_field(fid,'fac_ExB'     ,[nx+2,ny+2])
            self.fchvispar    = read_field(fid,'fchvispar'   ,fluxdim)
            self.fchvisper    = read_field(fid,'fchvisper'   ,fluxdim)
            self.fchin        = read_field(fid,'fchin'       ,fluxdim)
            self.fna_nodrift  = read_field(fid,'fna_nodrift' ,fluxdims)
            self.fac_vis      = read_field(fid,'fac_vis'     ,[nx+2,ny+2])
            self.fna_mdf      = read_field(fid,'fna_mdf'     ,fluxdims)
            self.fhe_mdf      = read_field(fid,'fhe_mdf'     ,fluxdim)
            self.fhi_mdf      = read_field(fid,'fhi_mdf'     ,fluxdim)
            self.fnaPSch      = read_field(fid,'fnaPSch'     ,fluxdims)
            self.fhePSch      = read_field(fid,'fhePSch'     ,fluxdim)
            self.fhiPSch      = read_field(fid,'fhiPSch'     ,fluxdim)
            self.fna_fcor     = read_field(fid,'fna_fcor'    ,fluxdims)
            self.fna_he       = read_field(fid,'fna_he'      ,fluxdims)
            self.fchvisq      = read_field(fid,'fchvisq'     ,fluxdim)
            self.fchinert     = read_field(fid,'fchinert'    ,fluxdim)
            if version>'3.000.006' or (version[0]=='0' and version[1:]>'3.000.006'):
              # these are only present in 3.000.007 and beyond
              self.fht          = read_field(fid,'fht'         ,fluxdim)
              self.fhj          = read_field(fid,'fhj'         ,fluxdim)
              self.fhm          = read_field(fid,'fhm'         ,fluxdims)
              self.fhp          = read_field(fid,'fhp'         ,fluxdims)
            self.resco        = read_field(fid,'resco'       ,[nx+2,ny+2,ns])
            self.reshe        = read_field(fid,'reshe'       ,[nx+2,ny+2])
            self.reshi        = read_field(fid,'reshi'       ,[nx+2,ny+2])
            self.resmo        = read_field(fid,'resmo'       ,[nx+2,ny+2,ns])
            self.resmt        = read_field(fid,'resmt'       ,[nx+2,ny+2])
            self.respo        = read_field(fid,'respo'       ,[nx+2,ny+2])
            self.sch          = read_field(fid,'sch'         ,[nx+2,ny+2,4])
            self.she          = read_field(fid,'she'         ,[nx+2,ny+2,4])
            self.shi          = read_field(fid,'shi'         ,[nx+2,ny+2,4])
            self.smo          = read_field(fid,'smo'         ,[nx+2,ny+2,4,ns])
            self.smq          = read_field(fid,'smq'         ,[nx+2,ny+2,4,ns])
            self.sna          = read_field(fid,'sna'         ,[nx+2,ny+2,2,ns])
            self.sne          = read_field(fid,'sne'         ,[nx+2,ny+2,2])
            self.rsana        = read_field(fid,'rsana'       ,[nx+2,ny+2,ns])
            self.rsahi        = read_field(fid,'rsahi'       ,[nx+2,ny+2,ns])
            self.rsamo        = read_field(fid,'rsamo'       ,[nx+2,ny+2,ns])
            self.rrana        = read_field(fid,'rrana'       ,[nx+2,ny+2,ns])
            self.rrahi        = read_field(fid,'rrahi'       ,[nx+2,ny+2,ns])
            self.rramo        = read_field(fid,'rramo'       ,[nx+2,ny+2,ns])
            self.rqahe        = read_field(fid,'rqahe'       ,[nx+2,ny+2,ns])
            self.rqrad        = read_field(fid,'rqrad'       ,[nx+2,ny+2,ns])
            self.rqbrm        = read_field(fid,'rqbrm'       ,[nx+2,ny+2,ns])
            self.rcxna        = read_field(fid,'rcxna'       ,[nx+2,ny+2,ns])
            self.rcxhi        = read_field(fid,'rcxhi'       ,[nx+2,ny+2,ns])
            self.rcxmo        = read_field(fid,'rcxmo'       ,[nx+2,ny+2,ns])
            self.b2stbr_sna   = read_field(fid,'b2stbr_sna'  ,[nx+2,ny+2,ns])
            self.b2stbr_smo   = read_field(fid,'b2stbr_smo'  ,[nx+2,ny+2,ns])
            self.b2stbr_she   = read_field(fid,'b2stbr_she'  ,[nx+2,ny+2])
            self.b2stbr_shi   = read_field(fid,'b2stbr_shi'  ,[nx+2,ny+2])
            self.b2stbr_sch   = read_field(fid,'b2stbr_sch'  ,[nx+2,ny+2])
            self.b2stbr_sne   = read_field(fid,'b2stbr_sne'  ,[nx+2,ny+2])
            self.b2stbc_sna   = read_field(fid,'b2stbc_sna'  ,[nx+2,ny+2,ns])
            self.b2stbc_smo   = read_field(fid,'b2stbc_smo'  ,[nx+2,ny+2,ns])
            self.b2stbc_she   = read_field(fid,'b2stbc_she'  ,[nx+2,ny+2])
            self.b2stbc_shi   = read_field(fid,'b2stbc_shi'  ,[nx+2,ny+2])
            self.b2stbc_sch   = read_field(fid,'b2stbc_sch'  ,[nx+2,ny+2])
            self.b2stbc_sne   = read_field(fid,'b2stbc_sne'  ,[nx+2,ny+2])
            self.b2stbm_sna   = read_field(fid,'b2stbm_sna'  ,[nx+2,ny+2,ns])
            self.b2stbm_smo   = read_field(fid,'b2stbm_smo'  ,[nx+2,ny+2,ns])
            self.b2stbm_she   = read_field(fid,'b2stbm_she'  ,[nx+2,ny+2])
            self.b2stbm_shi   = read_field(fid,'b2stbm_shi'  ,[nx+2,ny+2])
            self.b2stbm_sch   = read_field(fid,'b2stbm_sch'  ,[nx+2,ny+2])
            self.b2stbm_sne   = read_field(fid,'b2stbm_sne'  ,[nx+2,ny+2])
            self.b2sihs_divue = read_field(fid,'b2sihs_divue',[nx+2,ny+2])
            self.b2sihs_divua = read_field(fid,'b2sihs_divua',[nx+2,ny+2])
            self.b2sihs_exbe  = read_field(fid,'b2sihs_exbe' ,[nx+2,ny+2])
            self.b2sihs_exba  = read_field(fid,'b2sihs_exba' ,[nx+2,ny+2])
            self.b2sihs_visa  = read_field(fid,'b2sihs_visa' ,[nx+2,ny+2])
            self.b2sihs_joule = read_field(fid,'b2sihs_joule',[nx+2,ny+2])
            self.b2sihs_fraa  = read_field(fid,'b2sihs_fraa' ,[nx+2,ny+2])
            self.b2sihs_str   = read_field(fid,'b2sihs_str' ,[nx+2,ny+2])
            self.b2npmo_smaf  = read_field(fid,'b2npmo_smaf' ,[nx+2,ny+2,4,ns])
            self.b2npmo_smag  = read_field(fid,'b2npmo_smag' ,[nx+2,ny+2,4,ns])
            self.b2npmo_smav  = read_field(fid,'b2npmo_smav' ,[nx+2,ny+2,4,ns])
            self.smpr         = read_field(fid,'smpr'        ,[nx+2,ny+2,ns])
            self.smpt         = read_field(fid,'smpt'        ,[nx+2,ny+2,ns])
            self.smfr         = read_field(fid,'smfr'        ,[nx+2,ny+2,ns])
            self.smcf         = read_field(fid,'smcf'        ,[nx+2,ny+2,ns])
            self.ext_sna      = read_field(fid,'ext_sna'     ,[nx+2,ny+2,ns])
            self.ext_smo      = read_field(fid,'ext_smo'     ,[nx+2,ny+2,ns])
            self.ext_she      = read_field(fid,'ext_she'     ,[nx+2,ny+2])
            self.ext_shi      = read_field(fid,'ext_shi'     ,[nx+2,ny+2])
            self.ext_sch      = read_field(fid,'ext_sch'     ,[nx+2,ny+2])
            self.ext_sne      = read_field(fid,'ext_sne'     ,[nx+2,ny+2])
            self.calf         = read_field(fid,'calf'        ,fluxdim)
            self.cdna         = read_field(fid,'cdna'        ,fluxdims)
            self.cdpa         = read_field(fid,'cdpa'        ,fluxdims)
            self.ceqp         = read_field(fid,'ceqp'        ,[nx+2,ny+2])
            self.chce         = read_field(fid,'chce'        ,fluxdim)
            self.chci         = read_field(fid,'chci'        ,fluxdim)
            self.chve         = read_field(fid,'chve'        ,fluxdim)
            self.chvemx       = read_field(fid,'chvemx'      ,[nx+2,ny+2])
            self.chvi         = read_field(fid,'chvi'        ,fluxdim)
            self.chvimx       = read_field(fid,'chvimx'      ,[nx+2,ny+2])
            self.csig         = read_field(fid,'csig'        ,fluxdim)
            self.cvla         = read_field(fid,'cvla'        ,fluxdims)
            self.cvsa         = read_field(fid,'cvsa'        ,fluxdims)
            self.cthe         = read_field(fid,'cthe'        ,[nx+2,ny+2,ns])
            self.cthi         = read_field(fid,'cthi'        ,[nx+2,ny+2,ns])
            self.csigin       = read_field(fid,'csigin'      ,[fluxdims[0],fluxdims[1],fluxdims[2],fluxdims[3],ns])
            self.cvsa_cl      = read_field(fid,'cvsa_cl'     ,fluxdims)
            self.fllime       = read_field(fid,'fllime'      ,[nx+2,ny+2])
            self.fllimi       = read_field(fid,'fllimi'      ,[nx+2,ny+2])
            self.fllim0fna    = read_field(fid,'fllim0fna'   ,fluxdims)
            self.fllim0fhi    = read_field(fid,'fllim0fhi'   ,fluxdims)
            self.fllimvisc    = read_field(fid,'fllimvisc'   ,[nx+2,ny+2,ns])
            self.sig0         = read_field(fid,'sig0'        ,[nx+2,ny+2])
            self.hce0         = read_field(fid,'hce0'        ,[nx+2,ny+2])
            self.alf0         = read_field(fid,'alf0'        ,[nx+2,ny+2])
            self.hci0         = read_field(fid,'hci0'        ,[nx+2,ny+2])
            self.hcib         = read_field(fid,'hcib'        ,[nx+2,ny+2,ns])
            self.dpa0         = read_field(fid,'dpa0'        ,[nx+2,ny+2,ns])
            self.dna0         = read_field(fid,'dna0'        ,[nx+2,ny+2,ns])
            self.vsa0         = read_field(fid,'vsa0'        ,[nx+2,ny+2,ns])
            self.vla0         = read_field(fid,'vla0'        ,[nx+2,ny+2,2,ns])
            self.csig_an      = read_field(fid,'csig_an'     ,fluxdim)
            self.calf_an      = read_field(fid,'calf_an'     ,fluxdim)
            nstra              = read_field(fid,'nstra'       ,[1],True)
            if nstra!=0:
              self.sclstra      = read_field(fid,'sclstra'     ,[ns+1,nstra[0]])
              self.sclrtio      = read_field(fid,'sclrtio'     ,[ns+1,nstra[0]])
    plasmf = plasmfResults()
    fid.close()
    print('done reading b2fplasmf')
    return plasmf


def read_ft44(fileName):
#
# Read fort.44 file
#
# For now
# - only fort.44 version 20081111 recognized
# - assuming nfla = 1 until a better fix 
# - assuming nlwrmsh = 1 until a better fix
#

    print('read_ft44: assuming nlwrmsh = 1, nfla = 1.')
    nlwrmsh = 1
    nfla = 1

    fid = open(fileName)
    if (fid == -1): print("read_ft44: can't open file")

# Read dimensions

# nx, ny, version
    dims = fid.readline().rstrip().split()
    nx = int(dims[0])
    ny = int(dims[1])
    ver = int(dims[2])

    if (ver != 20081111 and ver != 20160829 and ver != 20170328):
        print('read_ft44: unknown format of fort.44 file (this is usually fine)')

# go to new line (skip reading a possible git-hash)
#     fid.readline().rstrip()

# natm, nmol, nion
    dims = fid.readline().rstrip().split()
    natm = int(dims[0])
    nmol = int(dims[1])
    nion = int(dims[2])
# for now, ignore reading species labels

    for i in range(natm): line = fid.readline().rstrip()
    for i in range(nmol): line = fid.readline().rstrip()
    for i in range(nion): line = fid.readline().rstrip()

# Read basic data, there is more, I might grab it if I find out I need it
    class ft44Results:
        def __init__(self):
            self.dab2     = read_ft44_field(fid,ver,'dab2',[nx,ny,natm]);
            self.tab2     = read_ft44_field(fid,ver,'tab2',[nx,ny,natm]);
            self.dmb2     = read_ft44_field(fid,ver,'dmb2',[nx,ny,nmol]);
            self.tmb2     = read_ft44_field(fid,ver,'tmb2',[nx,ny,nmol]);
            self.dib2     = read_ft44_field(fid,ver,'dib2',[nx,ny,nion]);
            self.tib2     = read_ft44_field(fid,ver,'tib2',[nx,ny,nion]);
            self.rfluxa   = read_ft44_field(fid,ver,'rfluxa',[nx,ny,natm]);
            self.rfluxm   = read_ft44_field(fid,ver,'rfluxm',[nx,ny,nmol]);
            self.pfluxa   = read_ft44_field(fid,ver,'pfluxa',[nx,ny,natm]);
            self.pfluxm   = read_ft44_field(fid,ver,'pfluxm',[nx,ny,nmol]);
            self.refluxa  = read_ft44_field(fid,ver,'refluxa',[nx,ny,natm]);
            self.refluxm  = read_ft44_field(fid,ver,'refluxm',[nx,ny,nmol]);
            self.pefluxa  = read_ft44_field(fid,ver,'pefluxa',[nx,ny,natm]);
            self.pefluxm  = read_ft44_field(fid,ver,'pefluxm',[nx,ny,nmol]);
            self.emiss    = read_ft44_field(fid,ver,'emiss',[nx,ny,1]);
            self.emissmol = read_ft44_field(fid,ver,'emissmol',[nx,ny,1]);
            self.srcml    = read_ft44_field(fid,ver,'srcml',[nx,ny,nmol]);
            self.edissml  = read_ft44_field(fid,ver,'edissml',[nx,ny,nmol]);
            [wallN,someNumber,istra] = fid.readline().split()
            wldna = []
            ewlda = []
            wldnm = []
            ewldm = []
            wldnek = []
            wldnep = []
            wldra = []
            wldrm = []
            wldnek.append(read_ft44_field(fid,ver,'wldnek(0)',[-1]))
            wldnep.append(read_ft44_field(fid,ver,'wldnep(0)',[-1]))
            wldna.append(read_ft44_field(fid,ver,'wldna(0)',[natm,-1]))
            ewlda.append(read_ft44_field(fid,ver,'ewlda(0)',[natm,-1]))
            wldnm.append(read_ft44_field(fid,ver,'wldnm(0)',[nmol,-1]))
            ewldm.append(read_ft44_field(fid,ver,'ewldm(0)',[nmol,-1]))
            self.wall_geometry = read_ft44_field(fid,ver,'wall_geometry',[620])
            wldra.append(read_ft44_field(fid,ver,'wldra(0)',[natm,-1]))
            wldrm.append(read_ft44_field(fid,ver,'wldrm(0)',[nmol,-1]))
            for i in range(1,int(istra)+1):
                if i<10:
                    wldnek.append(read_ft44_field(fid,ver,'wldnek(  '+str(i)+')',[-1]))
                    wldnep.append(read_ft44_field(fid,ver,'wldnep(  '+str(i)+')',[-1]))
                    wldna.append(read_ft44_field(fid,ver,'wldna(  '+str(i)+')',[natm,-1]))
                    ewlda.append(read_ft44_field(fid,ver,'ewlda(  '+str(i)+')',[natm,-1]))
                    wldnm.append(read_ft44_field(fid,ver,'wldnm(  '+str(i)+')',[nmol,-1]))
                    ewldm.append(read_ft44_field(fid,ver,'ewldm(  '+str(i)+')',[nmol,-1]))
                    wldra.append(read_ft44_field(fid,ver,'wldra(  '+str(i)+')',[natm,-1]))
                    wldrm.append(read_ft44_field(fid,ver,'wldrm(  '+str(i)+')',[nmol,-1]))
                else:
                    wldnek.append(read_ft44_field(fid,ver,'wldnek( '+str(i)+')',[-1]))
                    wldnep.append(read_ft44_field(fid,ver,'wldnep( '+str(i)+')',[-1]))
                    wldna.append(read_ft44_field(fid,ver,'wldna( '+str(i)+')',[natm,-1]))
                    ewlda.append(read_ft44_field(fid,ver,'ewlda( '+str(i)+')',[natm,-1]))
                    wldnm.append(read_ft44_field(fid,ver,'wldnm( '+str(i)+')',[nmol,-1]))
                    ewldm.append(read_ft44_field(fid,ver,'ewldm( '+str(i)+')',[nmol,-1]))
                    wldra.append(read_ft44_field(fid,ver,'wldra( '+str(i)+')',[natm,-1]))
                    wldrm.append(read_ft44_field(fid,ver,'wldrm( '+str(i)+')',[nmol,-1]))
            self.wldna    = np.array(wldna)
            self.ewlda    = np.array(ewlda)
            self.wldnm    = np.array(wldnm)
            self.ewldm    = np.array(ewldm)
            self.wldnek   = np.array(wldnek)
            self.wldnep   = np.array(wldnep)
            self.wldra    = np.array(wldra)
            self.wldrm    = np.array(wldrm)
            wldpeb = []
            wldpeb.append(read_ft44_field(fid,ver,'wldpeb(0)',[-1]))
            for i in range(1,int(istra)+1):
                if i<10:
                    wldpeb.append(read_ft44_field(fid,ver,'wldpeb(  '+str(i)+')',[-1]))
                else:
                    wldpeb.append(read_ft44_field(fid,ver,'wldpeb( '+str(i)+')',[-1]))
            self.wldpeb   = np.array(wldpeb)
            self.wlarea   = read_ft44_field(fid,ver,'wlarea',[168])
#            self.wldspt0   = read_ft44_field(fid,ver,'wldspt(0)',[natm,-1])
#            self.wldspt1   = read_ft44_field(fid,ver,'wldspt(  1)',[natm,-1])
#            self.wldspt2   = read_ft44_field(fid,ver,'wldspt(  2)',[natm,-1])
#            self.wldspt3   = read_ft44_field(fid,ver,'wldspt(  3)',[natm,-1])
#            self.wldspt4   = read_ft44_field(fid,ver,'wldspt(  4)',[natm,-1])
#            self.wldspt5   = read_ft44_field(fid,ver,'wldspt(  5)',[natm,-1])
#            self.wldspt6   = read_ft44_field(fid,ver,'wldspt(  6)',[natm,-1])
 #           self.wlpumpA   = read_ft44_field(fid,ver,'wlpump(A)',[natm,88])
 #           self.wlpumpM   = read_ft44_field(fid,ver,'wlpump(M)',[nmol,88])
            self.eneutrad  = read_ft44_field(fid,ver,'eneutrad',[nx,ny,natm])
            self.emolrad  = read_ft44_field(fid,ver,'emolrad',[nx,ny,nmol])
            self.eionrad  = read_ft44_field(fid,ver,'eionrad',[nx,ny,nion]) 
    ft44 = ft44Results()
    fid.close()
    print('done reading ft44 file')
    return ft44

def read_ft46(fileName):
    # ft46 = read_ft46(file)
    #
    # Read fort.46 file. Convert to SI units.
    #
    # For now, only fort.46 version 20160513 recognized 
    #

    fid = open(fileName)
    if (fid == -1): print("read_ft44: can't open file")

    # Read dimensions

    # ntri, version, avoid reading git-hash
    line = fid.readline().rstrip().split()
    ntri = int(line[0])
    ver  = int(line[1])

    if ver != 20160513 and ver != 20160829 and ver != 20170930:
        print('read_ft46: unknown format of fort.46 file')

    # natm, nmol, nion
    dims = fid.readline().rstrip().split()
    natm = int(dims[0])
    nmol = int(dims[1])
    nion = int(dims[2])

    # for now, ignore reading species labels
    for i in range(natm): fid.readline().rstrip()
    for i in range(nmol): fid.readline().rstrip()
    for i in range(nion): fid.readline().rstrip()

    eV   = 1.6021765650000000E-019
    # Read data
    class ft46Results:
        def __init__(self):
            self.pdena  = read_ft44_field(fid,ver,'pdena',[ntri,natm])*1e6# m^{-3}
            self.pdenm  = read_ft44_field(fid,ver,'pdenm',[ntri,nmol])*1e6
            self.pdeni  = read_ft44_field(fid,ver,'pdeni',[ntri,nion])*1e6
            
            self.edena  = read_ft44_field(fid,ver,'edena',[ntri,natm])*1e6*eV# J m^{-3}
            self.edenm  = read_ft44_field(fid,ver,'edenm',[ntri,nmol])*1e6*eV
            self.edeni  = read_ft44_field(fid,ver,'edeni',[ntri,nion])*1e6*eV

            self.vxdena = read_ft44_field(fid,ver,'vxdena',[ntri,natm])*1e1# kg s^{-1} m^{-2}
            self.vxdenm = read_ft44_field(fid,ver,'vxdenm',[ntri,nmol])*1e1
            self.vxdeni = read_ft44_field(fid,ver,'vxdeni',[ntri,nion])*1e1

            self.vydena = read_ft44_field(fid,ver,'vydena',[ntri,natm])*1e1# kg s^{-1} m^{-2}
            self.vydenm = read_ft44_field(fid,ver,'vydenm',[ntri,nmol])*1e1
            self.vydeni = read_ft44_field(fid,ver,'vydeni',[ntri,nion])*1e1

            self.vzdena = read_ft44_field(fid,ver,'vzdena',[ntri,natm])*1e1# kg s^{-1} m^{-2}
            self.vzdenm = read_ft44_field(fid,ver,'vzdenm',[ntri,nmol])*1e1
            self.vzdeni = read_ft44_field(fid,ver,'vzdeni',[ntri,nion])*1e1
            self.vol =    read_ft44_field(fid,ver,'volumes',[ntri])
            self.pux    = read_ft44_field(fid,ver,'pux',[ntri])
            self.puy    = read_ft44_field(fid,ver,'puy',[ntri])
            
    ft46 = ft46Results()
    # Close file
    fid.close()
    print('done reading ft46 file')
    return ft46

def read_ft33(fileName):
    #
    # Read fort.33-files (triangle nodes). Converts to SI units (m).
    #
    #

    fid = open(fileName);
    if (fid == -1): print("can't open fort.33 file")

    print('read_ft33: assuming ntrfrm = 0.')
    ntrfrm = 0


    # Read coordinates

    # number of nodes
    nnodes = int(fid.readline().rstrip())
    nodes  = [[],[]]

    if (ntrfrm==0):
            for line in fid:
                for j in range(len(line.split())):
                    nodes[0].append(float(line.split()[j]))
                if len(nodes[0])>=nnodes: break
            for line in fid:
                for j in range(len(line.split())):
                    nodes[1].append(float(line.split()[j]))
                if len(nodes[1])>=nnodes: break

    else: print('read_ft33: wrong ntrfrm.')

    # Convert from cm to m
    nodes = np.array(nodes)*1e-2
    # close file
    fid.close()
    return nodes

def read_ft34(fileName):
    # cells = read_ft34(file)
    #
    # Read fort.34-files (nodes composing each triangle). 
    #

    fid = open(fileName)
    if (fid == -1): print("can't open fort.34 file")



    # Read data

    # number of triangels
    ntria = int(fid.readline().rstrip())

    cells = [[],[],[]]
    
    for i in range(ntria):
        line = fid.readline().rstrip().split()
        cells[0].append(int(line[1]))
        cells[1].append(int(line[2]))
        cells[2].append(int(line[3]))
    
    # close file
    fid.close()
    return cells

def read_ft35(fileName):
    # links = read_ft35(file)
    #
    # Read fort.35-files (triangle data). 
    #

    fid = open(fileName)
    if (fid == -1): print("can't open fort.34 file")

    # Read data

    # number of triangles
    ntria = int(fid.readline().rstrip())
    
    class ft35Results():
        def __init__(self):
            self.nghbr = np.zeros([ntria,3]);
            self.side  = np.zeros([ntria,3]);
            self.cont  = np.zeros([ntria,3]);
            self.ixiy  = np.zeros([ntria,2]);

            for i in range (ntria):
                data = fid.readline().rstrip().split()
                data = [int(i) for i in data]
                self.nghbr[i,:] = data[1::3][0:3]
                self.side[i,:]  = data[2::3][0:3]
                self.cont[i,:]  = data[3::3]
                self.ixiy[i,:]  = data[10:12]
    links=ft35Results()
    # close file
    fid.close()
    return links

def read_triangle_mesh(fort33fn,fort34fn,fort35fn):
    # triangles = read_triangle_mesh(fort33,fort34,fort35)
    #
    # Wrapper routine to read all triangle data at once.
    #
    # Returns nodes, cells, nghbr, side and cont as fields of triangles-struct.
    #
    
    class triangleResults:
        def __init__(self):
            self.nodes = np.array(read_ft33(fort33fn))#list of 
            self.cells = np.array(read_ft34(fort34fn))
            centroidsX  = []
            centroidsY  = []
            nodeXs      = []
            nodeYs      = []
            for i in range(np.shape(self.cells)[1]):#loop through every triangle
                cntrX=0
                cntrY=0
                nodeX=[]
                nodeY=[]
                for j in range(3):#loop through each node on each triangle
                    cntrX=cntrX+self.nodes[:,self.cells[:,i][j]-1][0]
                    nodeX.append(self.nodes[:,self.cells[:,i][j]-1][0])
                    cntrY=cntrY+self.nodes[:,self.cells[:,i][j]-1][1]
                    nodeY.append(self.nodes[:,self.cells[:,i][j]-1][1])
                cntrX=cntrX/3#calculate centroid of triangle
                cntrY=cntrY/3
                nodeXs.append(nodeX)
                nodeYs.append(nodeY)
                centroidsX.append(cntrX)#make list of triangle centroid x-coordinate
                centroidsY.append(cntrY)#make list of triangle centroid y-coordinate
            self.nodeXs = np.array(nodeXs)
            self.nodeYs = np.array(nodeYs)
            self.triaX = np.array(centroidsX)
            self.triaY = np.array(centroidsY)
            links      = read_ft35(fort35fn)

            self.nghbr = links.nghbr
            self.side  = links.side
            self.cont  = links.cont
            self.ixiy  = links.ixiy
    triangles=triangleResults()
    return triangles

def readB2Plot(fileLoc):
#   reads the resulting file of writes within b2plot commands and returns array
#   idx 0 is computational index
#   idx 1 is R-Rsep
#   idx 2 is value from b2plot
    fid = open(fileLoc)
    title = fid.readline().rstrip()
    line  = fid.readline().rstrip().split()
    dataList =[[],[],[]]
    while (is_number(line[0])):
        dataList[1].append(float(line[0]))
        dataList[2].append(float(line[1]))
        line = fid.readline().rstrip().split()
    line = fid.readline().rstrip().split()
    while (is_number(line[0])):
        dataList[0].append(float(line[0]))
        line = fid.readline().rstrip().split()
        if not line: break
    fid.close()
    return np.array(dataList)

def readB2transportFile(caseDir):
# reads b2.transport.inputfile and puts the data into an array
# makes a few assumptions about how things are organized
# assumes only Dn, chiI, and chiE are specified
# use with caution
    fid = open(caseDir+'b2.transport.inputfile')
    line = fid.readline().rstrip().split()
    Dn=[]
    chiE=[]
    chiI=[]
    R=[]
    while (len(line)>0):
        line = fid.readline().rstrip().split()
        if ('addspec(' in line): continue
        if (['no_pflux=.true.']==line): break
        if (line==['/']): break
        if ('ndata(' in line):
            if (int(line[3])==1):
                DnVals=True
                chiIvals=False
                chiEvals=False
            if (int(line[3])==3):
                chiIvals=True
                DnVals=False
                chiEvals=False
            if (int(line[3])==4):
                chiEvals=True
                DnVals=False
                chiIvals=False
            line = fid.readline().rstrip().split()
        if (DnVals):
            Dn.append(float(line[-2]))
            R.append(float(line[9]))
        if (chiEvals):
            chiE.append(float(line[-2]))
        if (chiIvals):
            chiI.append(float(line[-2]))
    return [R,Dn,chiE,chiI]

def read_tally_field(fid,fieldname):
#   parses a line of display.tallies which is the result of display_tallies L > display.tallies
    line = fid.readline().rstrip()
    while fieldname not in line: line = fid.readline().rstrip()
    line = fid.readline().rstrip()
    data=[]
    while line:
        if is_number(line.split()[0]): data.append(np.array(line.split()).astype(np.float))
        else: data.append(np.array(line.split()[1:]).astype(np.float))
        line = fid.readline().rstrip()
    if np.shape(data)[0]==1: data=data[0]
    return np.array(data)

def readTallyDisplay(fileLoc):
# reads display.tallies which is the result of display_tallies L > display.tallies
# returns class with all the display_tallies results
    fid = open(fileLoc)
    line = fid.readline().rstrip()
    while 'ITER' not in line: line = fid.readline().rstrip()
    class tallyResults:
        def __init__(self):
            self.rsanareg       = read_tally_field(fid,'rsanareg')
            self.rsahireg       = read_tally_field(fid,'rsahireg')
            self.rsamoreg       = read_tally_field(fid,'rsamoreg')
            self.rranareg       = read_tally_field(fid,'rranareg')
            self.rrahireg       = read_tally_field(fid,'rrahireg')
            self.rramoreg       = read_tally_field(fid,'rramoreg')
            self.rqahereg       = read_tally_field(fid,'rqahereg')
#            self.rqradreg       = read_tally_field(fid,'rqradreg')
#            self.rqbrmreg       = read_tally_field(fid,'rqbrmreg')
            self.rcxnareg       = read_tally_field(fid,'rcxnareg')
            self.rcxhireg       = read_tally_field(fid,'rcxhireg')
            self.rcxmoreg       = read_tally_field(fid,'rcxmoreg')
            self.fnaxreg        = read_tally_field(fid,'fnaxreg')
            self.fnayreg        = read_tally_field(fid,'fnayreg')
            self.fhixreg        = read_tally_field(fid,'fhixreg')
            self.fhiyreg        = read_tally_field(fid,'fhiyreg')
            self.fhexreg        = read_tally_field(fid,'fhexreg')
            self.fheyreg        = read_tally_field(fid,'fheyreg')
            self.fhpxreg        = read_tally_field(fid,'fhpxreg')
            self.fhpyreg        = read_tally_field(fid,'fhpyreg')
            self.fhmxreg        = read_tally_field(fid,'fhmxreg')
            self.fhmyreg        = read_tally_field(fid,'fhmyreg')
            self.fchxreg        = read_tally_field(fid,'fchxreg')
            self.fchyreg        = read_tally_field(fid,'fchyreg')
            self.fhtxreg        = read_tally_field(fid,'fhtxreg')
            self.fhtyreg        = read_tally_field(fid,'fhtyreg')
            self.fhjxreg        = read_tally_field(fid,'fhjxreg')
            self.fhjyreg        = read_tally_field(fid,'fhjyreg')
#            self.qconvixreg     = read_tally_field(fid,'qconvixreg')
#            self.qconviyreg     = read_tally_field(fid,'qconviyreg')
#            self.qconvexreg     = read_tally_field(fid,'qconvexreg')
#            self.qconveyreg     = read_tally_field(fid,'qconveyreg')
            self.b2stbr_sna_reg = read_tally_field(fid,'b2stbr_sna_reg')
#            self.b2stbr_sne_reg = read_tally_field(fid,'b2stbr_sne_reg')
            self.b2stbr_she_reg = read_tally_field(fid,'b2stbr_she_reg')
            self.b2stbr_shi_reg = read_tally_field(fid,'b2stbr_shi_reg')
            self.b2stbr_sch_reg = read_tally_field(fid,'b2stbr_sch_reg')
            self.b2stbc_sna_reg = read_tally_field(fid,'b2stbc_sna_reg')
            self.b2stbc_she_reg = read_tally_field(fid,'b2stbc_she_reg')
            self.b2stbc_shi_reg = read_tally_field(fid,'b2stbc_shi_reg')
            self.b2stbm_she_reg = read_tally_field(fid,'b2stbm_she_reg')
            self.b2stbm_shi_reg = read_tally_field(fid,'b2stbm_shi_reg')
            self.nareg          = read_tally_field(fid,'nareg')
            self.tereg          = read_tally_field(fid,'tereg')
            self.nereg          = read_tally_field(fid,'nereg')
            self.ne2reg         = read_tally_field(fid,'ne2reg')
            self.tireg          = read_tally_field(fid,'tireg')
            self.nireg          = read_tally_field(fid,'nireg')
            self.poreg          = read_tally_field(fid,'poreg')
            self.volreg         = read_tally_field(fid,'volreg')
            self.b2brem         = read_tally_field(fid,'b2brem')
            self.b2rad          = read_tally_field(fid,'b2rad')
            self.b2qie          = read_tally_field(fid,'b2qie')
            self.b2vdp          = read_tally_field(fid,'b2vdp')
            self.b2divue        = read_tally_field(fid,'b2divue')
            self.b2divua        = read_tally_field(fid,'b2divua')
            self.b2exbe         = read_tally_field(fid,'b2exbe')
            self.b2exba         = read_tally_field(fid,'b2exba')
            self.b2visa         = read_tally_field(fid,'b2visa')
            self.b2joule        = read_tally_field(fid,'b2joule')
            self.b2fraa         = read_tally_field(fid,'b2fraa')
            self.b2she          = read_tally_field(fid,'b2she')
            self.b2shi          = read_tally_field(fid,'b2shi')
            self.b2she0         = read_tally_field(fid,'b2she0')
            self.b2shi0         = read_tally_field(fid,'b2shi0')
            self.rdneureg       = read_tally_field(fid,'rdneureg')
    tally = tallyResults()
    print('finished reading tallies')
    return tally

def read_ld_tg(fileLoc):
    fid = open(fileLoc)
    line = fid.readline().rstrip()
    x     = []
    ne    = []
    te    = []
    ti    = []
    wtot  = []
    wpart = []
    wrad  = []
    wpls  = []
    wneut = []
    wheat = []
    wpot  = []
    whtpl = []
    wptpl = []
    xmp   = []
    rclfc = []
    zclfc = []
    wpar_xpt = []
    wwpar = []
    wwtrg = []
    lcnnt = []
    lcnnx = []
    j=0
    while len(line)!=0:
        line = fid.readline().rstrip().split()
#        print(j)
#        j+=1
#        print(line)
        if len(line)==0: break
        if '#' in line: continue
        x.append(float(line[0]))
        ne.append(float(line[1]))
        te.append(float(line[2]))
        ti.append(float(line[3]))
        wtot.append(float(line[4]))
        wpart.append(float(line[5]))
        wrad.append(float(line[6]))
        wpls.append(float(line[7]))
        wneut.append(float(line[8]))
        wheat.append(float(line[9]))
        wpot.append(float(line[10]))
        whtpl.append(float(line[11]))
        wptpl.append(float(line[12]))
        xmp.append(float(line[13]))
        rclfc.append(float(line[14]))
        zclfc.append(float(line[15]))
        wpar_xpt.append(float(line[16]))
        wwpar.append(float(line[17]))
        wwtrg.append(float(line[18]))
        lcnnt.append(float(line[19]))
        lcnnx.append(float(line[20]))
    class ldResults:
        def __init__(self):
            self.x        = np.array(x)
            self.ne       = np.array(ne)
            self.te       = np.array(te)
            self.ti       = np.array(ti)
            self.wtot     = np.array(wtot)
            self.wpart    = np.array(wpart)
            self.wrad     = np.array(wrad)
            self.wpls     = np.array(wpls)
            self.wneut    = np.array(wneut)
            self.wheat    = np.array(wheat)
            self.wpot     = np.array(wpot)
            self.whtpl    = np.array(whtpl)
            self.wptpl    = np.array(wptpl)
            self.xmp      = np.array(xmp)
            self.rclfc    = np.array(rclfc)
            self.zclfc    = np.array(zclfc)
            self.wpar_xpt = np.array(wpar_xpt)
            self.wwpar    = np.array(wwpar)
            self.wwtrg    = np.array(wwtrg)
            self.lcnnt    = np.array(lcnnt)
            self.lcnnx    = np.array(lcnnx)
    ld = ldResults()
    print('finished reading ld file')
    return ld
def fmt(x, pos):
# formatting function
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

def read_input(inputFile):
# reads the input file of SOLPS and gets the eirene wall number and the divgeo wall number
# and pairs with the (R,Z) for each end point of the wall
# for the non-additional surfaces it tries to find the wall points associated with it
# and gives the non-additional surfaces those wall end points
# output is of the following form:
#surfaces[0] is the eirene wall number (first number in input.dat)
#surfaces[1] is the divgeo wall number (second number in input.dat)
#surfaces[2] is R1
#surfaces[3] is Z1
#surfaces[4] is R2
#surfaces[5] is Z2
    fid = open(inputFile)
    line=fid.readline().rstrip().split()
    additional=False
    surfaces=[]
    innerTargWalls = []
    outerTargWalls = []
    while 'atomic' not in line:
        line=fid.readline().rstrip().split()
        #mark non-additional surfaces (PFR, Targets, SOL, etc.)
        if ':' in line and not additional:
#            print(line[1])
            surfaces.append([int(line[1])*-1,int(line[1])*-1,1.0000,1.0000,1.000,1.000])#line[3]])
            if int(line[1])==3: innerTargIdx = len(surfaces)-1
            if int(line[1])==6: outerTargIdx = len(surfaces)-1
            if int(line[1])==14: outerTarg2ndIdx = len(surfaces)-1
        #now it goes through the additional surfaces (actual walls)
        elif ':' in line and additional:
            fid.readline().rstrip().split()
            fid.readline().rstrip().split()
            geoLine = fid.readline().rstrip()
            #The following if statements try to find the walls associated with the non-additional surfaces
            if len(innerTargWalls)>0:
                if (int(line[3])==innerTargWalls[0]):
                    surfaces[innerTargIdx][2] = float(geoLine[0:12])
                    surfaces[innerTargIdx][3] = float(geoLine[12:24])
                elif (int(line[3])==innerTargWalls[-1]):
                    surfaces[innerTargIdx][4] = float(geoLine[36:48])
                    surfaces[innerTargIdx][5] = float(geoLine[48:60])
            if len(outerTargWalls)>0:
                if (int(line[3])==outerTargWalls[0]):
                    surfaces[outerTargIdx][2] = float(geoLine[0:12])
                    surfaces[outerTargIdx][3] = float(geoLine[12:24])
                elif (int(line[3])==outerTargWalls[-1]):
                    surfaces[outerTargIdx][4] = float(geoLine[36:48])
                    surfaces[outerTargIdx][5] = float(geoLine[48:60])
            #This actually writes down the geo information
            surfaces.append([int(line[1]),int(line[3]),float(geoLine[0:12]),float(geoLine[12:24]),float(geoLine[36:48]),float(geoLine[48:60])])
        #This tells the code that we are switching to the additional surfaces
        if '3b.' in line:
            additional=True
    return np.array(surfaces)

def plotvar(xPts, yPts, var,minColor='none',maxColor='none', cbScale='linear',cbTitle=r'Density $m^{-3}$',colormap='viridis',title='SOLPS data',
        xlims=[0.25,1.6],ylims=[-1.7,1.7],ylabelOn=True,colorBarOn=True,filename='NONE',inputLoc='NONE',config=' ',inputLoc2='NONE',titleSize=35,cbTitleSize=25,cbTickThirds=False,tickLabelSize=20,axislabelSize=25,
            drawSep=False, sepIdx=8,sepxPts=0,sepyPts=0,sepColor='r',llamaOn=False):
# xPts is b2fgmtry.crx
# yPts is b2fgmtry.cry
# var is whatever variable you want to plot
# minColor and maxColor are bounds of colorbar, will try to automatically find bounds if you don't specify
# cbScale is scale of colorbar (log or linear or symlog, symlog changes colorbar to 'bwr')
# cbTitle is the title of the colorbar
# colormap is the colormap used by the colorbar
# title is the title of the whole plot
# xlims and ylims give the x and y bounds of the 2D plot
# colorBarOn turns color bar on and off
# filename is the name of the file the plot is saved to, 'NONE' causes the plot not to be saved
# inputLoc is the location of the input.dat, used to add walls to the 2D plot, 'NONE'
    if inputLoc!='NONE':
        wallGeo = read_input(inputLoc)
    if inputLoc2!='NONE':
        wallGeo2 = read_input(inputLoc2)
    patches = []
    nx = np.shape(xPts)[0]
    ny = np.shape(xPts)[1]
    for iy in np.arange(0,ny):
        for ix in np.arange(0,nx):
            rcol = xPts[ix,iy,[0,1,3,2]]
            zcol = yPts[ix,iy,[0,1,3,2]]
            rcol.shape=(4,1)
            zcol.shape=(4,1)
            polygon = Polygon(np.column_stack((rcol,zcol)), True,linewidth=3)
            patches.append(polygon)

    vals=var.T.flatten()
    if (cbScale=='symlog'):
        p = PatchCollection(patches,False,cmap='bwr',edgecolor='k',linewidth=0.15)
    else:
        p = PatchCollection(patches,False,cmap=colormap,edgecolor='k',linewidth=0.1)
    p.set_array(np.array(vals))
    if (minColor!='none'):
        if (cbScale=='linear'):
            p.set_clim([minColor,maxColor])
        if (cbScale=='log'):
            p.norm=colorsMPL.LogNorm(vmin=minColor,vmax=maxColor,clip=True)
        if (cbScale=='symlog'):
            p.norm=colorsMPL.SymLogNorm(linthresh=maxColor/50,linscale=0.5,vmin=minColor,vmax=maxColor)



    if not colorBarOn: fig,axs = plt.subplots(1,figsize=(abs((xlims[0]-xlims[1])/(ylims[0]-ylims[1]))*11, 11))
    else: fig,axs = plt.subplots(1,figsize=(abs((xlims[0]-xlims[1])/(ylims[0]-ylims[1]))*11*1.1875, 11))
    
    axs.add_collection(p)
    if (colorBarOn):
        if cbScale == 'symlog':
            if cbTickThirds: tickLocs = [maxColor/3,maxColor/30,maxColor/300,minColor/300,minColor/30,minColor/3]
            else: tickLocs = [maxColor/1,maxColor/10,maxColor/100,minColor/100,minColor/10,minColor/1]
            cb = plt.colorbar(p,ax=axs,pad=0.01,ticks=tickLocs)
#            tickLabels = []
#            for i in range(len(tickLocs)): tickLabels.append(tickLocs[i])
#            cb.ax.set_yticklabels(tickLabels)
        else:
            cb = plt.colorbar(p,ax=axs,pad=0.01)
        cb.ax.tick_params(labelsize=tickLabelSize)
        cb.set_label(cbTitle,fontsize=cbTitleSize)
    if inputLoc!='NONE':
        wallColor ='k'
        wallWidth=4
        NURpfrIdx = [22,23,24,25,26,27,28,29,30]
        NURevaporator = [112]
        LIDIdx = [15,16,17,18,19,20,21]
        targetSides = [113,114]
        NURDpuffLoc = [27]
        MDDpuffLoc = [49]
        coldBoxIdx = [32,33,34,35,52,53,54,55]
        hotBoxIdx = [36,37,38,39,119,120,121,122,123,116,47,48,49,50,51]
        evaporatorIdx = [36,37,50,51]

        liquidLiIdx = [39,40,41,42,43,46,47,48,49,50,51]
        CDevaporatorIdx = [44,45]
        CDpuffLoc = [53]
       
#        divSOLliquidLiIdx   = [27,28,30,31,32,33,34,134,135,136,137,138,140,147,150]
#        divSOLevaporatorIdx = [29,139]
#        divSOLpuffLoc       = [35]
        divSOLcoldIdx = [133,134,135,136,137,31,32,33,34]
        divSOLevaporatorIdx = [138,139,29,30]
        divSOLPFRevaporatorIdx = [138,139]
        divSOLCFRevaporatorIdx = [29,30]
        divSOLwarmIdx = [140,150,151,152,153,154,155,156,157,147,27,28]
        divSOLnozzleWarmIdx = [119,150,151,152,153,154,155,156,157,147,27,28]
        divSOLpuffLoc=[36]
        divSOLpuffLocCFR = [36]
        divSOLpuffLocPFR = [132]
        divSOLpuffLocPFRcave = [115]
 
        for i in range(np.shape(wallGeo)[0]):
            r=np.array([wallGeo[i][2],wallGeo[i][4]])/100
            z=np.array([wallGeo[i][3],wallGeo[i][5]])/100
            if (config=='open'):
                    if (wallGeo[i][1] in NURpfrIdx and wallGeo[i][1] not in NURDpuffLoc):
                        plt.plot(r,z,'m-',linewidth=wallWidth)
                        continue
                    if (wallGeo[i][1] in targetSides):
                        plt.plot(r,z,'m-',linewidth=wallWidth)
                        continue
                    if wallGeo[i][1] in LIDIdx:
                        plt.plot(r,z,'m-',linewidth=wallWidth)
                        continue
                    if wallGeo[i][1]==NURevaporator:
                        plt.plot(r,z,'r-',linewidth=wallWidth)
                        continue
                    if wallGeo[i][1]==NURDpuffLoc:
                        plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5)
                        continue
                    plt.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='MD'):
                if wallGeo[i][1] in coldBoxIdx:
                    axs.plot(r,z,'b-',linewidth=wallWidth)
                    continue
                if wallGeo[i][1] in evaporatorIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth)
#                if wallGeo[i][1] in hotBoxIdx and wallGeo[i][1] not in evaporatorIdx:
#                if wallGeo[i][1]==-6: print ([wallGeo[i][2],wallGeo[i][4]])/100,[wallGeo[i][3],wallGeo[i][5]])/100)
#                    axs.plot(r,z,'k-',linewidth=wallWidth)
                    continue
                if wallGeo[i][1]==MDDpuffLoc:
                        plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5)
                        continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='slot'):
                if wallGeo[i][1] in liquidLiIdx:
                    axs.plot(r,z,'b-',linewidth=wallWidth)
                    continue
                if wallGeo[i][1] in CDevaporatorIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth)
#                if wallGeo[i][1] in hotBoxIdx and wallGeo[i][1] not in evaporatorIdx:
#                if wallGeo[i][1]==-6: print ([wallGeo[i][2],wallGeo[i][4]])/100,[wallGeo[i][3],wallGeo[i][5]])/100)
#                    axs.plot(r,z,'k-',linewidth=wallWidth)
                    continue
                if wallGeo[i][1]==CDpuffLoc:
                        plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5)
                        continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='divSOLslot'):
#                if wallGeo[i][1] in divSOLcoldIdx:
#                    axs.plot(r,z,'b-',linewidth=wallWidth*1.5)
#                    continue
                if wallGeo[i][1] in divSOLevaporatorIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1] in divSOLwarmIdx:
                    plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='divSOLCFR'):
                if wallGeo[i][1] in divSOLCFRevaporatorIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1]==divSOLpuffLocPFR:
                    plt.plot(np.average(r),np.average(z),color='g',marker='o',markersize=30,linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                if wallGeo[i][1] in divSOLwarmIdx:
                    plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='divSOL'):
                if wallGeo[i][1] in divSOLevaporatorIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1]==divSOLpuffLocPFR:
                    plt.plot(np.average(r),np.average(z),color='g',marker='o',markersize=30,linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                if wallGeo[i][1] in divSOLwarmIdx:
                    plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='divSOLPFR'):
                if wallGeo[i][1] in divSOLPFRevaporatorIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1]==divSOLpuffLocPFR:
                    plt.plot(np.average(r),np.average(z),color='g',marker='o',markersize=30,linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                if wallGeo[i][1] in divSOLwarmIdx:
                    plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='divSOLnozzle'):
                if wallGeo[i][1]==176:
                    plt.plot(r,z,color='r',marker=' ',markersize=30,linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                if wallGeo[i][1]==111:
                    plt.plot(np.average(r),np.average(z),color='g',marker='o',markersize=30,linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                if wallGeo[i][1] in divSOLnozzleWarmIdx:
                    plt.plot(r,z,color='orange',linestyle='solid',linewidth=wallWidth*1.5,zorder=200)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config==' '):
#                for j in range(np.shape(wallGeo)[0]):
                if inputLoc2=='NONE':
                    axs.plot(r,z,color=wallColor,linewidth=wallWidth,linestyle='solid')
                else:
                    if (wallGeo[i][1]==81 or wallGeo[i][1]==82 or wallGeo[i][1]==83 or 
                        wallGeo[i][1]==113 or wallGeo[i][1]==114 or
                        wallGeo[i][1]==135 or wallGeo[i][1]==128): continue
                    else: 
                        axs.plot(r,z,color=wallColor,linewidth=wallWidth,linestyle='dotted')
            if (config=='cave'):
                hotIdx = [122]
                reflIdx = [121,123]
                warmIdx=[161]
                if wallGeo[i][1] in hotIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1] in reflIdx:
                    axs.plot(r,z,'g-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1] in warmIdx:
                    axs.plot(r,z,c='orange',linestyle='solid' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1]==divSOLpuffLocPFRcave:
                    plt.plot(np.average(r),np.average(z),color='g',marker='o',markersize=30,linestyle='solid',linewidth=wallWidth*1.5,zorder=175)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
            if (config=='caveNoTop'):
                hotIdx = [122]
                warmIdx=[121,123,161]
                if wallGeo[i][1] in hotIdx:
                    axs.plot(r,z,'r-' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                if wallGeo[i][1] in warmIdx:
                    axs.plot(r,z,c='orange',linestyle='solid' ,linewidth=wallWidth*1.5,zorder=200)
                    continue
                axs.plot(r,z,'k-',linewidth=wallWidth)
        if inputLoc2!='NONE':
            for i in range(np.shape(wallGeo2)[0]):
                r2=np.array([wallGeo2[i][2],wallGeo2[i][4]])/100
                z2=np.array([wallGeo2[i][3],wallGeo2[i][5]])/100
                axs.plot(r2,z2,color='k',linewidth=wallWidth,linestyle='dashed')
#                if wallGeo2[i][1]==139 or wallGeo2[i][1]==138 or wallGeo2[i][1]==29 or wallGeo2[i][1]==30:
#                    axs.plot(r2,z2,color='r',linewidth=wallWidth,linestyle='solid')
#                coldWalls = [133,134,135,136,137,31,32,33,34,35]
#                if wallGeo2[i][1]==147 or wallGeo2[i][1]==150 or wallGeo2[i][1] in coldWalls:
#                    axs.plot(r2,z2,color='b',linewidth=wallWidth,linestyle='solid')
#                tarEvaporators = [-6,140,28,147,150,175]
#                if wallGeo2[i][1] in tarEvaporators:
#                    axs.plot(r2,z2,color='orange',linewidth=wallWidth,linestyle='solid')
    if drawSep:
        if len(np.shape(sepxPts))<1:
            for i in range(len(xPts[:,sepIdx,0])):
                if i==np.amax(range(len(xPts[:,sepIdx,0]))): continue
                axs.plot([xPts[i,sepIdx,0],xPts[i+1,sepIdx,0]],[yPts[i,sepIdx,0],yPts[i+1,sepIdx,0]],sepColor,linewidth=3)
        else:
            for i in range(len(sepxPts[:,sepIdx,0])):
                if i==np.amax(range(len(sepxPts[:,sepIdx,0]))): continue
                axs.plot([sepxPts[i,sepIdx,0],sepxPts[i+1,sepIdx,0]],[sepyPts[i,sepIdx,0],sepyPts[i+1,sepIdx,0]],sepColor,linewidth=2)
    axs.set_title(title,fontsize=titleSize)
    axs.set_ylim(ylims)
    axs.set_xlim(xlims)
    axs.tick_params(axis='both',labelsize=tickLabelSize,labelleft=ylabelOn)
    if ylabelOn:
        plt.ylabel('Z [m]',fontsize=axislabelSize)
    else:
        plt.ylabel('',fontsize=axislabelSize)
    plt.xlabel('R [m]',fontsize=axislabelSize)
    plt.grid(True)
    if llamaOn:
        Rllama = np.array([1.1066,1.1174,1.1279,1.1387,1.1491,1.1595,1.17,1.1805,1.1913,1.2016,
                           1.2121,1.2225,1.2331,1.2433,1.2534,1.2635,1.2737,1.2839,1.2944,1.3041,
                           1.848,1.8603,1.8713,1.8825,1.8939,1.9055,1.9163,1.9265,1.9372,1.9479,
                           1.9579,1.9778,1.9877,1.9978,2.0072,2.0167,2.0257,2.035,2.0441])
        Zllama = np.array([-0.71067,-0.7096,-0.70789,-0.70872,-0.70898,-0.70716,-0.70719,-0.70596,
                           -0.70544,-0.70639,-0.70635,-0.70524,-0.7038,-0.70411,-0.70411,-0.70405,
                           -0.70233,-0.70206,-0.70374,-0.70423,-0.73876,-0.73758,-0.73815,-0.73901,
                           -0.73784,-0.73997,-0.7373,-0.73848,-0.7409,-0.74013,-0.7403,
                           -0.74,-0.73998,-0.73947,-0.74061,-0.74008,-0.74077,-0.73995,-0.7401,])
#       Rllama = np.array([181.27166667, 182.34833333, 183.425     , 184.50166667,
#       185.57833333, 186.655     , 187.73166667, 188.80833333,
#       189.885     , 190.96166667, 192.03833333, 193.115     ,
#       194.19166667, 195.26833333, 196.345     , 197.42166667,
#       198.49833333, 199.575     , 200.65166667, 201.72833333])/100
#       Zllama = np.array([-77.4, -77.4, -77.4, -77.4, -77.4, -77.4, -77.4, -77.4, -77.4,
#       -77.4, -77.4, -77.4, -77.4, -77.4, -77.4, -77.4, -77.4, -77.4,
#       -77.4, -77.4])/100
        plt.plot(Rllama,Zllama,'bo')
    if filename != 'NONE':
        plt.savefig(filename,bbox_inches='tight')    
    plt.show()

def is_neutral(a):
# checks if the species is a neutral 
# DOESNT WORK WITH MORE THAN TWO TYPES OF IONS
    if a>=6: print('WARNING: bigger species index than is_neutral was made for, proceed with caution')
    if a==0 or a==2:
        return True
    else:
        return False

def read_b2wdat_field(filename):
# reads a .out file produced by setting b2wdat_iout='4' in b2mn.dat
    f = open(filename)
    line = f.readline().rstrip().split()
    fieldVal = []
    while (line!=[]):
        line = f.readline().rstrip().split()
        if line==[]: break
        fieldVal.append([float(i) for i in line][1:])
    return np.array(fieldVal[::-1]).T

def read_b2wdat(b2wdatLoc,nSpec):
# reads .out files produced by setting b2wdat_iout='4' in b2mn.dat and returns a class with the data
# currently only grabs what I have needed there are literally hundreds more
# this isn't a very robust function, might not work if it isn't a D-only or D+Li case. Be careful
# adjusting is_neutral to be more robust might be all it needs but not sure
    nas = []
    uas = []
    ues = []
    b2srdt_smodts = []
    b2npmo_fmoxs = []
    b2npmo_fmoys = []
    b2sigp_smogpis = []
    b2sigp_smogpos = []
    b2npmo_smbs = []
    b2stcx_smqs = []
    b2npmo_smocfs = []
    b2stel_smq_ions = []
    b2stel_smq_recs = []
    b2npmo_smotfias = []
    b2npmo_smotfeas = []
    b2npmo_smofreas = []
    b2npmo_smofrias = []
    b2npmo_smoans = []
    b2stbc_phys_smos = []
    b2npmo_smovvs = []
    b2npmo_smovhs = []
    b2stbr_smos = []
    b2trcl_luciani_fllim_cvsahzxs = []
    b2trcl_luciani_cvsahzxs = []
    b2npmo_resmos = []
    b2stbr_sna_eirs = []
    b2stel_sna_ions = []
    b2stel_sna_recs = []
    b2npc_snas = []
    b2npc_fnaxs = []
    b2npc_fnays = []
    crxs = []
    crys = []
    for i in range(4): crxs.append(read_b2wdat_field(b2wdatLoc+'output/'+'crx'+str(i)+'.dat'))
    for i in range(4): crys.append(read_b2wdat_field(b2wdatLoc+'output/'+'cry'+str(i)+'.dat'))
    for spIdx in range(nSpec):
        if is_neutral(spIdx): continue
        if spIdx==1:nas.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npc11_na00'+str(spIdx)+'.dat'))
        if spIdx>1: nas.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npc11_na00'+str(spIdx)+'.dat'))
        uas.append(np.array(read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_ua00'+str(spIdx)+'.dat')))
        b2srdt_smodts.append( -read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_madnavadt00'+str(spIdx)+'.dat'))
        b2npmo_fmoxs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_fmox00'+str(spIdx)+'.dat'))
        b2npmo_fmoys.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_fmoy00'+str(spIdx)+'.dat'))
        b2sigp_smogpis.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2sigp_smogpi00'+str(spIdx)+'.dat'))
        b2sigp_smogpos.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2sigp_smogpo00'+str(spIdx)+'.dat'))
        b2npmo_smbs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smb00'+str(spIdx)+'.dat'))
        b2stcx_smqs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2stcx_smq00'+str(spIdx)+'.dat'))
        b2npmo_smocfs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smocf00'+str(spIdx)+'.dat'))
        b2stel_smq_ions.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2stel_smq_ion00'+str(spIdx)+'.dat'))
        b2stel_smq_recs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2stel_smq_rec00'+str(spIdx)+'.dat'))
        b2npmo_smotfias.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smotfia00'+str(spIdx)+'.dat'))
        b2npmo_smotfeas.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smotfea00'+str(spIdx)+'.dat'))
        b2npmo_smofreas.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smofrea00'+str(spIdx)+'.dat'))
        b2npmo_smofrias.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smofria00'+str(spIdx)+'.dat'))
        b2npmo_smoans.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smoan00'+str(spIdx)+'.dat'))
        b2stbc_phys_smos.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2stbc_phys_smo00'+str(spIdx)+'.dat'))
        b2npmo_smovvs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smovv00'+str(spIdx)+'.dat'))
        b2npmo_smovhs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_smovh00'+str(spIdx)+'.dat'))
        b2stbr_smos.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2stbr_smo_eir00'+str(spIdx)+'.dat'))
        b2trcl_luciani_fllim_cvsahzxs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2trcl_luciani_fllim_cvsahzx00'+str(spIdx)+'.dat'))
        b2trcl_luciani_cvsahzxs.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2trcl_luciani_cvsahzx00'+str(spIdx)+'.dat'))
        b2npmo_resmos.append( read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_resmo00'+str(spIdx)+'.dat'))
        b2stbr_sna_eirs.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2stbr_sna_eir00'+str(spIdx)+'.dat'))
        b2stel_sna_ions.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2stel_sna_ion00'+str(spIdx)+'.dat'))
        b2stel_sna_recs.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2stel_sna_rec00'+str(spIdx)+'.dat'))
        if spIdx==0 or spIdx==2: b2npc_fnaxs.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npco_fnax00'+str(spIdx)+'.dat'))
        else: b2npc_fnaxs.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npc11_fnax00'+str(spIdx)+'.dat'))

        if spIdx==0 or spIdx==2: b2npc_fnays.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npco_fnaxy00'+str(spIdx)+'.dat'))
        else: b2npc_fnays.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npc11_fnay00'+str(spIdx)+'.dat'))

        if spIdx==0 or spIdx==2: b2npc_snas.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npc_sna00'+str(spIdx)+'.dat'))
        else: b2npc_snas.append(read_b2wdat_field(b2wdatLoc+'output/'+'b2npc11_sna00'+str(spIdx)+'.dat'))
    #initialize class that will hold all the data of bwdat output
    class b2wdatResults:
        def __init__(self):
            #LHS of the momentum eqn
            self.b2srdt_smodt = b2srdt_smodts
            self.b2npmo_fmox = b2npmo_fmoxs
            self.b2npmo_fmoy = b2npmo_fmoys
            self.b2sigp_smogpi = b2sigp_smogpis
            self.b2sigp_smogpo = b2sigp_smogpos

            #RHS of the momentum equation
            self.b2npmo_smb = b2npmo_smbs
            self.b2stcx_smq = b2stcx_smqs
            self.b2npmo_smocf = b2npmo_smocfs
            self.b2stel_smq_ion = b2stel_smq_ions
            self.b2stel_smq_rec = b2stel_smq_recs
            self.b2npmo_smotfia = b2npmo_smotfias
            self.b2npmo_smotfea = b2npmo_smotfeas
            self.b2npmo_smofrea = b2npmo_smofreas
            self.b2npmo_smofria = b2npmo_smofrias
            self.b2npmo_smoan = b2npmo_smoans
            self.b2stbc_phys_smo = b2stbc_phys_smos
            self.b2npmo_smovv = b2npmo_smovvs
            self.b2npmo_smovh = b2npmo_smovhs
            self.b2stbr_smo = b2stbr_smos
            self.b2trcl_luciani_fllim_cvsahzx = b2trcl_luciani_fllim_cvsahzxs
            self.b2trcl_luciani_cvsahzx = b2trcl_luciani_cvsahzxs
            self.b2npmo_resmo = b2npmo_resmos

            #energy balance terms
            self.b2stbr_shi_eir = read_b2wdat_field(b2wdatLoc+'output/'+'b2stbr_shi_eir.dat')
            self.b2stbr_she_eir = read_b2wdat_field(b2wdatLoc+'output/'+'b2stbr_she_eir.dat')
            self.b2stel_she_rad = read_b2wdat_field(b2wdatLoc+'output/'+'b2stel_she_rad.dat')

            #particle sources
            self.b2stbr_sna_eir = b2stbr_sna_eirs
            self.b2stel_sna_ion = b2stel_sna_ions
            self.b2stel_sna_rec = b2stel_sna_recs
            self.b2npc_sna = b2npc_snas
            self.b2npc_fnaxs = b2npc_fnaxs
            self.b2npc_fnays = b2npc_fnays

            #geo info
            self.hx  = read_b2wdat_field(b2wdatLoc+'output/'+'hx.dat')
            self.hy  = read_b2wdat_field(b2wdatLoc+'output/'+'hy.dat')
            self.hz  = read_b2wdat_field(b2wdatLoc+'output/'+'hz.dat')
            self.vol = read_b2wdat_field(b2wdatLoc+'output/'+'vol.dat')
            self.bbx = read_b2wdat_field(b2wdatLoc+'output/'+'bbx.dat')
            self.bb  = read_b2wdat_field(b2wdatLoc+'output/'+'bb.dat')
            self.bx  = read_b2wdat_field(b2wdatLoc+'output/'+'bbx.dat')/read_b2wdat_field(b2wdatLoc+'output/'+'bb.dat')
            self.crx = crxs
            self.cry = crys

            #plasma parameters
            self.na = nas
            self.ua = uas
            self.ue = read_b2wdat_field(b2wdatLoc+'output/'+'b2npmo_ue.dat')
            self.phi = read_b2wdat_field(b2wdatLoc+'output/'+'b2nppo_po.dat')
            self.ti = read_b2wdat_field(b2wdatLoc+'output/'+'ti_eV.dat')
            #misc
            self.fchanmly = read_b2wdat_field(b2wdatLoc+'output/'+'b2tfch__fchanmly.dat')
            self.fchanmlx = read_b2wdat_field(b2wdatLoc+'output/'+'b2tfch__fchanmlx.dat')
            self.fchdiay  = read_b2wdat_field(b2wdatLoc+'output/'+'b2tfch__fchdiay.dat')
            self.fchdiax  = read_b2wdat_field(b2wdatLoc+'output/'+'b2tfch__fchdiax.dat')

    b2wdat = b2wdatResults()#instantiate class
    print('done reading b2wdat files')
    return b2wdat


def read_runlog(filename):
# reads run.log file produced by b2run b2mn > run.log
# currently just finds the recombination from the volumetric reombination in the second to last stratum
    record=False
    for line in reversed(list(open(filename))):
        if ('ISTRATUM' in line.rstrip().split() and record): break
        if ('ISTRATUM' in line.rstrip().split()): record=True
        if record:
            if 'IS,SSNI,SSMO' in line.rstrip().split() and line.rstrip().split()[2]=='3': reco = (line.rstrip().split()[3])
    return float(reco)/ev

def read_runlogD2(filename,verbose=False):
# reads run.log file produced by b2run b2mn > run.log
# currently just finds the recombination from the volumetric reombination in the third to last stratum
    record1=False
    record2=False
    record=False
    noCount=True
    counter=0
    for line in reversed(list(open(filename))):
        if ('ISTRATUM' in line.rstrip().split() and not noCount):
            noCount=True
        if not noCount:
            counter+=1
        if ('CUM:SSEE,SSEI[1234],SSNI,SSMO' in line.rstrip().split() and noCount):
            noCount=False
        if noCount and counter>0:
            if counter>3:
                if ('ISTRATUM' in line.rstrip().split() and record2): break
                if ('ISTRATUM' in line.rstrip().split() and record1): record2=True
                if ('ISTRATUM' in line.rstrip().split()): record1=True
                if record2:
                    if 'IS,SSNI,SSMO' in line.rstrip().split() and line.rstrip().split()[2]=='1': reco = (line.rstrip().split()[3])
                if verbose: print('More species file: ', line)
            if counter==3:
                if ('ISTRATUM' in line.rstrip().split() and record): break
                if ('ISTRATUM' in line.rstrip().split()): record=True
                if record:
                    if 'IS,SSNI,SSMO' in line.rstrip().split() and line.rstrip().split()[2]=='1': reco = (line.rstrip().split()[3])
                if verbose: print('D-only file:', line)

    return float(reco)/ev


def checkLastItim(fileLoc):
    fid = open(fileLoc)
    line = fid.readline().rstrip().split()
    lastTim = 0
    while 'b2mn.exe.dir' not in line:
        line = fid.readline().rstrip().split()
        if 'b2mndr_00:itim,dtim,ntim,stack_ptr' in line:
            lastTim = int(line[1])
    return lastTim

def read_runLog(runLogFile):
# reads the run log to find the pumped flux in itim=step
# only tested for a run.log.last10, might take a while for a full run.log
# returns the wall number, pumped species, and pumped flux in amperes
    testLine='NO. SPECIES  PUMPED FLUX'
    testLine=testLine.rstrip().split()
    testLine2 = 'PUMPED FLUX (ATOMIC) PER SPECIES'
    testLine2 = testLine2.rstrip().split()
    
    fid = open(runLogFile)
    step = checkLastItim(runLogFile)
    pumpedList=[]
    record=False
    i=1
    rightStep=False
    while i==1:
        line = fid.readline().rstrip().split()
        if 'b2mndr_ok:itim,dtim,ntim,stack_ptr' in line and str(step-1) in line: rightStep=True
        if (line==['NO.', 'SPECIES', 'PUMPED', 'FLUX'] and rightStep): break
    
    while i==1:
        line = fid.readline().rstrip().split()
        if line==[]: break
#         print(line[0],line[1],line[2])
        if   line[1]=='LI':   spIdx = 2
        elif line[1]=='LI+':  spIdx = 3
        elif line[1]=='LI++': spIdx = 4
        elif line[1]=='LI3+': spIdx = 5
        elif line[1]=='D':    spIdx = 0
        elif line[1]=='D2':   spIdx = -1
        pumpedList.append([int(line[0]),spIdx,float(line[2])])   
    return np.array(pumpedList)


#################################################################################

# The following functions were used to reproduce and check solps momentum results
# Probably not useful but kept just in case

#################################################################################


def b2tlnl(nx, ny, te, ti, ne,icase=0):

    ev=1.6021766339999999E-019
#-----------------------------------------------------------------------
#
# purpose
#
#     B2TLNL computes the Coulomb logarithm according to Braginskii or 
#     Wesson formulas.
#
#
#     lnlam is the log of the plasma parameter.
#
#-----------------------------------------------------------------------
#declarations
    lnlam=np.zeros(np.shape(te))
    
#.computation
    lamda=-5.0
    if (lamda<0):
        if icase==0:#Braginskii
            for iy in range(ny):
                for ix in range(nx):
                    if(te[ix][iy]/ev <= 50.0):
                        lnlam[ix][iy]=max(-lamda,23.4 - 1.15*math.log10(ne[ix][iy]/1.0e6) +
                                      3.45*math.log10(te[ix][iy]/ev))
                    else:
                        lnlam[ix][iy]=max(-lamda,25.3 - 1.15*math.log10(ne[ix][iy]/1.0e6) + 
                                      2.30*math.log10(te[ix][iy]/ev))
    else:
        lnlam = lamda
    return lnlam

def fce1(z): return ((1.0+0.24*z)*(1.0+0.93*z))/((1.0+2.56*z)*(1.0+0.29*z))

def fce2(z): return ((1.0+1.40*z)*(1.0+0.52*z))/((1.0+2.56*z)*(1.0+0.29*z))*1.56

def fce2n(z): return fce2(z)/(z+math.sqrt(2.0)/2.0)

def fal_cen(z): return -fce2n(z)/fce1(z)

def zmffCalc(zamax,na,ns,ismain):
    zmff   = np.zeros(np.shape(na[:,:,0]))
    for sI in range(ns):
        if(sI!=ismain): zmff = zmff + zamax[sI]**2 * na[:,:,sI]
    zmff=zmff/(zamax[ismain]**2 * na[:,:,ismain])
    return zmff

def fkabvp(a,b,zamax,na):
    ismain = 1
    ns=len(zamax)
    zmff   = zmffCalc(zamax,na,ns,ismain)
    cimp1=fce1(zmff)
    if (a==ismain and (b!=a) and not is_neutral(a) and not is_neutral(b)):
        fkabvp=cimp1
    elif ((b==ismain) and (a!=b) and not is_neutral(a) and not is_neutral(b)):
        fkabvp=cimp1
    elif((a!=b and a!=ismain) and (b!=ismain) and not is_neutral(a) and not is_neutral(b)):
        fkabvp=np.ones(np.shape(na[:,:,0]))
    elif((a==b) and (not is_neutral(a)) and (not is_neutral(b))):
        fkabvp=np.zeros(np.shape(na[:,:,0]))
    else:
        fkabvp=np.zeros(np.shape(na[:,:,0]))
    return fkabvp

def fkabtf(a, b,zamax,na):
    ismain=1
    ns=len(zamax)
    zmff = zmffCalc(zamax,na,ns,ismain)
    cimp2=fce2(zmff)
    if ((b==ismain) and (b!=a) and (not is_neutral(a)) and (not is_neutral(b))):
        fkabtf=cimp2
    elif ((a!=ismain) and (b!=ismain) and (not is_neutral(a)) and (not is_neutral(b))):
        fkabtf=0.0
    elif ((a==ismain)):
        fkabtf=0.0
    else:
        fkabtf=0.0
    return fkabtf

def fka(a,zamax,na,am):
    ns = len(zamax)
    rz2 = zamax**2
    fka = np.zeros(np.shape(na[:,:,0]))
    for r in range(ns):
        fka = fka + rz2[r]*na[:,:,r]*math.sqrt(mp)*math.sqrt(am[a]*am[r]/(am[a]+am[r]))
    fka = fka*rz2[a]
    return fka


def b2xpne(ns, rza, na):# b2aux/b2xpne.F
#     ------------------------------------------------------------------
#     B2XPNE computes the electron density, ne:
#       ne(,) = (sum is :: rza(,,is)*na(,,is))
#     I'm using it to calculate ne2 which is used in some functions below
#     ------------------------------------------------------------------
    ne = np.zeros(np.shape(na[:,:,0]))
    for species in range(ns): 
        ne = ne + rza[species]*na[:,:,species]
    return ne
