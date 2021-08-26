import os,csv,sys
libpath = os.path.dirname(os.path.realpath(__file__))
if libpath not in sys.path:
  sys.path.append(libpath)
import openfastInterface as ofi
import numpy as np

def createTempFiles(filename,outputfilename,values):
  with open(filename) as inputfile:
    content = inputfile.read()
    outputstring = content % values #.format(*values.items())#format(**values)
    with open(outputfilename,'w') as outputfile:
      outputfile.write(outputstring)

def xfoilRun(foil,wd,Re,M,Alpha,xfoilexe='xfoil',filename='xfoil_template.inp',
             tempfilename='TEMP_xfoil.inp',outputfilename='TEMP_xfoil.out',cpfile='TEMP_xfoil_cpwr.dat'):
  params = {'Re':Re, 'Mach':M, 'AOA':Alpha, 'foilFile':foil}
  os.chdir(wd)
  createTempFiles(filename,tempfilename,params)
  os.system("%s < %s > %s" % (xfoilexe,tempfilename,outputfilename))
  x  = ofi.importTxtFileNumpy(cpfile,1,2,10000)
  cp = ofi.importTxtFileNumpy(cpfile,2,2,10000)
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

"""
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
"""
def interpFoils(foil1,foil2,ratio,outputname,wd,xfoilexe='xfoil',tempinp='interp.inp'):
  os.chdir(wd)
  inptext = ''
  reptext = 'inte\nf\n{foil1}.foil\nf\n{foil2}.foil\n{ratio}\n{name}\npcop\nsave\n{name}.foil\ny\n'
  try:
    for i in range(len(ratio)):
      inptext = inptext + reptext.format(foil1=foil1[i],foil2=foil2[i],ratio=ratio[i],name=outputname[i])
  except:
    inptext = reptext.format(foil1=foil1,foil2=foil2,ratio=ratio,name=outputname)
  inptext = inptext + 'quit\n'
  with open(tempinp,'w') as outputfile:
    outputfile.write(inptext)
  os.system("%s < %s" % (xfoilexe,tempinp,))

def foil2numad(foilnames,xfoildir,numadAFdir,flatbacks=[]): # foilnames should match outputname in interpFoils
  if type(foilnames) == str:
    foilnames = [foilnames]
  for i in range(len(foilnames)):
    x = ofi.importTxtFileNumpy(os.path.join(xfoildir,foilnames[i]+'.foil'),1)
    y = ofi.importTxtFileNumpy(os.path.join(xfoildir,foilnames[i]+'.foil'),2)
    x = np.maximum(np.minimum(x,1),0)
    if x[0] == x[-1] and y[0] == y[-1]:
      x = x[:-1]
      y = y[:-1]
    if i in flatbacks: 
      x[0]  = 1
      x[1]  = 1
      x[-1] = 1
    elif x[0] == 1 and x[-1] == 1: # for this circumstance, the foil is a flatback foil
      if x[1] == 1:
        print(foilnames[i],'is already flatback')
        pass
      elif y[0] >=0 or y[-1] <=0:
        print('Unable to create flatback foil for',foilnames[i])
        x[-1] = .999999
      else:
        x = np.insert(x,0,1)
        y = np.insert(y,0,0)
        print('Flatback foil created for',foilnames[i])
    else:
      print(foilnames[i],'is not a flatback foil')
    outputstr = '<reference>%s</reference>\n<coords>\n' % (foilnames[i],)
    for j in range(len(x)):
      outputstr = outputstr + '{:.7e}'.format(x[j]).rjust(16) + '{:.7e}\n'.format(y[j]).rjust(16)
    outputstr = outputstr + '</coords>\n'
    with open(os.path.join(numadAFdir,foilnames[i]+'.txt'), 'w') as outputfile:
      outputfile.write(outputstr)

def flatbackFoils(xfoildir,foilnames):
  if type(foilnames) == str:
    foilnames = [foilnames]
  outputbool = [False]*len(foilnames)
  for i in range(len(foilnames)):
    x = ofi.importTxtFileNumpy(os.path.join(xfoildir,foilnames[i]+'.foil'),1)
    y = ofi.importTxtFileNumpy(os.path.join(xfoildir,foilnames[i]+'.foil'),2)
    if x[0] == 1 and x[1] == 1:
      if x[0] == x[-1] and y[0] == y[-1]:
        if x[-2] == 1:
          outputbool[i] = True
      else:
        if x[-1] == 1:
          outputbool[i] = True
  return np.array(outputbool)