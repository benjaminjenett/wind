#%% Append path
import sys,os
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
sys.path.append("/home/colin/Source/lib/")
#%% Setup and import data
import numpy as np
import pandas as pd
import readOpenfastCoords as rofc
import composites as cm
import airfoilcalcs as afc
import matplotlib.pyplot as plt
import importLoads as il

openfastFolder = os.path.join(wd,'openfast')
openfastAirfoilFolder = os.path.join(openfastFolder,'Airfoils')

#%% read openfast input data
afCoords30,_ = rofc.importAirfoil(openfastAirfoilFolder)
eta30 = rofc.importTxtFileNumpy(openfastFolder+'IEA-3.4-130-RWT_ElastoDyn_blade.dat',17,46,1)
chord30 = rofc.importTxtFileNumpy(openfastFolder+'IEA-3.4-130-RWT_AeroDyn15_blade.dat',7,36,6)

#%% import blade properties from trade study document
filename = os.path.join(wd,'TradeStudyDocs','Product Trade Study Data.xlsx')
dfts = pd.read_excel(filename,sheet_name = 'IEA 63')
eta55 = dfts['eta'].to_numpy()
chord55 = dfts['Chord (mm)'].to_numpy()*1e-3
thickness55 = dfts['Abs. Thick (mm)'].to_numpy()*1e-3
#interpList= dfts['InterpRatio'].to_numpy()
#airfoil1  = dfts['Airfoil1'].to_list()
#airfoil2  = dfts['Airfoil2'].to_list()
EI_flap_iea  = dfts['E11 (flapwise) (Nm2)']
EI_flap_lat_xls = dfts['E11 (Lattice)']
mass = dfts['Mass (kg/m)'].to_numpy()
del dfts,filename

#%% import from IEAonshore.xlsx
filename = os.path.join(wd,'IEAonshore.xlsx')
dfiea_bct = pd.read_excel(filename,sheet_name = 'BladeCompThickness')
skinThickness55 = dfiea_bct['Thickness Shell Skin on Trailing Edge Suction Side'][1:len(eta55)+1].to_numpy().astype(float)
sparcapThickness55 = dfiea_bct['Thickness Suction Spar Cap'][1:len(eta55)+1].to_numpy().astype(float)
frontShearwebThickness55 = dfiea_bct['Thickness Front Web'][1:len(eta55)+1].to_numpy().astype(float)
rearShearwebThickness55  = dfiea_bct['Thickness Rear Web' ][1:len(eta55)+1].to_numpy().astype(float)
frontShearwebBalsa55 = dfiea_bct['Thickness Sandwich Core Front Web'][1:len(eta55)+1].to_numpy().astype(float)
rearShearwebBalsa55  = dfiea_bct['Thickness Sandwich Core Rear Web' ][1:len(eta55)+1].to_numpy().astype(float)

#%% Loads
filenamebase = 'IEA-3.4-130-RWT_%s-%s.csv'
numfiles = 5
totalpoints = 30

normalForce,mintangentForce,maxtangentForce = il.openfastNormTanForce(filenamebase,openfastFolder,numfiles,totalpoints)

#%% Initialize constants

E11_UD_caps = 42000e6 #Pa
E22_UD_caps = 12300e6 #Pa
nu12_UD_caps = .31
G12_UD_caps = 3470e6  #Pa
rho_UD_caps = 1940
lamS_UD_caps,lamQ_UD_caps = cm.sqGenerate(E11_UD_caps,E22_UD_caps,G12_UD_caps,nu12_UD_caps)

E11_triax  = 21790e6
E22_triax  = 14670e6
nu12_triax = .48
G12_triax  = 9413e6
rho_triax = 1845
lamS_triax,lamQ_triax = cm.sqGenerate(E11_triax,E22_triax,G12_triax,nu12_triax)

E11_biax  = 13920e6
E22_biax  = 13920e6
nu12_biax = .53
G12_biax  = 11500e6
rho_biax = 1845
lamS_biax,lamQ_biax = cm.sqGenerate(E11_biax,E22_biax,G12_biax,nu12_biax)

