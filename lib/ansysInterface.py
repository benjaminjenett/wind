#%% Setup and Functions
import numpy as np
import matplotlib.pyplot as plt
import csv, os
import pandas as pd

def readsrcPoints(filename,startrow):
  x = []
  y = []
  z = []
  index = []
  with open(filename) as file:
    content = file.readlines()[startrow-1:]
    for row in content:
      try:
        rowarray = row.split()[0].split(',')
        if rowarray[0] == 'k':
          x.append(rowarray[2])
          y.append(rowarray[3])
          z.append(rowarray[4])
          index.append(rowarray[1])
      except:
        continue
  return np.array(x).astype(float),np.array(y).astype(float),np.array(z).astype(float),np.array(index).astype(int)

def readNodes(filename):
  x = []
  y = []
  z = []
  index = []
  with open(filename) as file:
    content = file.readlines()
    for row in content:
      try:
        rowarray = row.split()#[0].split(' ')
        nodenum = int(rowarray[0])
        index.append(nodenum)
        x.append(float(rowarray[1]))
        y.append(float(rowarray[2]))
        z.append(float(rowarray[3]))
      except:
        continue
  return np.array(x).astype(float),np.array(y).astype(float),np.array(z).astype(float),np.array(index).astype(int)

def readSections(filename):
  outputtemp = []
  sectype = []
  secnum = []
  with open(filename) as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      try:
        row[0] = row[0].strip(' ')
        outputtemp.append(row)
      except:
        continue
        #output.append(row)
  for i in range(len(outputtemp)):
    if outputtemp[i][0] == 'sectype':
      loc = outputtemp[i-1][0].find('_')+1
      sectype.append(outputtemp[i-1][0][loc:])
      #sectype.append(outputtemp[i-1][0][9:])
      secnum.append(outputtemp[i][1])
  return sectype,np.array(secnum).astype(float)

def readElements(filename):
  index = []
  secnum = []
  nodes = []
  with open(filename) as file:
    content = file.readlines()
    for row in content:
      try:
        rowarray = row.split()#[0].split(' ')
        index.append(int(rowarray[0]))
        secnum.append(int(rowarray[5]))
        noderow = [rowarray[6],rowarray[7],rowarray[8],rowarray[9]]
        nodes.append(noderow)
      except:
        continue
  return np.array(index),np.array(secnum),np.array(nodes).astype(int)

def findNodeLoc(nodenum,secnum,sectype,elementnodes,elementsecs,topbottom):
  nodelocTypes = sorted(set(topbottom.values()))
  nodeloc = {}
  for i in nodelocTypes:
    nodeloc[i] = np.zeros(len(nodenum))#{'Top':np.zeros(len(nodenum)),'Bottom':np.zeros(len(nodenum)),'Web':np.zeros(len(nodenum))}
  for i in range(len(elementnodes)):#1,30000,3000):
    secnumlocal = elementsecs[i]
    seclabel = sectype[np.where(secnum == secnumlocal)[0][0]]
    nodeloclocal = topbottom[seclabel]
    #print(nodeloclocal)
    for j in range(np.shape(elementnodes)[1]):
      nodenumlocal = elementnodes[i,j]
      nodeloc[nodeloclocal][nodenumlocal-1] = 1
      #print(nodeloc[nodenumlocal-1])
  #for i in range(len(nodeloc)):
  #  nodeloc[i].uniq
  return nodeloc#['Top'],nodeloc['Bottom'],nodeloc['Web']

