import os,sys
import re
import numpy as np
import matplotlib.pyplot as plt
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import openfastInterface as ofi
import airfoilcalcs as afc
import xfoilInterface as xi

#%% Parameters
BlPitch = [1.051]#,1.173,0.870,5.332,6.719,8.923,10.728,12.362,13.870,15.347,16.813,18.220,19.540,20.781,21.969,23.121,24.251,25.365,26.462]
RotSpeed = [12.105]#,8.549,8.163,7.619,7.273,6.667,6.154,5.714,5.333,5.000,4.706,4.444,4.211,4.000,3.810,3.636,3.478,3.333,3.200]
HWindSpeed = [9]#,9.3,9.8,10.5,11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0,21.0,22.0,23.0,24.0,25.0]

numBladePts = 30

workingdir = '/home/colin/Documents/DLI/wind/openfast/'
xfoildir   = '/home/colin/Documents/DLI/xfoil/'
os.chdir(workingdir)

fstFile = 'IEA-3.4-130-RWT.fst'
edFile = '%sIEA-3.4-130-RWT_ElastoDyn%s.dat'
ifFile = '%sIEA-3.4-130-RWT_InflowFile%s.dat'
adfile = '%sIEA-3.4-130-RWT_AeroDyn15%s.dat'
adNodeOutputs = ['VUndx','VRel','DynP','Re','M','Alpha','Theta','Phi','Fl','Fd','Mm']
adNodeOutputs = '"' + '"\n"'.join(adNodeOutputs) + '"'
fileLabels = ('TEMP_','_template')
#InflowFile = ifFile % tempFile
#EDFile = edFile % tempFile
#ADfile = adfile % tempFile
bl = ofi.bladeProperties()

params = ofi.paramsDict(len(BlPitch),BlPitch=BlPitch,RotSpeed=RotSpeed,
                        HWindSpeed=HWindSpeed,AeroDynNodeOutputs=adNodeOutputs)
#,EDFile=EDFile,AeroFile=ADfile,InflowFile=InflowFile

#%% Run functions
df = ofi.runOpenfast(fstFile,[edFile,ifFile,adfile],fileLabels,params)
print('Openfast Operation Complete.')

#%% Filter Based on max/min criteria
crit = ['RootFxb1','RootFyb1','RootFzb1','RootMxb1','RootMyb1','RootMzb1','AB1N025Fl']

dfmaxmin = df.iloc[ofi.dfMaxMinIndex(df,crit)]

#%% Create arrays of node values
#var values will pull all instances of each of the variables in each dataframe row,
#and create an array of the values indexed by the variable as a key:
# [{'Alpha':np.array([30 items])}]*len(dfmaxmin)
nodevars = ['Alpha','DynP','Fd','Fl','M','Mm','Phi','Re','Theta','VRel','VUndx','FLz']
cols = list(df.columns)
valuesList = [None]*len(dfmaxmin)
for i in range(len(dfmaxmin)):
  values = {}
  for var in nodevars:
    r = re.compile('.*B\dN\d\d\d'+var)
    colList = list(filter(r.match,cols))
    values[var] = np.zeros(len(colList))
    for j,item in enumerate(colList):
      values[var][j] = dfmaxmin[item].to_numpy()[i]
  valuesList[i] = values
      
for var in nodevars:
  plt.figure()
  plt.title('Plot of %s' % var)
  for i in range(len(valuesList)):
    plt.plot(valuesList[i][var])
  plt.show()
  
#%% Get Cp from xfoil
foilfile = 'AF%02.0f_Coords.foil'
numfoilpoints = 200
rho_air = 1.225
xList  = [None]*len(dfmaxmin)
yList  = [None]*len(dfmaxmin)
cpList = [None]*len(dfmaxmin)
pressureList = [None]*len(dfmaxmin)
_,yLocal  = ofi.afxy('/home/colin/Documents/DLI/IEA-3.4-130-RWT/openfast/Airfoils/')
for i in range(9,10):#len(dfmaxmin)):
  xLocal  = np.zeros([numfoilpoints,numBladePts])
  cp = np.zeros([numfoilpoints,numBladePts])
  for j in range(numBladePts):
    xLocal[:,j],cp[:,j] = xi.xfoilRun(foilfile % (j+1,),xfoildir,
                                  dfmaxmin['AB1N%03.0fRe' % (j+1,)].to_numpy()[i]*1e6,
                                  dfmaxmin['AB1N%03.0fM'  % (j+1,)].to_numpy()[i],
                                  dfmaxmin['AB1N%03.0fAlpha' % (j+1,)].to_numpy()[i])
  pressure = .5 * cp * valuesList[i]['VRel']**2 * rho_air
  pressureList[i] = pressure
  xList[i] = xLocal
  #yList[i] = yLocal
  cpList[i] = cp

"""
#%% Get element sizes
elementsize = np.zeros([np.shape(pressure)[0],np.shape(pressure)[1]])
for i in range(np.shape(pressure)[1]):
  elsi = afc.afElementLength(x[:,i],y[:,i])
  elementsize[:len(elsi),i] = elsi
  
#%% Calculate Bending Moment
normalForce,tangentForce = ofi.normTanForce(dfmaxmin,numBladePts)
plt.figure()
#plt.plot(stations,maxBendingMoment)
for i in range(len(valuesList)):
  moment,shear,deflection = afc.bending(eta30,bladelen,normalForce[i],np.interp(eta30,eta55,EI_flap_iea))
  plt.plot(eta30,deflection)
plt.legend(['Provided value'])
plt.show()
"""