E_balsa = 50e6
G_balsa = 150e6
rho_balsa = 110
nu_balsa = .4999

maxLamThick = 41.5e-3*2 #m, based on the max laminate thickness in the DTU 10MW turbine
# from NRT blade, max laminate thickness is 13.9mm

Urated = 9.8
rho_air = 1.225

Elattice  = 62.5541579e6*.1
nulattice = .15
Glattice  = Elattice/(2*(1+nulattice))
rholattice_05 = 1390*.05
rholattice = 1390*.05*.1

skint = 1e-3
sparcap_t = 13.9e-3-skint
width_sparcap = .8
width_sparcap_lat30 = np.minimum(np.ones(len(chord30))*width_sparcap,chord30*.75)

bladelen = 63
hubrad = 2
R = bladelen+hubrad

latticeS,latticeQ = cm.sqGenerate(Elattice,Elattice,Glattice,nulattice)

ABD_skin = cm.ABD([lamQ_triax],[-skint/2,skint/2],[0])
abd_skin = np.linalg.inv(ABD_skin)
ABD_sparcap = cm.ABD([lamQ_UD_caps],[-sparcap_t/2,sparcap_t/2],[0])
abd_sparcap = np.linalg.inv(ABD_sparcap)
  
"""
#%% sandwich caps

sparcapsEIlist = [None]*len(eta55)
thicknessfactor = .9

for i in range(len(eta55)):
  coret = sparcapThickness55[i]-2*skint
  total_h = thickness55[i]*thicknessfactor
  fullLatticet = total_h-2*sparcapThickness55[i]
  d = coret+skint
  dfull = fullLatticet+coret
  ABDlattice = cm.ABD([latticeQ],[-coret/2,coret/2],[0])
  ABDfulllattice = cm.ABD([latticeQ],[-fullLatticet/2,fullLatticet/2],[0])
  Askin = ABDlattice[:3,:3]+2*ABD_skin[:3,:3]
  Dskin = ABDlattice[3:,3:]+2*ABD_skin[3:,3:]+.5*d**2*ABD_skin[:3,:3]
  
  Acaps = 2*Askin+ABDfulllattice[:3,:3]
  acaps = np.linalg.inv(Acaps)
  Dcaps = ABDfulllattice[3:,3:]+2*Dskin+.5*dfull**2*Askin
  dcaps = np.linalg.inv(Dcaps)
  
  zb = total_h/2
  EIfl = width_sparcap/dcaps[0,0]
  Ex = 1/(acaps[0,0]*sparcapThickness55[i])
  Ey = 1/(acaps[1,1]*sparcapThickness55[i])
  nuxy = -acaps[0,1]/acaps[0,0]
  Gxy = 1/(acaps[2,2]*sparcapThickness55[i])
  capS,_ = cm.sqGenerate(Ex,Ey,Gxy,nuxy)
  sparcapsEIlist[i],_ = cm.eiea([width_sparcap,width_sparcap,fullLatticet],[sparcapThickness55[i],sparcapThickness55[i],width_sparcap],zb,[EIfl]*2,'I',[capS,capS,latticeS])
"""
#%% calculate using openfast profiles
rootCapThick = maxLamThick*.75
sparcap_tList = rootCapThick - eta30*(rootCapThick)

