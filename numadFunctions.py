import numpy as np
import pandas as pd
import sys,os
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import numadInterface as numad

numadfolder = os.path.join(wd,'IEA-3_4_NuMAD')
numadfile   = os.path.join(numadfolder,'IEA-3_4_NuMAD.nmd')

#%% Clean materials file to remove unused materials
inputfile = 'MatDBsi_Lattice3x_optimized_temp.txt'
outputfile = os.path.join(numadfolder,'temp.txt')
materials = numad.matImport(os.path.join(numadfolder,inputfile),'composite')
othermats = numad.matImport(os.path.join(numadfolder,inputfile),'basic')
numadmodel = numad.numadImport(numadfile)
activematerials = numadmodel['numad']['activematerials']['list'].split('\n')
activematerials = np.unique(activematerials)
bladematerials = []
for station in numadmodel['numad']['blade']['station']:
  if type(station['surfacematerial']) == str:
    temp = station['surfacematerial'].replace(' ','').split('\n')
    bladematerials = bladematerials + temp
for station in numadmodel['numad']['blade']['shearweb']:
  if type(station['material']) == str:
    bladematerials = bladematerials + [station['material'].replace(' ','')]
bladematerials = np.unique(bladematerials)

matfilematerials = []
outputmaterials = []
bllist = []
for mat in materials:
  matfilematerials.append(mat['name'])
  if mat['name'] in bladematerials:
    outputmaterials.append(mat)
    bllist.append(round(int(mat['name'][:6])*.001,3))
#matfilematerials = np.unique(matfilematerials)
bluniquelist = np.unique(bllist)
numad.matExport(othermats+outputmaterials,outputfile)

del temp,station,mat

#%% Print revised delineation points for the numad model
# inputs from an excel file (NuMAD.xlsx), and reads from columns (originally columns labeled 2, 7, 9,14)
bladelen = 63

filename = os.path.join(numadfolder,'NuMAD.xlsx')
df = pd.read_excel(filename,sheet_name = 'IEA',header=1,nrows=83)
#df = df[~np.isnan(df['Eta'].to_numpy())]
eta = df['Eta'].to_numpy().astype(float)
col2  = df[2].to_numpy().astype(float)
col7  = df[7].to_numpy().astype(float)
col9  = df[9].to_numpy().astype(float)
col14 = df[14].to_numpy().astype(float)

doc = numad.numadImport(numadfile,'blade')
stations = doc['station']
z = np.zeros(len(stations))
points = ['']*len(stations)
mats = ['']*len(stations)
pointvals = [None]*len(stations)
index_df = np.zeros(len(stations))
for i in range(len(stations)):
  z[i] = stations[i]['locationz']
  points[i] = stations[i]['delineationpoint']
  mats[i] = stations[i]['surfacematerial']
  temp = points[i].split('\n')
  temparray = [None] * len(temp)
  for j,line in enumerate(temp):
    temparray[j] = line.split(' ',1)
  pointvals[i] = np.array(temparray)
  temp = np.abs(z[i]/bladelen-eta)
  index_df[i] = np.where(np.min(temp)==temp)[0][0]

expxml = ''
for i,vals in enumerate(pointvals):
  #print('z =',z[i])
  #print('\n'.join(' '.join(y) for y in vals),'\n')
  zeroindex = np.where(vals[:,0] == '0')[0][0]
  vals[2,0]  = col2[int(index_df[i])]
  vals[-3,0] = col14[int(index_df[i])]
  if len(vals[:,0]) == 17:
    vals[zeroindex-1,0] = col7[int(index_df[i])]
    vals[zeroindex+1,0] = col9[int(index_df[i])]
  print('new values at z =',z[i])
  print('\n'.join(' '.join(y) for y in vals),'\n')
  expxml = expxml + 'new values at z = ' + '{:0.3}'.format(z[i]) + '\n'
  expxml = expxml + '    <delineationpoint>\n' + '\n'.join(' '.join(y) for y in vals) + '\n    </delineationpoint>\n\n'

#%% Compare Materials 
# Verify whether different materials are identical by visual inspection
materials = numad.matImport(os.path.join(numadfolder,'MatDBsi_Lattice2x_noGelcoat.txt'),'composite')

name = [None]*len(materials)
matdata = [None]*len(materials)
matdataandname = [None]*len(materials)
matloc = [None]*len(materials)
uniquematdata = []
for i,mat in enumerate(materials):
  temp = []
  name[i] = mat['name']
  matloc[i] = name[i][7:]
  if type(mat['layer']) is list:
    for j,layer in enumerate(mat['layer']):
      temp.append(layer['layerName'])
      temp.append(layer['thicknessA'])
  if temp not in matdata:
    uniquematdata.append(temp)
  matdata[i] = temp
  matdataandname[i] = [name[i]] + temp
checkitems = np.array(['HP_FLAT','LP_FLAT'])
index = [None]*len(matloc)
for i in range(len(matloc)):
  if np.any(matloc[i] == checkitems):
    print(matdataandname[i])

#%% Remove a layer in all materials
removelayer = 'Gelcoat'
inputfile  = os.path.join(numadfolder,'MatDBsi.txt')
outputfile = os.path.join(numadfolder,'testMatDB.txt')
numad.removeLayers(removelayer,inputfile,outputfile)

#%% Split layers
# If material database is not properly ordered (not designed for bending), this
# function will divide it so that the total thickness of each material remains
# the same, but is divided equally in a symmetrical laminate
inputfile  = os.path.join(numadfolder,'MatDBsi.txt')
outputfile = os.path.join(numadfolder,'testMatDB.txt')
numad.splitLayers(inputfile,outputfile)

#%% Change core
import numadInterface as numad
inputfile  = os.path.join(numadfolder,'MatDBsi_Balsa_noGelcoat.txt')
outputfile = os.path.join(numadfolder,'MatDBsi_Lattice3x_noGelcoat.txt')
oldcore = 'BalsaIso'
newcore = 'Lattice'
factor = 3 #multiply the oldcore thickness by this factor when replacing the oldcore by the new core
minvalue = .02 # minimum thickness for the new core, overrides the original multiple if too thin
numad.changeCore(inputfile,outputfile,oldcore,newcore,factor,minvalue)
