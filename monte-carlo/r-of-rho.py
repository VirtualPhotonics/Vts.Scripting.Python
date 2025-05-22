# This is an example of python code using VTS to plot R(rho) using MCCL
#
# Import the Operating System so we can access the files for the VTS library
import libraries
from pythonnet import load
load('coreclr')
import clr
import os
file = './libraries/Vts.dll'
print('Does this filepath exist?', os.path.isfile(file))
clr.AddReference(os.path.abspath(file))

print('Import numpy')
import numpy as np
print('Import plotly.graph')
import plotly.graph_objects as go
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
from System import Array
# Setup the values for the simulations and plot results
# create a SimulationInput object to define the simulation
detectorRange = DoubleRange(start=0, stop=40, number=201)
detectorInput = ROfRhoDetectorInput()
detectorInput.Rho = detectorRange
detectorInput.Name = "ROfRho"
detectors = Array.CreateInstance(IDetectorInput,1)
detectors[0] = detectorInput

simulationInput = SimulationInput()
simulationInput.N=1000
simulationInput.DetectorInputs= detectors

# create the simulation
simulation = MonteCarloSimulation(simulationInput)

# run the simulation
simulationOutput = simulation.Run()

# plot the results using Plotly
detectorResults = Array.CreateInstance(ROfRhoDetector,1)
detectorResults[0] = simulationOutput.ResultsDictionary["ROfRho"]
logReflectance = [r for r in detectorResults[0].Mean]
detectorMidpoints = [mp for mp in detectorRange]

xLabel = "ρ [mm]"
yLabel = "log(R(ρ)) [mm-2]"

chart = go.Figure()
chart.add_trace(go.Scatter(x=detectorMidpoints, y=logReflectance, mode='markers'))
chart.update_layout( title="log(R(ρ)) [mm-2]", xaxis_title=xLabel, yaxis_title=yLabel)
chart.update_yaxes(type="log")
chart.show(renderer="browser")