# Spatially-Resolved Reflectance Predictions for Analog versus CAW Simulations 
#
# Goal: This exercise compares error estimates of spatially-resolved 
# reflectance using Analog versus Continuous Absorption Weighting (CAW) i
# simulations. 
#
# Import the Operating System so we can access the files for the VTS library
from pythonnet import load
load('coreclr')
import clr
import os
import time
file = '../libraries/Vts.dll'
clr.AddReference(os.path.abspath(file))
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
from System import Array, Object, Double
# Setup the values for the Analog and CAW simulations and plot the results
# Setup the detector input for the simulation
detectorRange = DoubleRange(start=0, stop=10, number=101)
detectorInput = ROfRhoDetectorInput()
detectorInput.Rho = detectorRange
detectorInput.TallySecondMoment = True
detectorInput.Name = "ROfRho"
detectors = Array.CreateInstance(IDetectorInput,1)
detectors[0] = detectorInput

# Setup the tissue input for the simulation
regions = Array.CreateInstance(ITissueRegion, 3)
regions[0] = LayerTissueRegion(zRange=DoubleRange(Double.NegativeInfinity, 0.0), op=OpticalProperties(mua=0.0, musp=1E-10, g=1.0, n=1.0)) # air
regions[1] = LayerTissueRegion(zRange=DoubleRange(0.0, 100.0), op=OpticalProperties(mua=0.01, musp=1.0, g=0.8, n=1.4)) # tissue
regions[2] = LayerTissueRegion(zRange=DoubleRange(100.0, Double.PositiveInfinity), op=OpticalProperties(mua=0.0, musp=1E-10, g=1.0, n=1.0)) # air

simulationOptions1 = SimulationOptions()
simulationOptions1.AbsorptionWeightingType = AbsorptionWeightingType.Analog
# create a SimulationInput object to define the simulation
simulationInput1 = SimulationInput()
simulationInput1.N=10000
simulationInput1.OutputName = "MonteCarloROfRho-Analog"
simulationInput1.DetectorInputs= detectors
simulationInput1.Options = simulationOptions1
simulationInput1.Tissue = MultiLayerTissueInput(regions)

simulationOptions2 = SimulationOptions()
simulationOptions2.AbsorptionWeightingType = AbsorptionWeightingType.Continuous
# create a SimulationInput object to define the simulation
simulationInput2 = SimulationInput()
simulationInput2.N=10000
simulationInput2.OutputName = "MonteCarloROfRho-CAW"
simulationInput2.DetectorInputs = detectors
simulationInput2.Options = simulationOptions2
simulationInput2.Tissue = MultiLayerTissueInput(regions)

# create the simulations
simulation1 = MonteCarloSimulation(simulationInput1)
simulation2 = MonteCarloSimulation(simulationInput2)

# run the simulations
start_time = time.time()
simulationOutput1 = simulation1.Run()
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time Analog: {elapsed_time:.6f} seconds")
start_time = time.time()
simulationOutput2 = simulation2.Run()
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time CAW: {elapsed_time:.6f} seconds")

# determine standard deviation and plot the results using Plotly
detectorResults1 = Array.CreateInstance(ROfRhoDetector,1)
detectorResults1[0] = simulationOutput1.ResultsDictionary["ROfRho"]
Reflectance1 = [r for r in detectorResults1[0].Mean]
SecondMoment1 = [s for s in detectorResults1[0].SecondMoment]
StandardDeviation1 = np.sqrt((SecondMoment1 - np.multiply(Reflectance1, Reflectance1)) / simulationInput1.N)
RelativeError1 = np.divide(StandardDeviation1, Reflectance1)
detectorMidpoints1 = [mp for mp in detectorRange]

detectorResults2 = Array.CreateInstance(ROfRhoDetector,1)
detectorResults2[0] = simulationOutput2.ResultsDictionary["ROfRho"]
Reflectance2 = [r for r in detectorResults2[0].Mean]
SecondMoment2 = [s for s in detectorResults2[0].SecondMoment]
StandardDeviation2 = np.sqrt((SecondMoment2 - np.multiply(Reflectance2, Reflectance2)) / simulationInput2.N)
RelativeError2 = np.divide(StandardDeviation2, Reflectance2)
detectorMidpoints2 = [mp for mp in detectorRange]

# plot reflectance with 1-sigma error bars and relative error difference
chart = make_subplots(rows=2, cols=1)
xLabel = "ρ [mm]"
yLabel = "log(R(ρ)) [mm-2]"
# reflectance with 1-sigma error bars: omit last data point because includes reflectance beyond last rho bin
chart.add_trace(go.Scatter(x=detectorMidpoints1[:-2], y=Reflectance1[:-1], error_y=dict(type='data',array=StandardDeviation1[:-1],visible=True), mode='markers', name='Analog'), row=1, col=1)
chart.add_trace(go.Scatter(x=detectorMidpoints2[:-2], y=Reflectance2[:-1], error_y=dict(type='data',array=StandardDeviation2[:-1],visible=True), mode='markers', name='CAW'), row=1, col=1)
chart.update_traces(error_y_thickness=1)
chart.update_layout(xaxis_title=xLabel, yaxis_title=yLabel, xaxis_range=[0,10])
chart.update_yaxes(type="log", row=1, col=1)
# relative error difference
relativeErrorDifference = RelativeError1 - RelativeError2
chart.add_trace(go.Scatter(x=detectorMidpoints1[:-2], y=relativeErrorDifference[:-1], mode='lines', showlegend=False), row=2, col=1)
chart.add_hline(y=0.0, line_dash="dash", line_color="black", row=2, col=1)
chart['layout']['yaxis2']['title']='Analog RE - CAW RE'
chart['layout']['xaxis2']['title']=xLabel
chart['layout']['xaxis2']['range']=[0,10]

chart.show(renderer="browser")
