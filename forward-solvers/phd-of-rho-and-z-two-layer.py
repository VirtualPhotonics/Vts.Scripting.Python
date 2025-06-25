# This is an example of python code using VTS to Compute photon hitting density for a two-layer 
# medium at a given set of optical properties 
#
# Import PythonNet
from pythonnet import load
load('coreclr')
import clr
# Import the Operating System so we can access the files for the VTS library
import os
file = '../libraries/Vts.dll'
clr.AddReference(os.path.abspath(file))
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
from System import Array, Double, Object, Func, Math
clr.AddReference("System.Core")
from System.Linq import Enumerable

solver = TwoLayerSDAForwardSolver()
solver.SourceConfiguration = SourceConfiguration.Distributed
topLayerThickness = 5
opRegions = Array.CreateInstance(IOpticalPropertyRegion, 2)
opRegions[0] = LayerOpticalPropertyRegion(DoubleRange(0, topLayerThickness, 2), OpticalProperties(0.1, 1, 0.8, 1.4))
opRegions[1] = LayerOpticalPropertyRegion(DoubleRange(topLayerThickness, Double.PositiveInfinity, 2), OpticalProperties(0.01, 1, 0.8, 1.4))
# Create the DoubleRange instance
rhos_range = DoubleRange(0.1, 19.9, 100) # range of s-d separations in mm

# Convert to .NET array
rho_delta = rhos_range.GetDelta()
print(rho_delta)
# Start at 0.1, increment by 0.2, 100 elements
rhos = 0.1 + rho_delta * np.arange(100)
print(rhos)

zs_range = DoubleRange(0.1, 19.9, 100) # range of depths in mm

# Convert to .NET array
zs_delta = zs_range.GetDelta()
print(zs_delta)
# Start at 0.1, increment by delta, 100 elements
zs = 0.1 + zs_delta * np.arange(100)
print(zs)

allRhos = np.concatenate((-rhos[::-1], rhos))
opRegionsArray = Array[Array[IOpticalPropertyRegion]]([opRegions])
# predict the tissue's fluence(rho, z) for the given optical properties 
fluenceOfRhoAndZ = solver.FluenceOfRhoAndZ(opRegionsArray, allRhos, zs );

#PHD
sourceDetectorSeparation = 10
opArray = Array.CreateInstance(OpticalProperties, 2)
opArray[0] = OpticalProperties(0.1, 1, 0.8, 1.4)
opArray[1] = OpticalProperties(0.01, 1, 0.8, 1.4)

phdOfRhoAndZ = ComputationFactory.GetPHD(solver, fluenceOfRhoAndZ, sourceDetectorSeparation, opArray, Array[Double](allRhos.tolist()), Array[Double](zs.tolist()))

# log transform
log_fluence = [Math.Log(f) for f in phdOfRhoAndZ]

size = len(zs)
# split into rows
fluenceRowsToPlot = np.array([log_fluence[i:i+size] for i in range(0, len(log_fluence), size)])

# Heatmap function to convert the data into a heat map
def heatmap(values, x, y, x_label="", y_label="", title=""):
    """Create a heatmap chart."""
    # values should be a 2D array-like (list of lists or 2D numpy array)
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=x,
        y=y,
        transpose=True,
        colorscale='Hot',
        colorbar=dict(title=title)
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        yaxis_autorange='reversed'
    )
    return fig

fluenceChart = heatmap(fluenceRowsToPlot.tolist(), allRhos.tolist(), list(zs), "ρ [mm]", "z [mm]", "log(phd(ρ, z) [mm-2])")
fluenceChart.add_hline(y=topLayerThickness, line_dash="dash", line_color="white", line_width=2)
fluenceChart.show(renderer="browser")
