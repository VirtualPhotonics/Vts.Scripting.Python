# This is an example of python code using VTS to plot R(rho) using MCCL
#
# Import the Operating System so we can access the files for the VTS library
from pythonnet import load
load('coreclr')
import clr
import os
file = '../libraries/Vts.dll'
print('Does this filepath exist?', os.path.isfile(file))
clr.AddReference(os.path.abspath(file))

print('Import numpy')
import numpy as np
print('Import pyplot')
import matplotlib.pyplot as plt
print('Import Vts')
from Vts import *
from Vts.Common import *
from Vts.Extensions import *
from Vts.Modeling.Optimizers import *
from Vts.Modeling.ForwardSolvers import *
from Vts.SpectralMapping import *
from Vts.Factories import *
from Vts.MonteCarlo import *
from Vts.MonteCarlo.Sources import *
from Vts.MonteCarlo.Tissues import *
from Vts.MonteCarlo.Detectors import *
from Vts.MonteCarlo.Factories import *
from Vts.MonteCarlo.PhotonData import *
from Vts.MonteCarlo.PostProcessing import *
print('Import System')
from System import Array, Double

# SimulationInput defines the simulation. I think the default is collimated point source illumination normal to the surface.
simulationInput = SimulationInput()
simulationInput.N = 10000

# We add four detectors. One to monitor the reflected excitance as a function of radius, and three to monitor the overall reflection and transmission.
# add detectors to Simulation object
detectors = Array.CreateInstance(IDetectorInput, 4)

detectors[0] = ROfRhoDetectorInput()
detectors[0].Rho = DoubleRange(start=0, stop=5, number=401)
detectors[1] = RDiffuseDetectorInput()
detectors[2] = RSpecularDetectorInput()
detectors[3] = TDiffuseDetectorInput()

simulationInput.DetectorInputs = detectors

# This is an index matched sample that has scattering of 0.99/mm and absorption of 0.01/mm. It is 10mm thick.
d = 10       # mm
mua = 0.01   # mm⁻¹
musp = 0.99  # mm⁻¹
g = 0        # scattering anisotropy
n = 1        # matched index of refraction

regions = Array.CreateInstance(ITissueRegion, 3)

regions[0] = LayerTissueRegion(zRange=DoubleRange(Double.NegativeInfinity, 0.0), op=OpticalProperties(mua=0.0, musp=1E-10, g=1.0, n=1.0))
regions[1] = LayerTissueRegion(zRange=DoubleRange(0.0, d), op=OpticalProperties(mua=mua, musp=musp, g=g, n=n))
regions[2] = LayerTissueRegion(zRange=DoubleRange(d, Double.PositiveInfinity), op=OpticalProperties(0.0, 1E-10, 1.0, 1.0))

simulationInput.TissueInput = MultiLayerTissueInput(regions)

# create the simulation
simulation = MonteCarloSimulation(simulationInput)

# run the simulation
simulationOutput = simulation.Run()

# extract the data
rDiffuse = Array.CreateInstance(RDiffuseDetector, 1)
rDiffuse[0] = simulationOutput.ResultsDictionary["RDiffuse"]

tDiffuse = Array.CreateInstance(TDiffuseDetector, 1)
tDiffuse[0] = simulationOutput.ResultsDictionary["TDiffuse"]

rSpecular = Array.CreateInstance(RSpecularDetector, 1)
rSpecular[0] = simulationOutput.ResultsDictionary["RSpecular"]

print("specular R = %.5f" % rSpecular[0].Mean)
print(" diffuse R = %.5f" % rDiffuse[0].Mean)
print(" diffuse T = %.5f" % tDiffuse[0].Mean)

# plot the results using Pyplot
detectorResults = Array.CreateInstance(ROfRhoDetector, 1)
detectorResults[0] = simulationOutput.ResultsDictionary["ROfRho"]

reflectance = np.array([r for r in detectorResults[0].Mean])
edges = np.array([mp for mp in detectorResults[0].Rho])[:-1]

plt.figure(figsize=(8,4.5))
plt.plot(edges, reflectance, 'ob', markersize=2)
plt.plot(-edges, reflectance, 'ob', markersize=2)
plt.xlabel('ρ [mm]')
plt.ylabel('R(ρ) [W/mm²]')
plt.title('1 W Impulse Beam')

text_args = {
    'ha': 'left',  # Horizontal alignment
    'va': 'top',   # Vertical alignment
    'transform': plt.gca().transAxes,  # Coordinate system transformation
    'fontsize': 9  # Font size
}

plt.text(0.8, 0.95, 'n=%.3f' % n, **text_args)
plt.text(0.8, 0.90, r'$\mu_a$=%.2f mm⁻¹' % mua, **text_args)
plt.text(0.8, 0.85, r"${\mu_s}'$=%.2f mm⁻¹" % musp, **text_args)
plt.text(0.8, 0.80, 'g=%.2f' % g, **text_args)
plt.text(0.8, 0.75, 'd=%.1f mm' % d, **text_args)
plt.show()