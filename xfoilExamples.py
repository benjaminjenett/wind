import os,sys
wd = os.path.dirname(os.path.realpath(__file__))
libpath = os.path.join(wd,'lib')
if libpath not in sys.path:
  sys.path.append(libpath)
import xfoilInterface as xi

xfoildir = os.path.join(wd,'xfoil')

foilfile = 'FX77-W-500.foil'
Re = 3000000
Mach = .2
Alpha = 4
VRel = 40
rho_air = 1.225
x,cp = xi.xfoilRun(foilfile,xfoildir,Re,Mach,Alpha)
pressure = .5 * cp * VRel * rho_air
