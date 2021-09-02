import sys,os,csv
import numpy as np
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import openfastInterface as ofi

ansysfolder = os.path.join(wd,'ansys')
dirs = [f.path for f in os.scandir(ansysfolder) if f.is_dir()]

values = []
materials = []
labels = []
for folder in dirs:
  #folder = os.path.join(wd,'ansys','IEAblade_nm03_lattice3x_optimized')
  filename = os.path.join(folder,'ALIST.lis')
  if not os.path.isfile(filename):
    continue
  
  alistesize = ofi.importTxtFileNumpy(filename,8)
  alistelnum = ofi.importTxtFileNumpy(filename,10).astype(int)
  alistsecn  = ofi.importTxtFileNumpy(filename,15).astype(int)
  alistarea  = ofi.importTxtFileNumpy(filename,7).astype(float)
  
  density = np.array([])
  matnames = []
  with open(os.path.join(folder,'shell7.src')) as file:
    content = file.readlines()
    for row in content:
      if '!' in row:
        temp = row.split('!')
        currentmat = temp[-1]
      if 'mp,dens' in row:
        temp = row.split(',')
        matnames.append(currentmat.strip())
        density = np.append(density,float(temp[-1]))
      

  filename = os.path.join(folder,'SLIST.lis')
  matIDs   = np.unique(ofi.importTxtFileNumpy(filename,3)).astype(int)  
  
  sectids   = []
  sectthick = []
  sectmatid = []
  #layers = []
  with open(filename) as file:
    content = csv.reader(file, delimiter=' ')
    for row in content:
      row = [i for i in row if i]
      if 'SECTION' in row and 'NUMBER:' in row:
        currentsect = int(row[-1])
      elif len(row)>0:
        try:
          temp = int(row[0])
          sectids.append(currentsect)
          sectthick.append(float(row[1]))
          sectmatid.append(int(row[2]))
        except:
          continue
  sectids = np.array(sectids)
  sectmatid = np.array(sectmatid)
  sectthick = np.array(sectthick)
  
  BOMvol = np.zeros(max(matIDs))#len(matIDs))
  for (secnum,secarea) in zip(alistsecn,alistarea):
    index = np.where(sectids == secnum)[0]
    try:
      for (matid,thickness) in zip(sectmatid[index],sectthick[index]):
        BOMvol[matid-1] = BOMvol[matid-1] + thickness*secarea # Note this assumes materials are numbered 1-N with no skips
    except:
      matid = sectmatid[index]
      BOMvol[matid-1] = BOMvol[matid-1] + sectthick[index]*secarea
  
  BOMmass = density*BOMvol
  values.append(BOMmass)
  materials.append(matnames)
  labels.append(os.path.basename(folder))

#%%
gelcoatmass = values[2][np.where(np.array(materials[2]) == 'Gelcoat')[0][0]]
keycases = []
uniquemats = []
for i,(material,value) in enumerate(zip(materials,values)):
  if 'Gelcoat' not in material:
    material.append('Gelcoat')
    values[i] = np.append(value,gelcoatmass)
  else:
    try:
      index = np.where(np.array(material) == 'Gelcoat')[0][0]
      if value[index] == 0:
        value[index] = gelcoatmass
    except:
      continue
  uniquemats = uniquemats + material
uniquemats = list(np.unique(uniquemats))

#%%
with open(os.path.join(wd,'output.csv'),'w') as file:
  csvwriter = csv.writer(file)
  csvwriter.writerow([''] + labels)
  for material in uniquemats:
    rowvalues = []
    for i,value in enumerate(values):
      try:
        index = np.where(np.array(materials[i]) == material)[0][0]
        rowvalues.append(value[index])
      except:
        rowvalues.append(0)
    csvwriter.writerow([material] + rowvalues)