def correctTipNodes(dfiea,xArray,yArray,nodex,nodey,correctedz,avgy,avgz,topnodes,bottomnodes,eta,bladelen):
  minx = dfiea['TE'][1:].to_numpy(dtype=float)*-1e-3
  maxx = dfiea['LE'][1:].to_numpy(dtype=float)*-1e-3
  #thickness = dfiea['Abs thickness'][1:].to_numpy(dtype=float)*1e-3
  eta55 = dfiea['Eta'][1:].to_numpy(dtype=float)
  zeroindex = np.where(xArray == 0)[0][0]
  avgyc = (max(yArray)+min(yArray))/2
  plt.figure()
  plt.plot(xArray,yArray)
  for i in range(len(correctedz)):
    if correctedz[i]<58:
      continue
    etalocal = correctedz[i]/bladelen
    maxxlocal = np.interp(etalocal,eta55,maxx)
    minxlocal = np.interp(etalocal,eta55,minx)
    xc = min(1,max(0,(maxxlocal-nodex[i])/(maxxlocal-minxlocal)))
    yc = (nodey[i] - np.interp(correctedz[i],avgz,avgy))/(maxxlocal-minxlocal)+avgyc
    
    #print(xc,yc,topnodes[i],bottomnodes[i])
    xbottom = np.abs(xArray[zeroindex:]-xc).argmin()+zeroindex
    xtop = np.abs(xArray[:zeroindex+1]-xc).argmin()
    topbottom = np.abs(np.array([yArray[xtop],yArray[xbottom]])-yc).argmin()
    if topbottom == 1:
      topnodes[i] = 1
      bottomnodes[i] = 0
      plt.plot(xc,yc,'r.')
    else:
      topnodes[i] = 0
      bottomnodes[i] = 1
      plt.plot(xc,yc,'b.')
  plt.show()
  return topnodes,bottomnodes

def getDistortionAngle(srcindex, srcx, srcy, srcz, numsections):
  localangle = []
  avgz = []
  avgy = []
  avgx = []
  for i in range(numsections):
    localfilter = (srcindex < (i+1)*1000) & (srcindex > i*1000)
    #localset = index[localfilter]
    xlocal = srcx[localfilter]
    ylocal = srcy[localfilter]
    zlocal = srcz[localfilter]
    maxy = ylocal[ylocal==max(ylocal)][0]
    maxz = zlocal[ylocal==max(ylocal)][0]
    miny = ylocal[ylocal==min(ylocal)][0]
    minz = zlocal[ylocal==min(ylocal)][0]
    avgx.append((max(xlocal)+min(xlocal))/2)
    avgy.append((max(ylocal)+min(ylocal))/2)
    avgz.append((max(zlocal)+min(zlocal))/2)
    #avgy.append(np.mean(ylocal))
    #avgz.append(np.mean(zlocal))
    localangle.append(np.arctan((maxz-minz)/(maxy-miny)))
  return localangle,avgx,avgy,avgz

def correctNodeZ(nodey,nodez,localangle,avgy,avgz):
  correctedz = np.zeros(len(nodez))
  correctedy = np.zeros(len(nodey))
  for i in range(len(nodez)):
    ang = np.interp(nodez[i],avgz,localangle)
    correctedy[i] = nodey[i] - np.interp(nodez[i],avgz,avgy)
    dz = correctedy[i]*np.tan(ang)
    correctedz[i] = nodez[i]-dz
  correctedz = np.minimum(np.maximum(correctedz,0),63)
  return correctedz

def writeAnsysInput(nodenum,nodepressure,elementindex,elementnodes,cmd,prefix,filename = None):
  outputstr = prefix
  for i in range(np.shape(elementnodes)[0]):
    nplocal = []
    for node in elementnodes[i,:]:
      index = np.where(nodenum == node)[0][0]
      nplocal.append(nodepressure[index])
    outputstr = outputstr + cmd.format(elementindex[i],nplocal[0],nplocal[1],nplocal[2],nplocal[3])
  if filename is not None:
    file = open(filename,'w')
    file.write(outputstr)
    file.close()
  return outputstr

def replaceText(params,text,prefix=''):#,nodenum,nodepressure,elementindex,elementnodes,cmd,prefix,*args):
  outputstr = prefix
  try:
    if type(params[0]) == tuple:
      for paramTuple in params:
        outputstr = outputstr + text % paramTuple#cmd.format(elementindex[i],nplocal[0],nplocal[1],nplocal[2],nplocal[3])
    else:
      for param in params:
        outputstr = outputstr + text % (param,)
  except:
    outputstr = outputstr + text % (param,)
  return outputstr

