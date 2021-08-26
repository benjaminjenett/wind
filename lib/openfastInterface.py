import subprocess
import pandas as pd
import io
import os,csv
#if '/home/colin/Documents/DLI/lib' not in sys.path:
#  sys.path.append('/home/colin/Documents/DLI/lib')
#import readOpenfastCoords as ro
import numpy as np

#%% Setup functions
def paramsDict(listlength,**kwargs):
  outputList = [{} for sub in range(listlength)]
  for arg in kwargs:
    try:
      for j in range(len(kwargs[arg])):
        outputList[j][arg] = kwargs[arg][j]
    except:
      for j in range(listlength):
        outputList[j][arg] = kwargs[arg]
  return outputList

def createTempFiles(filename,outputfilename,values):
  with open(filename) as inputfile:
    content = inputfile.read()
    outputstring = content % values #.format(*values.items())#format(**values)
    with open(outputfilename,'w') as outputfile:
      outputfile.write(outputstring)

def readOutputFile(filename):
  with open(filename) as inputfile:
    content = inputfile.readlines()
    contentstring = content[6] + ''.join(content[8:])
    data = io.StringIO(contentstring)
    df = pd.read_csv(data,sep='\t')
  return df

def runOpenfast(masterfile,templatefn,fileLabels,variables):#tempFile,templateFile
  tempFile = (fileLabels[0],'')
  templateFile = ('',fileLabels[1])
  resultsfile = masterfile[:-3] + 'out'
  if type(variables) is dict:
    variables = [variables]
  df = [None]*len(variables)
  for i in range(len(variables)):
    for j in range(len(templatefn)):
      createTempFiles(templatefn[j] % templateFile,templatefn[j] % tempFile,variables[i]) # e.g. 'IEA-3.4-130-RWT_template.fst'
    subprocess.run(["openfast",masterfile])
    df[i] = readOutputFile(resultsfile)
    df[i] = df[i].assign(LoadCaseIndex=i)
  df = pd.concat(df,axis=0).reset_index()
  return df

def dfMaxMinIndex(df,crit):
  index = []
  for i in range(len(crit)):
    index.append(df[crit[i]].idxmin())
    index.append(df[crit[i]].idxmax())
  return index

def dfReturnPoints(df,crit,minmax):
  for i in range:
    print(i)
    
def normTanForce(df,totalpoints):#filenamebase,folder,numfiles,totalpoints):
  liftName = 'AB1N%03.0fFl'
  dragName = 'AB1N%03.0fFd'
  phiName  = 'AB1N%03.0fPhi'  
  
  tangentForce = [None]*len(df)
  normalForce  = [None]*len(df)
  
  for i in range(len(df)):
    tForce = [None]*totalpoints
    nForce = [None]*totalpoints
    for j in range(totalpoints):
      lift = df[liftName % (j+1,)].to_numpy()[i]
      drag = df[dragName % (j+1,)].to_numpy()[i]
      phi  = df[phiName  % (j+1,)].to_numpy()[i]
      nForce[j] = lift*np.cos(np.deg2rad(phi))+drag*np.sin(np.deg2rad(phi))
      tForce[j] = lift*np.sin(np.deg2rad(phi))-drag*np.cos(np.deg2rad(phi))
    tangentForce[i] = tForce
    normalForce[i]  = nForce
  return normalForce,tangentForce

def xfoilRun(foil,wd,Re,M,Alpha):
  params = {'Re':Re, 'Mach':M, 'AOA':Alpha, 'foilFile':foil}
  os.chdir(wd)
  createTempFiles('xfoil_template.inp','TEMP_xfoil.inp',params)
  os.system("xfoil < TEMP_xfoil.inp > TEMP_xfoil.out")
  cp = importTxtFileNumpy('TEMP_xfoil_cpwr.dat',2,2,10000,delimiter=' ')
  x  = importTxtFileNumpy('TEMP_xfoil_cpwr.dat',1,2,10000,delimiter=' ')
  return x,cp

def importAirfoil(folder,startline=9):
  fileList = []
  listoflists = []
  for file in os.listdir(folder):
    if file.endswith(".txt"):
      tempoutput = []
      fileList.append(file)
      with open(folder+file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        for row in csv_reader:
          row = [i for i in row if i]
          tempoutput.append(row)
      tempoutput = tempoutput[startline-1:]
      for row in tempoutput:
        row[:] =[float(a) for a in row]
      listoflists.append(np.array(tempoutput))       
  return listoflists,fileList

def afxy(folder,chord=1):
  coordslist,_ = importAirfoil(folder)
  x = np.zeros([len(coordslist[0]),len(coordslist)])
  y = np.zeros([len(coordslist[0]),len(coordslist)])
  for i in range(len(coordslist)):
    x[:,i] = coordslist[i][:,0]
    y[:,i] = coordslist[i][:,1]
  return x*chord,y*chord

#def importTxtFileNumpy(filename,startline,endline,column,delimiter=' '):
def importTxtFileNumpy(filename,column,startline=None,endline=None,delimiter=' ',includeNAN=False):
  tempoutput = []
  with open(filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    for row in csv_reader:
      row = [i for i in row if i]
      try:
        tempoutput.append(float(row[column-1]))
      except:
        if includeNAN:
          tempoutput.append([])
  if startline is None:
    startline = 1
  if endline is None:
    tempoutput = tempoutput[startline-1:]
  else:
    tempoutput = tempoutput[startline-1:endline]
  ar = np.array(tempoutput)
  return ar

def importTxtFileDict(filename,startline,endline,headerline = None,delimiter=' '):
  if headerline is None:
    headerline = startline - 2
  outputDict = {}
  tempoutput = []
  with open(filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=delimiter)
    for row in csv_reader:
      row = [i for i in row if i]
      try:
        tempoutput.append(row)
      except:
        tempoutput.append([None])
  keys = tempoutput[headerline-1]
  for key in keys:
    outputDict[key] = np.array([])
  for row in tempoutput[startline-1:endline]:
    for i in range(len(keys)):
      outputDict[keys[i]] = np.append(outputDict[keys[i]],float(row[i]))
  return outputDict

def bladeProperties(openfastFolder = '/home/colin/Documents/DLI/IEA-3.4-130-RWT/openfast/',
                    edFile = 'IEA-3.4-130-RWT_ElastoDyn_blade.dat',
                    adFolder = 'IEA-3.4-130-RWT_AeroDyn15_blade.dat'):
  bl  = importTxtFileDict(openfastFolder + edFile,17,46)
  bl |= importTxtFileDict(openfastFolder + adFolder,7,36)
  return bl