EI_flap_latskin1 = np.zeros(len(afCoords30))
EI_flap_latcap1  = np.zeros(len(afCoords30))
masslist = np.zeros(len(afCoords30))
perimlen = np.zeros(len(afCoords30))
masslistCaps = np.zeros(len(afCoords30))
secarea30 = np.zeros(len(afCoords30))
for j in range(len(afCoords30)):
  chord = chord30[j]
  cx = afCoords30[j][:,0]
  cy = afCoords30[j][:,1]
  endIndex = np.where(cx==0)[0][0]
  secarea30[j] = afc.afArea(cx,cy,chord)

  temp_EI = np.zeros(endIndex)
  maxh = skinThickness55[ii]
  skint_over_chord = skint/chord
  temp_EI[i],_ = cm.eiea([b,b,h],[skint_over_chord,skint_over_chord,b],zb,[EIfl]*2,'I',[lamS_triax,lamS_triax,latticeS])
  EI_total = sum(temp_EI)
  EI_flap_latskin1[j] = chord**4*EI_total
  b = width_sparcap_lat30[j]
  sparcap_t = sparcap_tList[j]
  if not sparcap_t == 0:
    ABD_sparcap = cm.ABD([lamQ_UD_caps],[-sparcap_t/2,sparcap_t/2],[0])
    abd_sparcap = np.linalg.inv(ABD_sparcap)
    EIfl = b/(abd_sparcap[3,3])
    EI_flap_latcap1[j],_  = cm.eiea([b,b,maxh-2*sparcap_t],[sparcap_t,sparcap_t,b],maxh/2,[EIfl]*2,'I',[lamS_UD_caps,lamS_UD_caps,latticeS*1e9])
    masslistCaps[j] = 2*b*rho_UD_caps*sparcap_t
  perimlen[j] = afc.afPerim(cx, cy, chord)#sum(np.sqrt((cx[:-1]-cx[1:])**2+(cy[:-1]-cy[1:])**2)) + np.sqrt((cx[0]-cx[-1])**2+(cy[0]-cy[-1])**2)
  masslist[j] = perimlen[j]*rho_UD_caps*skint + rholattice*secarea30[j]
  #masslistCaps[j] = 2*perimlen[j]*rho_UD_caps*skint + rholattice*secarea30[j]
plt.plot(eta55,EI_flap_iea)
plt.plot(eta30,EI_flap_latskin1)
plt.plot(eta55,EI_flap_lat_xls)
plt.plot(eta30,EI_flap_latcap1+EI_flap_latskin1)
plt.yscale('log')
plt.xlabel(r'$\eta$')
plt.ylabel(r'EI (Nm$^2$)')
plt.title('Blade stiffness')
plt.legend(['As Designed','Lattice w/skin, t = %s mm' %(skint*1e3,),r'Pure Lattice $​\bar{\rho}$ = .05','Spar caps, linear taper\nfrom %s mm to 0' %(round(rootCapThick,15)*1e3,)])
plt.show()

plt.figure()
plt.plot(eta55,mass)
plt.plot(eta30,masslist)
plt.plot(eta30,secarea30*rholattice_05)
plt.plot(eta30,masslistCaps+masslist)
plt.title('Blade Mass')
plt.xlabel(r'$\eta$')
plt.ylabel('Mass/Length (kg/m)')
plt.legend(['As Designed','Lattice w/skin, t = %s mm' %(skint*1e3,),r'Pure Lattice $​\bar{\rho}$ = .05','Spar caps, linear taper\nfrom %s mm to 0' %(round(rootCapThick,15)*1e3,)])

#%% calculate stiffness of box beam only (spar cap+skin, shear webs)
EI_flap_boxbeam = np.zeros(len(eta55))
mass_boxbeam = np.zeros(len(eta55))
mass_caps = np.zeros(len(eta55))
mass_webs = np.zeros(len(eta55))
mass_webbalsa = np.zeros(len(eta55))
for i in range(len(EI_flap_boxbeam)):
  if thickness55[i] == 0 or frontShearwebThickness55[i] == 0:
    continue
  capt = sparcapThickness55[i]*1e-3
  webt = (frontShearwebThickness55[i]+rearShearwebThickness55[i])*1e-3
  h = thickness55[i]-capt*2
  ABD_temp = cm.ABD([lamQ_UD_caps],[-capt/2,capt/2],[0])
  abd_temp = np.linalg.inv(ABD_temp)
  zb = thickness55[i]/2
  EIfl = width_sparcap/(abd_temp[3,3])
  EI_flap_boxbeam[i],_ = cm.eiea([width_sparcap,width_sparcap,h],
                                 [capt,capt,webt],
                                 zb,[EIfl]*2,'box',[lamS_UD_caps,lamS_UD_caps,lamS_biax])
  mass_boxbeam[i] = width_sparcap*capt*rho_UD_caps*2+webt*h*rho_biax
  mass_caps[i] = width_sparcap*capt*rho_UD_caps
  mass_webs[i] = webt*h*rho_biax
  mass_webbalsa[i] = (frontShearwebBalsa55[i] + rearShearwebBalsa55[i])*1e-3*h*rho_balsa

