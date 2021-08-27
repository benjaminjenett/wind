import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

wd = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(wd,'IEAonshore.xlsx')
sheetname = 'Airfoils'
df = pd.read_excel(filename,sheet_name = sheetname)

def polyArea(x,y):
  return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

#%%
Xlabel = 'Airfoil Name'
Ylabel = 'Span Positioning'

suffix = ['','.1','.2','.3','.4','.5','.6','.7','.8']
airfoilLabel = [None]*len(suffix)
coordsX = [None]*len(suffix)
coordsY = [None]*len(suffix)
enclosedArea = np.zeros(len(suffix))
Iflaplist = [None]*len(suffix)
Iedgelist = [None]*len(suffix)

plt.figure()

for i in range(len(suffix)):
  Xcol = df[Xlabel+suffix[i]]
  Ycol = df[Ylabel+suffix[i]]
  airfoilLabel[i] = Xcol[1]
  cx = Xcol[4:].to_list()
  cx = np.array(cx)
  cx = cx[~np.isnan(cx)]
  cy = Ycol[4:].to_list()
  cy = np.array(cy)
  cy = cy[~np.isnan(cy)]
  coordsX[i] = cx
  coordsY[i] = cy
  enclosedArea[i] = polyArea(cx,cy)
  plt.plot(cx,cy)
  print('Airfoil: %s, Area: %s' % (airfoilLabel[i],np.round(enclosedArea[i],6)))
  Iflap = 0
  Ibend = 0
  centroidFlap = 0
  centroidEdge = 0
  for j in range(len(cx)-1):
    centroidFlap = centroidFlap + .5/enclosedArea[i] * (cx[j] - cx[j+1])*cy[j]**2
  #for j in range(np.floor(len(cx)/2)):
  #  centroidEdge = centroidEdge + .5/enclosedArea[i] * abs(cy[j] - cy[-j-1])
  for j in range(len(cx)-1):
    Iflap = Iflap + (cx[j] - cx[j+1])*(cy[j]-centroidFlap)**3/3
  Iflaplist[i] = Iflap
plt.grid()
plt.show()
#plt.legend(airfoilLabel)