def writeForceSrc(nodeforce,nodenum,zeronodes,ansysoutputfilename):
  nodeforcecmd = 'FLST,2,1,1,ORDE,1\nFITEM,2,%s\n!*\n/GO\nF,P51X,%s,%s\n'
  encastrecmd  = 'FLST,2,1,1,ORDE,1\nFITEM,2,%s\n!*\n/GO\nD,P51X, ,0, , , ,ALL, , , , ,\n'
  loadValue = np.concatenate((nodeforce[0],nodeforce[1],nodeforce[2],nodeforce[3]))
  index = np.nonzero(loadValue)[0]
  loadType = ['FX']*len(nodenum)+['FY']*len(nodenum)+['FZ']*len(nodenum)+['MZ']*len(nodenum)
  loadType = list(np.array(loadType)[index])
  nodenumfiltered = np.concatenate((nodenum,nodenum,nodenum,nodenum))
  nodenumfiltered = nodenumfiltered[index]
  loadValue = loadValue[index]
  params = list(zip(nodenumfiltered,loadType,loadValue))
  encastre = replaceText(nodenum[zeronodes], encastrecmd,
                         '/PREP7\nFDELE,ALL,ALL\nFKDELE,ALL,ALL\nDKDELE,ALL,ALL\nDDELE,ALL,ALL\n')
  outputText = replaceText(params,nodeforcecmd,encastre)#nodenum,nodepressure,elementindex,elementnodes,nodepressurecmd,encastre,ansysoutputfilename)
  with open(ansysoutputfilename,'w') as file:
    file.write(outputText)

def getNodes(DLIfolder,ansysmodelfolder,keynodelabel,adjustz = False,topbottom=None,shell='shell7.src',
             nlist='NLIST.lis',elist='ELIST.lis'):
  ansysfolder = os.path.join(DLIfolder,'ansys')
  if topbottom is None:
    topbottom = {'HP_CAP':'Cap', 'HP_FLAT':'Bottom', 'HP_LE_REINF':'Bottom', 'HP_TE_REINF':'Bottom',
                 'LE_PS_FILLER':'Bottom', 'LE_SS_FILLER':'Top', 'LP_CAP':'Cap', 'LP_FLAT':'Top',
                 'LP_LE_REINF':'Top', 'LP_TE_REINF':'Top', 'SW1':'Web', 'SW2':'Web','SW':'Web',
                 'SW_36':'Web','SW_37':'Web', 'SW_1_HP':'Cap', 'SW_1_LP':'Cap', 'SW_2_HP':'Cap', 
                 'SW_2_LP':'Cap', 'TE-PS-Filler':'Bottom', 'TE_SS_filler':'Top','HP_TE_FILLER':'Bottom',
                 'HP_LE_FILLER':'Bottom','LP_TE_FILLER':'Top', 'LP_LE_FILLER':'Top','LE_REINF':'Top'}

  srcfilename = os.path.join(ansysfolder,ansysmodelfolder,shell)
  lisfilename = os.path.join(ansysfolder,ansysmodelfolder,nlist)
  elementlisfilename = os.path.join(ansysfolder,ansysmodelfolder,elist)
  nodex,nodey,nodez,nodenum = readNodes(lisfilename)
  sectype,secnum = readSections(srcfilename)
  elementindex,elementsecs,elementnodes = readElements(elementlisfilename)
  nodeloc = findNodeLoc(nodenum,secnum,sectype,elementnodes,elementsecs,topbottom)
  if adjustz:
    srcx,srcy,srcz,srcindex = readsrcPoints(srcfilename,62264)
    localangle, avgx, avgy, avgz = getDistortionAngle(srcindex, srcx, srcy, srcz, 61)
    correctedz = correctNodeZ(nodey,nodez,localangle,avgy,avgz)
  else:
    correctedz = nodez
  zeronodes = np.where(correctedz < .001)[0]
  
  keynodes = np.zeros(len(correctedz))
  if type(keynodelabel) == str:
    keynodelabel = [keynodelabel]
  for label in keynodelabel:
    keynodes = np.maximum(keynodes,nodeloc[label])
  keynodes[zeronodes] = 0
  return keynodes,zeronodes,nodenum,correctedz

