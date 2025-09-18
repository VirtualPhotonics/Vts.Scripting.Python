# Dependence of Fluence Predictions on the Number of Photons Simulated
#
# Goal: This exercise explores how fluence estimates change with the 
# number of photons simulated. 
# 
# Import the Operating System so we can access the files for the VTS library
from pythonnet import load
load('coreclr')
import clr
import os
file = '../libraries/Vts.dll'
clr.AddReference(os.path.abspath(file))
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# use matplotlib.pyplot
import matplotlib as mpl
import matplotlib.pyplot as plt
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
from System import Array, Object, Double, Math
# Setup the detector input for the simulation
rhoStart = 0
rhoStop = 10  # [mm]
rhoCount = 101
zStart = 0
zStop = 10  # [mm]
zCount = 101
detectorRhoRange = DoubleRange(start=rhoStart, stop=rhoStop, number=rhoCount)
detectorZRange = DoubleRange(start=zStart, stop=zStop, number=zCount)
detectorInput = FluenceOfRhoAndZDetectorInput()
detectorInput.Rho = detectorRhoRange
detectorInput.Z = detectorZRange
detectorInput.Name = "FluenceOfRhoAndZ"
detectorInput.TallySecondMoment = True
detectors = Array.CreateInstance(IDetectorInput,1)
detectors[0] = detectorInput

# Setup the tissue input for the simulation
regions = Array.CreateInstance(ITissueRegion, 3)
regions[0] = LayerTissueRegion(zRange=DoubleRange(Double.NegativeInfinity, 0.0), op=OpticalProperties(mua=0.0, musp=1E-10, g=1.0, n=1.0)) # air
regions[1] = LayerTissueRegion(zRange=DoubleRange(0.0, 100.0), op=OpticalProperties(mua=0.01, musp=1.0, g=0.8, n=1.4)) # tissue
regions[2] = LayerTissueRegion(zRange=DoubleRange(100.0, Double.PositiveInfinity), op=OpticalProperties(mua=0.0, musp=1E-10, g=1.0, n=1.0)) # air

# Setup source
sourceInput = DirectionalPointSourceInput()
sourceInput.InitialTissueRegionIndex=0

# Setup number of photons simulated
nPhot = [10, 100, 1000, 10000]
FluenceArray = np.zeros((len(nPhot), (zCount - 1) * (rhoCount - 1)))
RelativeErrorArray = np.zeros((len(nPhot), (zCount - 1) * (rhoCount-1)))

# plot 4 cases in grid
fig, axes = plt.subplots(nrows=2,ncols=2)
fig.suptitle("Fluence vs n")
xLabel = "ρ [mm]"
yLabel = "z [mm]"
title = "log(Φ(ρ,z)) [mm-2]"
# ignore divide by zero warning when calculating relative error
np.seterr(divide='ignore', invalid='ignore')

for i in range(0, len(nPhot)):
  simulationOptions = SimulationOptions()
  simulationOptions.AbsorptionWeightingType = AbsorptionWeightingType.Analog  # variation: set to Discrete
  # create a SimulationInput object to define the simulation
  simulationInput = SimulationInput()
  simulationInput.N = nPhot[i]
  simulationInput.OutputName = "MonteCarloFluence"
  simulationInput.DetectorInputs = detectors
  simulationInput.Options = simulationOptions
  simulationInput.Tissue = MultiLayerTissueInput(regions)
  # create the simulations
  simulation = MonteCarloSimulation(simulationInput)
  # run the simulations
  simulationOutput = simulation.Run()
  # determine standard deviation and plot the results using Plotly
  detectorResults = Array.CreateInstance(FluenceOfRhoAndZDetector, 1)
  detectorResults[0] = simulationOutput.ResultsDictionary["FluenceOfRhoAndZ"]
  Fluence = Array.CreateInstance(FluenceOfRhoAndZDetector, 1)
  RelativeError = Array.CreateInstance(FluenceOfRhoAndZDetector, 1)
  FluenceArray[i] = [f for f in detectorResults[0].Mean]
  SecondMoment = [s for s in detectorResults[0].SecondMoment]
  StandardDeviation = np.sqrt((SecondMoment - np.multiply(FluenceArray[i], FluenceArray[i]) / simulationInput.N))
  RelativeErrorArray[i] = np.divide(StandardDeviation, FluenceArray[i])

  # plot fluence as a function of N, number of photons simulated
  # plot log of fluence and mirror fluence(rho,z) about rho=0 axis
  logFluence = [Math.Log(f) for f in FluenceArray[i]]
  # Convert to .NET array
  rhoDelta = detectorRhoRange.GetDelta()
  rhos = rhoStart + rhoDelta * np.arange(rhoCount - 1)
  # reverse and concatenate
  allRhos = np.concatenate((-rhos[::-1], rhos))
  zDelta = detectorZRange.GetDelta()
  zs = zStart + zDelta * np.arange(zCount - 1)
  fluenceRowsToPlot = np.array([logFluence[i:i+len(zs)] for i in range(0, len(logFluence), len(zs))])

  colormap=mpl.colormaps['magma']
  cbar_ticks = [-6, -4, -2, 0]

  if (i==0):
    im0=allFluenceRowsToPlot = np.concatenate((fluenceRowsToPlot[::-1], fluenceRowsToPlot))
    im0=axes[0,0].imshow(allFluenceRowsToPlot.T, vmin=-6, vmax=0)
    axes[0,0].set_title('log(Flu(ρ,z))[mm^-2]');
    axes[0,0].set_xlabel('ρ [mm]')
    axes[0,0].set_ylabel('z [mm]')
    axes[0,0].text(10, 90, 'N=10')
    cbar = fig.colorbar(im0, cmap=colormap, location='right', shrink=0.6, pad=0.05)
    cbar.set_ticks(cbar_ticks)
  if (i==1):
    im1=allFluenceRowsToPlot = np.concatenate((fluenceRowsToPlot[::-1], fluenceRowsToPlot))
    im1=axes[0,1].imshow(allFluenceRowsToPlot.T, vmin=-6, vmax=0)
    axes[0,1].set_title('log(Flu(ρ,z))[mm^-2]');
    axes[0,1].set_xlabel('ρ [mm]')
    axes[0,1].set_ylabel('z [mm]')
    axes[0,1].text(10, 90, 'N=100')
    cbar = fig.colorbar(im1, cmap=colormap, location='right', shrink=0.6, pad=0.05)
    cbar.set_ticks(cbar_ticks)
  if (i==2):
    im2=allFluenceRowsToPlot = np.concatenate((fluenceRowsToPlot[::-1], fluenceRowsToPlot))
    im2=axes[1,0].imshow(allFluenceRowsToPlot.T, vmin=-6, vmax=0)
    axes[1,0].set_title('log(Flu(ρ,z))[mm^-2]');
    axes[1,0].set_xlabel('ρ [mm]')
    axes[1,0].set_ylabel('z [mm]')
    axes[1,0].text(10, 90, 'N=1000')
    cbar = fig.colorbar(im2, cmap=colormap, location='right', shrink=0.6, pad=0.05)
    cbar.set_ticks(cbar_ticks)
  if (i==3):
    im3=allFluenceRowsToPlot = np.concatenate((fluenceRowsToPlot[::-1], fluenceRowsToPlot))
    im3=axes[1,1].imshow(allFluenceRowsToPlot.T, vmin=-6, vmax=0)
    axes[1,1].set_title('log(Flu(ρ,z))[mm^-2]');
    axes[1,1].set_xlabel('ρ [mm]')
    axes[1,1].set_ylabel('z [mm]')
    axes[1,1].text(10, 90, 'N=10000')
    cbar = fig.colorbar(im3, cmap=colormap, location='right', shrink=0.6, pad=0.05)
    cbar.set_ticks(cbar_ticks)

