import xmltodict
from collections import OrderedDict

def numadImport(numadfilename,ret = None):
  with open(numadfilename) as fd:
    doc = xmltodict.parse(fd.read())
    if ret == 'blade' or ret == 'ansys' or ret == 'activematerials':
      return doc['numad'][ret]
    elif ret == 'precurve' or ret == 'presweep' or ret == 'shearweb' or ret == 'station':
      return doc['numad']['blade'][ret]
    elif ret == 'numad':
      return doc['numad']
    else:
      return doc
  print('File not found or opened')
  
def matImport(filename,mattype=None):
  with open(filename) as fd:
    contents = fd.read()
    contents = '<?xml version="1.0" encoding="UTF-8" ?>\n<materials>\n' + contents + '</materials>'
    doc = xmltodict.parse(contents)
  outputdoc = []
  if mattype == 'basic':
    for value in doc['materials']['material']:
      if value['type'] != 'composite':
        outputdoc.append(value)
  elif mattype is not None:
    for value in doc['materials']['material']:
      if value['type'] == mattype:
        outputdoc.append(value)
  else:
    outputdoc = doc
  return outputdoc

def matExport(content,filename):
  output = OrderedDict([('materials',OrderedDict([('material',content)]))])
  output = xmltodict.unparse(output,pretty=True)
  output = output.replace('\n\t','\n').replace('\t','   ')
  output = output.split('\n')
  output = '\n'.join(output[2:-1])
  with open(filename,'w') as file:
    file.write(output)

def numadExportXml(od):
  text = xmltodict.unparse(od,pretty=True)
  index = text.find('<numad')
  text = text[index:] + '\n'
  text = text.replace('\t\t\t','    ')
  text = text.replace('\t\t','  ')
  text = text.replace('\t','')
  return text

def changeLayer(matlist,changeind,factor,minvalue=0,maxvalue=None):
  pass

def changeCore(inputfile,outputfile,oldcore,newcore,factor,minvalue=0,maxvalue=None):
  materials = matImport(inputfile,'composite')
  othermats = matImport(inputfile,'basic')
  for i,mat in enumerate(materials):
    if type(mat['layer']) == OrderedDict:
      continue
    for j,layer in enumerate(mat['layer']):
      if layer['layerName'] == oldcore:
        layer['layerName'] = newcore
        thicknessA = max(minvalue,float(layer['thicknessA'])*factor)
        thicknessB = max(minvalue,float(layer['thicknessB'])*factor)
        if maxvalue is not None:
          thicknessA = min(maxvalue,thicknessA)
          thicknessB = min(maxvalue,thicknessB)
        layer['thicknessA'] = thicknessA
        layer['thicknessB'] = thicknessB
  matExport(othermats + materials,outputfile)

def splitLayers(inputfile,outputfile):
  materials = matImport(inputfile,'composite')
  othermats = matImport(inputfile,'basic')
  for i,mat in enumerate(materials):
    if mat['layer'][0]['layerName'] == 'Gelcoat':
      gelind = 1
      mat['uniqueLayers'] = 2*(int(mat['uniqueLayers'])-1)
      layers = [None]*mat['uniqueLayers']
      layers[0] = mat['layer'][0]
      #layers[:len(mat['layer']] = mat['layer']
    else:
      gelind=0
      mat['uniqueLayers'] = 2*int(mat['uniqueLayers'])-1
      layers = [None]*mat['uniqueLayers']
    layers[len(mat['layer'])-1] = mat['layer'][-1]
    for j in range(len(mat['layer'])-1-gelind):
      layers[j+gelind] = mat['layer'][j+gelind]
      layers[j+gelind]['thicknessA'] = float(mat['layer'][j+gelind]['thicknessA'])/2
      layers[j+gelind]['thicknessB'] = float(mat['layer'][j+gelind]['thicknessB'])/2
      layers[-j-1] = layers[j+gelind]
    mat['layer'] = layers
  matExport(othermats + materials,outputfile)

def removeLayers(removeitem,inputfile,outputfile):
  materials = matImport(inputfile,'composite')
  othermats = matImport(inputfile,'basic')
  for i,mat in enumerate(materials):
    for j,layer in enumerate(mat['layer']):
      if layer['layerName'] == removeitem:
        mat['uniqueLayers'] = int(mat['uniqueLayers'])-1
        mat['layer'].pop(j)
        continue
  matExport(othermats + materials,outputfile)

"""
def nodeCat(matlist,searchID = None, loc = None):
  if type(searchID) == str:
    searchID = [searchID]
    
  if loc == None:
    topbottom = {'HP_CAP':'Cap', 'HP_FLAT':'Bottom', 'HP_LE_REINF':'Bottom', 'HP_TE_REINF':'Bottom',
                 'LE_PS_FILLER':'Bottom', 'LE_SS_FILLER':'Top', 'LP_CAP':'Cap', 'LP_FLAT':'Top',
                 'LP_LE_REINF':'Top', 'LP_TE_REINF':'Top', 'SW1':'Web', 'SW2':'Web','SW':'Web',
                 'SW_36':'Web','SW_37':'Web', 'SW_1_HP':'Cap','SW_1_LP':'Cap', 'SW_2_HP':'Cap',
                 'SW_2_LP':'Cap', 'TE-PS-Filler':'Bottom','TE_SS_filler':'Top','HP_TE_FILLER':'Bottom',
                 'HP_LE_FILLER':'Bottom','LP_TE_FILLER':'Top','LP_LE_FILLER':'Top','LE_REINF':'Top'}
"""