def generateNodeForce(loadcase,keynodes,eta,ansysmodelfolder,correctedz,twisteta,twist,bladelen,divisions=50):
  zeronodes = np.where(correctedz < .001)[0]
  
  keynodes[zeronodes] = 0
  etaFull = np.linspace(0,1,divisions+1)
  temptwist = np.interp(etaFull,twisteta,twist)
  
  # Note that the x,y,z directions provided in the report data do not align with 
  # the x,y,z axes of the ansys model
  tempFx = np.interp(etaFull,np.append(eta,1),np.append(loadcase['Fx'],0))
  tempFy = np.interp(etaFull,np.append(eta,1),np.append(loadcase['Fy'],0))
  Fy = np.cos(np.radians(temptwist))*tempFx + np.sin(np.radians(temptwist))*tempFy
  Fx = np.sin(np.radians(temptwist))*tempFx - np.cos(np.radians(temptwist))*tempFy
  Fz = -np.interp(etaFull,np.append(eta,1),np.append(loadcase['Fz'],0))
  Mz =  np.interp(etaFull,np.append(eta,1),np.append(loadcase['Mz'],0))
  dFx = Fx[:-1]-Fx[1:]
  dFy = Fy[:-1]-Fy[1:]
  dFz = Fz[:-1]-Fz[1:]
  dMz = Mz[:-1]-Mz[1:]
    
  nodeforce = getForce(correctedz,keynodes,etaFull,[dFx,dFy,dFz,dMz],bladelen)
  return nodeforce

def fixcmd(srcindex,encastrecmd,fixitemcmd):
  subset = srcindex[srcindex<1000]
  numelements = len(subset)
  outputstr = ''
  for i in range(numelements):
    outputstr = outputstr + fixitemcmd.format(subset[i])
  outputstr = encastrecmd.format(numelements,outputstr)
  return outputstr

def getPressure(dfiea,xArray,nodex,correctedz,pressure,bottomnodes,topnodes,eta,bladelen):
  minx = dfiea['TE'][1:].to_numpy(dtype=float)*-1e-3
  maxx = dfiea['LE'][1:].to_numpy(dtype=float)*-1e-3
  eta55 = dfiea['Eta'][1:].to_numpy(dtype=float)
  zeroindex = np.where(xArray[:,0] == 0)[0][0]
  nodepressure = np.zeros(len(nodex))
  for i in range(len(correctedz)):
    etalocal = correctedz[i]/bladelen
    maxxlocal = np.interp(etalocal,eta55,maxx)
    minxlocal = np.interp(etalocal,eta55,minx)
    xc = min(1,max(0,(maxxlocal-nodex[i])/(maxxlocal-minxlocal)))
    ind0 = np.abs(eta - etalocal).argmin()
    if eta[ind0] - etalocal <0:
      ind1 = ind0+1
    elif eta[ind0] == etalocal:
      #nodepressure[i] = np.interp(xc,xArray[zeroindex:,ind0],pressure[zeroindex:,ind0])      
      ind1 = ind0
      #continue
    else:
      ind1 = ind0
      ind0 = ind0-1
    if bottomnodes[i] == 1:
      pressure1 = np.interp(xc,xArray[zeroindex:,ind0],pressure[zeroindex:,ind0])
      pressure2 = np.interp(xc,xArray[zeroindex:,ind1],pressure[zeroindex:,ind1])
    elif topnodes[i] == 1:
      pressure1 = np.interp(xc,np.flip(xArray[:zeroindex+1,ind0]),np.flip(pressure[:zeroindex+1,ind0]))
      pressure2 = np.interp(xc,np.flip(xArray[:zeroindex+1,ind1]),np.flip(pressure[:zeroindex+1,ind1]))
    else:
      continue
    nodepressure[i] = np.interp(etalocal,
                                np.array([eta[ind0],eta[ind1]]),
                                np.array([pressure1,pressure2]))
  return nodepressure

def getForce(correctedz,skinnodes,eta,forces,bladelen):
  if len(forces)==len(correctedz):
    forces = [forces]
  #minx = dfiea['TE'][1:].to_numpy(dtype=float)*-1e-3
  #maxx = dfiea['LE'][1:].to_numpy(dtype=float)*-1e-3
  nodeEta = correctedz/bladelen
  #eta55 = dfiea['Eta'][1:].to_numpy(dtype=float)
  #zeroindex = np.where(xArray[:,0] == 0)[0][0]
  nodeForceList = [None]*len(forces)

  for i,forcelist in enumerate(forces):
    nodeforce = np.zeros(len(correctedz))
    for j,force in enumerate(forcelist):
      index = np.logical_and(np.logical_and(nodeEta > eta[j], nodeEta <= eta[j+1]), skinnodes == 1)
      unique,counts = np.unique(index, return_counts=True)
      #numnodes = dict(zip(unique, counts))
      #numnodes = numnodes[1]
      numnodes = np.count_nonzero(index == 1)
      singlenodeforce = force/numnodes
      nodeforce[index] = singlenodeforce
    nodeForceList[i] = nodeforce
  return nodeForceList

