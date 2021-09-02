# DLI Wind Energy Study
The files in this repository are the compilation of the primary files used for studying a lattice structure in a wind turbine blade. A more detailed analysis of the project can be found in [ProjectSummary.md](ProjectSummary.md).
## File Contents
The general contents of the repository are shown by folder below. As a general note, none of these files have been tested on more than one computer (Colin's computer).
Python files have only been tested with Linux (Ubuntu 21.04), and in some cases may need some modifications to run under Windows. The primary issue that I expect is that some file names and folder paths are hard coded in which need to be corrected (ideally using os.path.join or some similar method). Also, the Python files have only been tested in the Spyder IDE, which allows running of code sections, similar to matlab, and maintains variables for later use. Some code will run cleanly straight through, but others sometimes have certain sections which are broken.
Matlab code has been primarily tested in Windows 10, but should be cross-platform. Again, like in Python, there may be some areas where file names and folder paths are hard coded in which need to be adjusted.
### Top level files
In general, the top level directory currently contains various scripts that I have used for doing certain calculations, and various misc files. In most cases, these files will depend on libraries in the lib folder, and also as-written are directory structure dependent, so if files are moved around, they will need to have file/folder paths adjusted to maintain function.
### ansys
Contains various Ansys simulations showing variations in the performance of the IEA blade with changes to material properties. Most simulations will contain a file 'ansysresults_setXX.txt' which contains the key outputs from the simulation. These files can be parsed into Matlab to allow easy post-processing there due to easier operation than Ansys postproc, and allowing quick comparision. Each folder should contain the shell7.src and .mac files that are used to generate the model used in each analysis. The .src and .mac files are small and can easily be uploaded to github, but the results files may be better stored elsewhere (size ~80MB).
Several scripts are contained in the folder, as well as loads input files.
### IEA-3\_4\_NuMAD
This folder contains the NuMAD model for the IEA blade, including 2 variations of the model, and 9 variations of the material database. The material database that is desired to be used when running NuMAD should be renamed as MatDBsi.txt prior to opening the model.
### lib
This contains several libraries used for processing data (openFast, xfoil, NuMAD, ansys) and performing calculations.
### openfast
This is the IEA blade openfast model, as updated for Openfast 3.0, and with some modifications for use with a Python script to collect and process the data.
### xfoil
This is the working directory for xfoil. It contains various .foil files used for the IEA blade, as well as a template file used for operating xfoil from Python.
