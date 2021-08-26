import pandas as pd
import sys,os
import numpy as np
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import xfoilInterface as xi
import openfastInterface as ofi
# airfoils: circular, FX77-W-500, FX77-W-400, DU00-W2-350, DU97-W-300, DU91-W2-250, DU08-W-210
xfoildir = '/home/colin/Documents/DLI/wind/xfoil/'
numaddir = '/home/colin/Documents/DLI/wind/IEA-3_4_NuMAD/'
numadAFdir = os.path.join(numaddir,'airfoils/')
filterprofile = 'FX77-W-500'

df = pd.read_excel(os.path.join(numaddir,'NuMAD.xlsx'),sheet_name = 'IEA',header=1,usecols='AP:BG',nrows=200)

index = df['interp?'] == 'Y'
foil1 = df['interpfoil1'][index].to_numpy()
foil2 = df['interpfoil2'][index].to_numpy()
ratio = df['interpValue'][index].to_numpy()
name  = df['InterpName'][index].to_numpy()

#%% Filter as required to limit interpolation to certain airfoil profiles
if 'filterprofile' in locals() and type(filterprofile) == str and len(filterprofile.strip()) > 0:
  index = np.where(np.array(foil2) == filterprofile)
  foil1 = foil1[index]
  foil2 = foil2[index]
  ratio = ratio[index]
  name  = name[index]
  del filterprofile

#%% Run Interpolation
f1 = xi.flatbackFoils(xfoildir, foil1)
f2 = xi.flatbackFoils(xfoildir, foil2)

flatbacks = np.where(f1 & f2)[0]

xi.interpFoils(foil1,foil2,ratio,name,xfoildir)
xi.foil2numad(name,xfoildir,numadAFdir,flatbacks)

#%% Plot numad and xfoil profiles to confirm that they are acceptable
import matplotlib.pyplot as plt
import xfoilInterface as xi
#name = ['airfoilname']
for foilname in name:
  x = ofi.importTxtFileNumpy(os.path.join(xfoildir,foilname+'.foil'),1)
  y = ofi.importTxtFileNumpy(os.path.join(xfoildir,foilname+'.foil'),2)
  x2 = ofi.importTxtFileNumpy(os.path.join(numadAFdir,foilname+'.txt'),1,delimiter='\t')
  y2 = ofi.importTxtFileNumpy(os.path.join(numadAFdir,foilname+'.txt'),2,delimiter='\t')
  if len(x2) == 0:
    x2 = ofi.importTxtFileNumpy(os.path.join(numadAFdir,foilname+'.txt'),1)
  if len(y2) == 0:
    y2 = ofi.importTxtFileNumpy(os.path.join(numadAFdir,foilname+'.txt'),2)  
  
  plt.figure()
  plt.plot(x,y)
  plt.plot(x2,y2,'.')
  plt.legend(['xfoil','NuMAD'])
  plt.show()
  