def importLoadsFile(filename,criticalvalue,variables=['Fx','Fy','Fz','Mx','My','Mz','Fxy','Mxy']):
  df  = pd.read_excel(filename,sheet_name='RotorEnvelope',header=1)
  df3 = pd.read_excel(filename,sheet_name='DLC-MaxTip',header=5)
  df.rename(columns={'Unnamed: 0':'LoadCase'},inplace=True)
  
  etaSeries = df['Fx'][df.Fx.str.startswith('Envel').fillna(False)].tolist()
  eta = np.zeros(len(etaSeries)+1)
  for i in range(len(etaSeries)):
    temp = etaSeries[i].split()
    eta[i+1] = temp[temp.index('=')+1]
    
  loadcases = list(df['LoadCase'].dropna().unique())
  
  # Extract Load Cases
  loadcaseValues = [None]*len(loadcases)
  for i, case in enumerate(loadcases):
    index = df['LoadCase'] == case
    temp = {}
    for variable in variables:
      temp[variable] = df[variable][index].to_numpy().astype(float)
    loadcaseValues[i] = temp
  
  # Add DLC-MaxTip load case
  index = np.argwhere(np.round(df3['Unnamed: 0'].to_numpy(),2) == criticalvalue)[0][0]
  tempFx, tempFy, tempFz, tempMz = np.zeros(len(eta)), np.zeros(len(eta)), np.zeros(len(eta)), np.zeros(len(eta))
  for i in range(len(eta)):
    suffix = ''
    if i > 0:
      suffix = '.{0}'.format(i)
    tempFx[i] = df3['Fx [N]' + suffix][index]
    tempFy[i] = df3['Fy [N]' + suffix][index]
    tempFz[i] = df3['Fz [N]' + suffix][index]
    tempMz[i] = df3['Mz [Nm]' + suffix][index]
  criticalcase = {'Fx':tempFx,'Fy':tempFy,'Fz':tempFz,'Mz':tempMz}
  loadcaseValues.append(criticalcase)
  loadcases.append('DLC-MaxTip')
  return loadcaseValues,loadcases


"""
      etalocal = correctedz[i]/bladelen
      maxxlocal = np.interp(etalocal,eta55,maxx)
    minxlocal = np.interp(etalocal,eta55,minx)
    xc = min(1,max(0,(maxxlocal-nodex[i])/(maxxlocal-minxlocal)))
    ind0 = np.abs(eta - etalocal).argmin()
    if eta[ind0] - etalocal <0:
      ind1 = ind0+1
    elif eta[ind0] == etalocal:
      #nodepressure[i] = np.interp(xc,xArray[zeroindex:,ind0],pressure[zeroindex:,ind0])      
      ind1 = ind0
      #continue
    else:
      ind1 = ind0
      ind0 = ind0-1
    if bottomnodes[i] == 1:
      pressure1 = np.interp(xc,xArray[zeroindex:,ind0],pressure[zeroindex:,ind0])
      pressure2 = np.interp(xc,xArray[zeroindex:,ind1],pressure[zeroindex:,ind1])
    elif topnodes[i] == 1:
      pressure1 = np.interp(xc,np.flip(xArray[:zeroindex+1,ind0]),np.flip(pressure[:zeroindex+1,ind0]))
      pressure2 = np.interp(xc,np.flip(xArray[:zeroindex+1,ind1]),np.flip(pressure[:zeroindex+1,ind1]))
    else:
      continue
    nodepressure[i] = np.interp(etalocal,
                                np.array([eta[ind0],eta[ind1]]),
                                np.array([pressure1,pressure2]))
  return nodepressure
                                """