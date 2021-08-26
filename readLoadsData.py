import sys,os
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import pandas as pd
import numpy as np
import datetime
import ansysInterface as ai

filename = os.path.join(wd,'TUM_3_35MW.xlsx')
variables = ['Fx','Fy','Fz','Mx','My','Mz','Fxy','Mxy']

df  = pd.read_excel(filename,sheet_name='RotorEnvelope',header=1)
df2 = pd.read_excel(filename,sheet_name='BladeExternalGeometry')
df.rename(columns={'Unnamed: 0':'LoadCase'},inplace=True)
eta55 = df2['Eta'][1:].to_numpy().astype(float)
twist = df2['Twist'][1:].to_numpy().astype(float)

etaSeries = df['Fx'][df.Fx.str.startswith('Envel').fillna(False)].tolist()
eta = np.zeros(len(etaSeries)+1)
for i in range(len(etaSeries)):
  temp = etaSeries[i].split()
  eta[i+1] = temp[temp.index('=')+1]
  
loadcases = list(df['LoadCase'].dropna().unique())

bladelen = 63
criticalvalue = 608.32
loadcaseValues,loadcases = ai.importLoadsFile(filename,criticalvalue)

ansysfolder = os.path.join(wd,'ansys')
ansysmodelfolder = 'IEAblade_nm03_latticeSW'

ansysoutputfilename = os.path.join(ansysfolder,'nodepressures%s.src' % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"),))
keynodes,zeronodes,nodenum,z = ai.getNodes(wd,ansysmodelfolder,'Cap')
loadcaseindex = -1
nodeforce = ai.generateNodeForce(loadcaseValues[loadcaseindex],keynodes,eta,ansysmodelfolder,z,eta55,twist,bladelen)
ai.writeForceSrc(nodeforce,nodenum,zeronodes,ansysoutputfilename)
