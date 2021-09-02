# Summary of Wind Turbine Lattice Project
## Product Trade Study, Full Blade Investigation
Going into this project, it was already a known issue that a lattice blade may not be as stiff as a traditional fiberglass blade. The objective of the full-blade investigation was to determine exactly how much the difference is between the baseline IEA blade stiffness and what is feasible to achieve with a lattice. The results of this have been discussed in the trade study report, but for the purposes of this summary, the key conclusions are listed below.
- The full lattice blade will not come close to the required stiffness at any point in the blade for any reasonable lattice relative density.
- When using the same spar caps as the original IEA blade, the desired bending stiffness can be achieved, but this does not take into account shear deflection of the blade.
- Ultimate loads did not drive the design criteria of the blade, so estimated peak stresses in the blade are low compared to the ultimate strength.
- To find opportunities for a lattice in a blade, it is important to look at detailed areas (edges, tip, core, etc.) to find the best fit.
- Further investigation requires FEA simulations to allow more direct comparison of different load cases and different blade structures.
## Ansys model creation
Initially, we received an Ansys model (specifically, NuMAD exported script for import to Ansys) from Mayank which was used to run FEA simulations. However, this model was somewhat difficult to use due to the pre-bent shape and due to some errors in identification of top and bottom surface that made it difficult to apply loads. Also, there was a lack of flexibility in changing material properties in bulk. Due to the complexity of the Ansys src file, it is very difficult to make any updates to it directly.

For this reason, a NuMAD model was first created in order to generate a better Ansys model. This proved to be a time-consuming task requiring a substantial amount of troubleshooting (with no documentation), but eventually a model was produced that closely matched the original model received from Mayank, except that the blade was not in the prebent form.

Once this model is generated, a list of nodes and elements can be exported from Ansys to a text file, to be used as an input for generating nodal loads.
## Loads model setup
In order to determine the performance of the lattice blade, as well as the baseline conventional blade, it was necessary to establish reasonable loads for various extreme load cases. There are two ways for the loads to be distributed through the airfoil:
1. Use the actual aero performance at each reference station of the blade to calculate the coefficient of pressure at each point on the blade, and use this to calculate loads at each point.
2. Use the Fx, Fy, Fz, and Mz values calculated in Openfast to apply loads to the spar caps.
Initially, the first method was used, but uncertainties of using Openfast, as well as Pietro's suggestion that such a level is not necessary, led to using the second method, with loads from the spreadsheet provided by Pietro. The loads provided contained internal force and moment values at ~13 points throughout the blade. The difference between each value was distributed on all nodes in the spar caps between the adjacent reference stations.
## Ansys model results
The key limitation of the Ansys models generated from NuMAD is that they are purely shell models. While there are some workarounds to this, it prevents the study of a blade with lattice components filling substantial portions of the blade. Instead, the focus of this portion of the study has been on comparing the performance of a lattice core blade to that of a balsa core. In any location where a balsa core existed in the original design, it would be replaced by a lattice with a minimum thickness of 2cm, while maintaining the same thickness of fiberglass.

To make modifications to the tested configuration, the NuMAD model was modified as required to allow a clean export of the .src model to Ansys. Since materials are uniquely named based on their location in the blade, simply changing the material database file for each variation allows an update to the core, which allows multiple models to be used simultaneously. Changes to the materials database was done through python code, since the native NuMAD function for this is very cumbersome and difficult to verify quality.

The original Ansys model contained some errors which negated the value of its results. The first is that the model did not appropriately separate the composite layers into a symmetrical laminate, while also assuming bending stiffness in the model, this resulted in reported stress values in the balsa, rather than in the laminate. Also, because the model included the surface protecting gelcoat layer, stress values were reported in the gelcoat as well. Both of these resulted in very low stress values being reported, due to the low moduli of each material. These issues were corrected in my model.

A sampling of the post-processing results are available in the [ansys/postproc](ansys/postproc) folder, which will show some of the differences in the results between various versions of the ansys model. To simplify the selection of images, there will be three sets: UY (flapwise deflection), SEQVtop (Mises on top surface), and SEQVbot (Mises on bottom surface). When using ansysResultsInput.m to plot, these plots can be rotated in 3d to show details all around. For simplicity of showing images, each of the images is shown in plan-form.
## Ansys analysis conclusions
It is difficult to draw extensive conclusions from the FEA simulations. It is not possible to use this model to demonstrate the capability of a lattice blade with new design features. For this, it would be necessary to take a more ground-up approach to the design and use a solid model in key areas to show the benefits of a solid lattice, for example at the tip, or leading and trailing edges.