ind = np.where(mass_boxbeam != 0)
plt.figure()
plt.plot(eta55,mass)
plt.plot(eta55[ind],mass_boxbeam[ind])
plt.plot(eta55[ind],mass_caps[ind])
plt.plot(eta55[ind],mass_webs[ind])
plt.plot(eta55[ind],mass_webbalsa[ind])
plt.plot(eta30,secarea30*rholattice_05*.1)
plt.grid()
plt.legend(['As Designed','Box Beam','Spar Caps','Spar Webs','Spar Web Core',r'Lattice $​\bar{\rho}$ = .005'])
plt.yscale('log')

#%% Stresses as-designed
# Note: this model does not properly account for the shear deformation of the core

dr = np.zeros(len(eta30))
dr[0]  = (eta30[1] -eta30[0] )/2
dr[-1] = (eta30[-1]-eta30[-2])/2
dr[1:-1] = (eta30[2:]-eta30[0:-2])/2
dr = dr*bladelen

flapwiseMoment = np.zeros(len(eta30))
flapwiseShear  = np.zeros(len(eta30))
flapwise_dThdX = np.zeros(len(eta30))
flapwise_Th    = np.zeros(len(eta30))
flapwiseDeflection = np.zeros(len(eta30))
flapwisePeakStrain = np.zeros(len(eta30))
for ii in range(len(eta30)):
  flapwiseShear[ii]  = sum(normalForce[ii:]*dr[ii:])
  flapwiseMoment[ii] = sum((eta30[ii+1:]-eta30[ii])*normalForce[ii+1:]*dr[ii+1:])*bladelen
  flapwise_dThdX[ii] = -flapwiseMoment[ii]/np.interp(eta30[ii],eta55,EI_flap_iea)
  if ii > 1:
    flapwise_Th[ii] = flapwise_Th[ii-1] + flapwise_dThdX[ii-1]*dr[ii]
    flapwiseDeflection[ii] = flapwiseDeflection[ii-1]+flapwise_Th[ii-1]*dr[ii]

flapwisePeakStrain = flapwiseMoment * np.interp(eta30,eta55,thickness55) / (2*np.interp(eta30,eta55,EI_flap_iea))
peakSkinStress = E11_UD_caps*flapwisePeakStrain
flapwisePeakShearStress = 1.5*flapwiseShear*secarea30
flapwisePeakShearStrain = flapwisePeakShearStress/Glattice

shearwebShearStress = flapwiseShear / np.interp(eta30,eta55,thickness55*(frontShearwebThickness55+rearShearwebThickness55)*1e-6)
shearwebShearStrain = shearwebShearStress/G12_biax

#CT = 3*sum(normalForce*dr)/(.5*rho_air*Urated**2*np.pi*R**2)

#plt.figure()
#plt.plot(eta30,flapwisePeakStrain)
plt.figure()
plt.plot(eta30,peakSkinStress*1e-6)
plt.title('Peak Skin Stress')
plt.figure()
plt.plot(eta30,flapwiseDeflection)
plt.title('Flapwise Deflection')
plt.figure()
plt.plot(eta30,flapwiseMoment)
plt.title('Flapwise Moment')
plt.figure()
plt.plot(eta30,flapwisePeakShearStress*1e-6)
#plt.plot(eta30,shearwebShearStrain)
#plt.legend(['Lattice Strain','Shear Web Strain'])
plt.grid()
plt.title('Flapwise Shear Stress')

#%% Retrieve bending moments

dfdlc = pd.read_excel(filename,sheet_name = 'DLC-MaxTip')
dfdlc.columns = dfdlc.iloc[4]