# plot relative error as a function of N, the number of photons simulated
# plot 4 cases in grid
fig, axes = plt.subplots(nrows=2,ncols=2)
fig.suptitle("Relative error vs n")
xLabel = "ρ [mm]"
yLabel = "z [mm]"
title = "relerror(Φ(ρ,z))"

for i in range(0, len(nPhot)):
  # plot fluence relative error and mirror about rho=0 axis
  relativeError = [r for r in RelativeErrorArray[i]]
  relativeErrorRowsToPlot = np.array([relativeError[i:i+len(zs)] for i in range(0, len(relativeError), len(zs))])

  colormap=mpl.colormaps['magma']
  cbar_ticks = [0.0, 0.5, 1.0]

  if (i==0):
    im0=allRelativeErrorRowsToPlot = np.concatenate((relativeErrorRowsToPlot[::-1], relativeErrorRowsToPlot))
    im0=axes[0,0].imshow(allRelativeErrorRowsToPlot.T, vmin=0, vmax=1)
    axes[0,0].set_title('relerr(Flu(ρ,z))');
    axes[0,0].set_xlabel('ρ [mm]')
    axes[0,0].set_ylabel('z [mm]')
    axes[0,0].text(10, 90, 'N=10')
    cbar = fig.colorbar(im0, cmap=colormap, location='right', shrink=0.6, pad=0.05)
    cbar.set_ticks(cbar_ticks)
  if (i==1):
    im1=allRelativeErrorRowsToPlot = np.concatenate((relativeErrorRowsToPlot[::-1], relativeErrorRowsToPlot))
    im1=axes[0,1].imshow(allRelativeErrorRowsToPlot.T, vmin=0, vmax=1)
    axes[0,1].set_title('relerr(Flu(ρ,z))');
    axes[0,1].set_xlabel('ρ [mm]')
    axes[0,1].set_ylabel('z [mm]')
    axes[0,1].text(10, 90, 'N=100')
    cbar = fig.colorbar(im1, cmap=colormap, location='right', shrink=0.6, pad=0.05)
  if (i==2):
    im2=allRelativeErrorRowsToPlot = np.concatenate((relativeErrorRowsToPlot[::-1], relativeErrorRowsToPlot))
    im2=axes[1,0].imshow(allRelativeErrorRowsToPlot.T, vmin=0, vmax=1)
    axes[1,0].set_title('relerr(Flu(ρ,z))');
    axes[1,0].set_xlabel('ρ [mm]')
    axes[1,0].set_ylabel('z [mm]')
    axes[1,0].text(10, 90, 'N=1000')
    cbar = fig.colorbar(im2, cmap=colormap, location='right', shrink=0.6, pad=0.05)
  if (i==3):
    im3=allRelativeErrorRowsToPlot = np.concatenate((relativeErrorRowsToPlot[::-1], relativeErrorRowsToPlot))
    im3=axes[1,1].imshow(allRelativeErrorRowsToPlot.T, vmin=0, vmax=1)
    axes[1,1].set_title('relerr(Flu(ρ,z))');
    axes[1,1].set_xlabel('ρ [mm]')
    axes[1,1].set_ylabel('z [mm]')
    axes[1,1].text(10, 90, 'N=10000')
    cbar = fig.colorbar(im3, cmap=colormap, location='right', shrink=0.6, pad=0.05)

plt.show()