The key conclusion that can be observed by a detailed inspection of different results, is regarding the core material. Once the model was properly cleaned up to produce better results, it became clear that despite the substantial reduction in stiffness of the lattice material compared to the balsa core used in the baseline model, there was negligible impact of the switch to the lattice core. This held true in the tip deflection, as well as the Mises stress in the reinforced areas. There is further study required in this area, but the indication of this is that it may be possible to replace balsa cores in the wind turbine blade with a lattice core. The viability of this will be highly dependent on the cost of building the lattice, but it is worth doing further study into the lattice core. The difficulty of sustainable balsa wood harvesting and the weight savings of the lattice core (density reduction from approximately 110kg/m3 to 7kg/m3) offer some appealing opportunities for improvements in the blade market.
## Comparison of models
One of the main factors differentiating the different Ansys models is the weight of various materials. For several key models, the weights of different materials are shown. These same labels will be used in further discussion below.
- IEA3_4MW: Model received from Mayank
- Balsa Core: Created with Colin's NuMAD model (as are all following models), modeled as closely as possible to the original IEA blade.
- Lattice 2x Core: .5 percent relative density lattice replaces Balsa Core, with a minimum thickness of 2cm and double the balsa core thickness.
- Lattice 3x Core: .5 percent relative density lattice replaces Balsa Core, with a minimum thickness of 2cm and triple the balsa core thickness.
- Lattice 3x Optimized: Similar to Lattice 3x Core, with a few modifications made to skin thickness in the LE, TE, and tip, and with better reinforcement of the tip area.

### Material BOM for Different Blade Iterations
All values in kg, except Vf. All composite laminae are E-Glass.

|Material	|IEA3_4MW	|Balsa Core	|Lattice 2x Core	|Lattice 3x Core	|Lattice 3x Optimized	| Vf |
|---	|---	|---	|---	|---	|---	|---|
|Biax webs	|342.7	|335.1	|335.1	|335.1	|335.1	|.5|
|Triax Shell	|6459.1	|7011.7	|7011.7	|7011.7	|7004.6	|.5|
|UD LE/TE	|433.2	|307.7	|307.7	|307.7	|307.7	|.55|
|UD Spar Caps	|6094.6	|6019.3	|6019.3	|6019.3	|6019.3	|.55|
|Balsa	|967.5	|997.6	|0	|0	|0	||
|Lattice	|0	|0	|127.9	|189.5	|191.2	||
|Gelcoat	|225.8	|225.4	|225.4	|225.4	|225.4	||
|Totals	|14522.9	|14896.9	|14027.2	|14088.8	|14083.3	||

### Flapwise deflection
Very little difference was observed in flapwise deflection between different models. For comparison, the original balsa core model deflection is shown compared to an optimized lattice design (with skin reinforcement at the tip). The deflection is slightly higher in the lattice blade, but the tip of the optimized blade does not exhibit the excessive deflection of the original models.

![Balsa Core](ansys/postproc/UY_Balsa%20Core%20with%20no%20gelcoat.png)

![Optimized Lattice Core](ansys/postproc/UY_Lattice3x%20optimized.png)

### Top Surface Stress
The stress plots do show some difference between the balsa core and the lattice core. It should be noted that there are some stress concentrations that occur due to the model which should not occur in a physical object. Mostly these are not visible in the plots, but they affect the coloration of the plots, which is why the plots are mostly blue. The easiest difference to see between the models is in the optimized model, where the high stresses at the tip have been eliminated due to the use of a lattice core in that area. Aside from this, the stress patterns are fairly similar between the various models, but the lattice core model has the lowest peak stress.

![Balsa Core](ansys/postproc/SEQVtop_Balsa%20Core%20with%20no%20gelcoat.png)

![Lattice 3x](ansys/postproc/SEQVtop_Lattice3x%20Core%20\(corrected\),%20no%20Gelcoat.png)

![Lattice 3x Optimized](ansys/postproc/SEQVtop_Lattice3x%20optimized.png)

### Bottom Surface Stress
On the bottom surface, the peak stress is somewhat higher in the lattice version than the balsa version, but as noted above, this is likely occurring at a stress concentration that would not occur outside of the model.

![Balsa Core](ansys/postproc/SEQVbot_Balsa%20Core%20with%20no%20gelcoat.png)

![Lattice 3x](ansys/postproc/SEQVbot_Lattice3x%20Core%20\(corrected\),%20no%20Gelcoat.png)


## General applicability of results
Part of this exercise is to develop the capability to quickly and easily work with any blade as a baseline. Ideally, when working with a different blade, a NuMAD model combined with either an OpenFast model or load cases would be sufficient to allow investigations into different material systems. The NuMAD model should be easy to update for a clean FEA model, or for different material systems. Since the Ansys model is produced in a consistent way, as long as the NuMAD materials are properly labeled and applied, then it should be straightforward to apply loads. The source of loads may have a different format which will require a new input method, but once they are input to Python, it should be simple to export to Ansys.