m1 = np.array(dfdlc.iloc[5:2790,7 ].to_list())
m2 = np.array(dfdlc.iloc[5:2790,14].to_list())
m3 = np.array(dfdlc.iloc[5:2790,21].to_list())

m1ind = np.where(m1 == max(m1))[0][0]

stations = [0,.5,.8,.85,1]
maxBendingMoment = np.array([m1[m1ind],m2[m1ind],m3[m1ind],m3[m1ind]*.01,m3[m1ind]*.0001])*1.9e7/m1[m1ind]
flapwisePeakStrain2 = np.interp(eta30,stations,maxBendingMoment) * np.interp(eta30,eta55,thickness55) / (2*np.interp(eta30,eta55,EI_flap_iea))
plt.figure()
plt.plot(eta30,flapwisePeakStrain)
plt.plot(eta30,flapwisePeakStrain2)
plt.title('Peak Strain (Mc/EI)')
plt.legend(['Calculated','From DLC'])

plt.figure()
plt.plot(eta30,E11_UD_caps*flapwisePeakStrain2*1e-6)
#plt.plot(eta30,Elattice*1000*flapwisePeakStrain2*1e-6)
#plt.plot(eta30,peakSkinStress*1e-6)
plt.grid()
plt.title('Peak Stress for DLC13, 9m/s')
plt.ylabel('Stress (MPa)')
plt.xlabel(r'$\eta$ (values above .8 are approximate)')

"""#%%
sparcapWidth = chord55*.25
thicknessfactor = 1
skintList = maxLamThick*.5 - eta55*(maxLamThick*.5-skint)
panelEI = np.zeros(len(eta55))
for i in range(len(eta55)):
  z = cm.t2z([skintList[i],thickness55[i]*thicknessfactor-2*skintList[i],skintList[i]])
  panelABD = cm.ABD([lamQ_UD_caps,latticeQ,lamQ_UD_caps], z,[0,0,0])
  panelabd = np.linalg.inv(panelABD)
  panelEI[i] = sparcapWidth[i]/panelabd[3,3]

plt.figure()
plt.plot(eta55,panelEI)
plt.plot(eta55,EI_flap_iea)
plt.plot(eta55,EI_flap_lat_xls)
plt.legend(['Structural Skin','As Designed','Lattice Only'])
plt.yscale('log')"""

#%% Mass Target
matDensity = 1390
masstarget = np.interp(eta30,eta55,mass)/(secarea30*matDensity)

plt.figure()
plt.plot(eta30[:-1],masstarget[:-1])
plt.title('Maximum relative density for mass equivalence')
plt.grid()
plt.xlim([0,1])
plt.xlabel(r'$\eta$')
plt.ylabel(r'$\bar{\rho}$')

#%% Beam stiffness comparison
skinS,skinQ = cm.sqGenerate(E11_triax, E22_triax, G12_triax, nu12_triax)
balsaS,balsaQ = cm.sqGenerate(E_balsa, E_balsa, G_balsa, nu_balsa)

skinThickness  = .001
balsaThickness = .2 - skinThickness
latticeThickness = .4 - skinThickness

abdLattice = np.linalg.inv(cm.ABD([latticeQ],[-latticeThickness/2,latticeThickness/2],[0]))
abdBalsa   = np.linalg.inv(cm.ABD([balsaQ],  [-balsaThickness/2,balsaThickness/2],[0]))

zLattice = cm.centroidT([1,latticeThickness],[skinThickness,1],[skinS,latticeS])
zBalsa   = cm.centroidT([1,balsaThickness],  [skinThickness,1],[skinS,balsaS])
EIlattice,EAlattice = cm.eiea([1,latticeThickness],[skinThickness,1],zLattice,[1/abdLattice[3,3]],'T',[skinS,latticeS])
EIbalsa,EAbalsa = cm.eiea([1,balsaThickness],[skinThickness,1],zBalsa,[1/abdBalsa[3,3]],'T',[skinS,balsaS])
