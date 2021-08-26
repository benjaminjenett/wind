import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys,os
import xmltodict
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import ansysInterface as ai

bladelen = 63

srcfilename = os.path.join(wd,'ansys','IEA3_4MW','shell7.src')
lisfilename = os.path.join(wd,'ansys','IEA3_4MW','NLIST.lis')
#elementlisfilename = '/home/colin/Documents/DLI/ansys/IEA3_4MW/ELIST.lis'

filename = os.path.join(wd,'IEAonshore.xlsx')
dfiea_bct = pd.read_excel(filename,sheet_name = 'BladeExternalGeometry')
eta55 = dfiea_bct['Eta'][1:].to_numpy().astype(float)
prebend = dfiea_bct['PreBend'][1:].to_numpy().astype(float)/-1000 # m
chord = dfiea_bct['Chord'][1:].to_numpy().astype(float)/1000
aerocenter = dfiea_bct['AC Axis'][1:].to_numpy().astype(float)*chord/100


srcx,srcy,srcz,srcindex = ai.readsrcPoints(srcfilename,62264)
nodex,nodey,nodez,nodenum = ai.readNodes(lisfilename)
#sectype,secnum = ai.readSections(srcfilename)
#elementindex,elementsecs,elementnodes = ai.readElements(elementlisfilename)
localangle, avgx, avgy, avgz = ai.getDistortionAngle(srcindex, srcx, srcy, srcz, 61)
correctedz = ai.correctNodeZ(nodey,nodez,localangle,avgy,avgz)

#%% Process src points
roundedlist = np.round(srcindex/1000).astype(int)
uniquelist = np.unique(roundedlist)
ymax = np.zeros(len(uniquelist))
ymin = np.zeros(len(uniquelist))
etasrc = np.zeros(len(uniquelist))
for i in np.unique(uniquelist):
  tempindex = i == roundedlist
  ymax[i] = max(srcy[tempindex])
  ymin[i] = min(srcy[tempindex])
  etasrc[i] = np.mean(srcz[tempindex])/bladelen

del tempindex, uniquelist

prebend_etasrc = np.interp(etasrc,eta55,prebend)
ymax = ymax - prebend_etasrc
ymin = ymin - prebend_etasrc

#%% Parse Numad
numadfilename = os.path.join(wd,'IEA-3_4_NuMAD','IEA-3_4_NuMAD.nmd')

with open(numadfilename) as fd:
  doc = xmltodict.parse(fd.read())
  stations = doc['numad']['blade']['station']
  
ymax_numad = np.zeros(len(stations))
ymin_numad = np.zeros(len(stations))
eta_numad  = np.zeros(len(stations))

for i,st in enumerate(stations):
  tempcoords = st['coords'].splitlines()
  coords = np.zeros(len(tempcoords))
  for j in range(len(tempcoords)):
    tempcoord = tempcoords[j].split(' ')
    tempcoord = [i for i in tempcoord if i]
    coords[j] = tempcoord[1]
  ymax_numad[i] = max(coords)*float(st['chord'])
  ymin_numad[i] = min(coords)*float(st['chord'])
  eta_numad[i]  = float(st['locationz'])/bladelen
  
del tempcoords, coords, tempcoord

avgYsrc = np.interp(eta_numad,etasrc,(ymax+ymin)/2)
avgYnumad = y=(ymax_numad+ymin_numad)/2

ymax_numad = ymax_numad - avgYnumad + avgYsrc
ymin_numad = ymin_numad - avgYnumad + avgYsrc

plt.figure()
plt.plot(etasrc,ymax)
plt.plot(etasrc,ymin)
plt.plot(eta_numad,ymax_numad)
plt.plot(eta_numad,ymin_numad)
plt.plot(eta_numad,avgYnumad)
plt.plot(eta_numad,avgYsrc)
plt.plot(eta_numad,- avgYnumad + avgYsrc)
plt.legend(['y max', 'y min', 'y max numad', 'y min numad'])
plt.show()

#%% Print offsets
for i in range(len(avgYnumad)):
  print(eta_numad[i]*bladelen,'{:0.6f}'.format(-avgYnumad[i] + avgYsrc[i]),'0')