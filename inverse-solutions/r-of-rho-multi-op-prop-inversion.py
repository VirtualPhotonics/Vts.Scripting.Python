# This is an example of python code using VTS to provide inverse solution
# for R(rho) to find chromophore concentrations and power law coefficients.
# The optimization is performed by a python library scipy.
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
from System import Array, Object
# Construct a scatterer
scatterer = PowerLawScatterer(1.2, 1.42)
# Setup wavelengths in visible and NIR spectral regimes
wavelengths = Array.CreateInstance(float, 13)
for i in range(0, len(wavelengths)):
    wavelengths[i] = 400.0 + 50 * i 
# Define rho
rho = 1.0
# Setup the values for the measured data
measuredData = [70.0, 30.0, 0.8]
chromophoresMeasuredData = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresMeasuredData[0] = ChromophoreAbsorber(ChromophoreType.HbO2, measuredData[0])
chromophoresMeasuredData[1] = ChromophoreAbsorber(ChromophoreType.Hb, measuredData[1])
chromophoresMeasuredData[2] = ChromophoreAbsorber(ChromophoreType.H2O, measuredData[2])
opsMeasured = Tissue(chromophoresMeasuredData, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
# Create measurements using Nurbs-based white Monte Carlo forward solver
measurementForwardSolver = NurbsForwardSolver()
measuredROfRho= measurementForwardSolver.ROfRho(opsMeasured, rho)
# Create a forward solver as a model function for inversion
forwardSolverForInversion = PointSourceSDAForwardSolver()

# Declare local forward reflectance function that computes reflectance from chromophores
def CalculateReflectanceVsWavelengthFromChromophoreConcentration(
    chromophoreConcentration, wavelengths, rho, scatterer, forwardSolver):
# Create a forward solve model function to solve inverse
   forwardSolverForInversion = PointSourceSDAForwardSolver()
   # Create an array of chromophore absorbers based on values
   chromophoresLocal = Array.CreateInstance(IChromophoreAbsorber, 3)
   chromophoresLocal[0] = ChromophoreAbsorber(ChromophoreType.HbO2, chromophoreConcentration[0])
   chromophoresLocal[1] = ChromophoreAbsorber(ChromophoreType.Hb, chromophoreConcentration[1])
   chromophoresLocal[2] = ChromophoreAbsorber(ChromophoreType.H2O, chromophoreConcentration[2])
   # Compose local tissue to obtain optical properties
   opsLocal = Tissue(chromophoresLocal, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
   print('opsLocal[0]=',opsLocal[0])
   # Compute reflectance for local absorbers
   modelDataLocal = Array.CreateInstance(float, len(wavelengths))
   modelDataLocal = forwardSolver.ROfRho(opsLocal, rho) 
   modelDataForReturn= Array.CreateInstance(float, len(wavelengths))
   for i in range(0, len(wavelengths)):
        modelDataForReturn[i] = modelDataLocal[i]
   return modelDataForReturn

# func for residual
def residual(chromophoreConcentration, wavelengths, rho, scatterer, measuredROfRho, forwardSolver):
   predictedROfRho= CalculateReflectanceVsWavelengthFromChromophoreConcentration(
      chromophoreConcentration, wavelengths, rho, scatterer, forwardSolver) 
   difference = Array.CreateInstance(float,len(wavelengths))
   for i in range(0,len(wavelengths)):
       difference[i] = predictedROfRho[i] - measuredROfRho[i]
   return difference

# Run the inversion: set up initial guess 
initialGuess = [70.0, 30.0, 0.8]
chromophoresInitialGuess = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresInitialGuess[0] = ChromophoreAbsorber(ChromophoreType.HbO2, initialGuess[0])
chromophoresInitialGuess[1] = ChromophoreAbsorber(ChromophoreType.Hb, initialGuess[1])
chromophoresInitialGuess[2] = ChromophoreAbsorber(ChromophoreType.H2O, initialGuess[2])
# Compose tissue for initial guess data to obtain OPs
opsInitialGuess = Tissue(chromophoresInitialGuess, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
initialGuessROfRho = forwardSolverForInversion.ROfRho(opsInitialGuess, rho) 
# Run the levenberg-marquardt inversion
from scipy.optimize import least_squares
fit = least_squares(
   residual,
   initialGuess, 
   ftol=1e-9, xtol=1e-9, max_nfev=10000, # max_nfev needs to be integer
   args=(wavelengths, rho, scatterer, measuredROfRho, forwardSolverForInversion), 
   method='lm')
# Calculate final reflectance from model at fit values
chromophoresFit = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresFit[0] = ChromophoreAbsorber(ChromophoreType.HbO2, fit.x[0])
chromophoresFit[1] = ChromophoreAbsorber(ChromophoreType.Hb, fit.x[1])
chromophoresFit[2] = ChromophoreAbsorber(ChromophoreType.H2O, fit.x[2])
opsFit = Tissue(chromophoresFit, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
fitROfRho= forwardSolverForInversion.ROfRho(opsFit, rho)
# plot the results using Plotly
xLabel = "wavelength [nm]"
yLabel = "R(wavelength)"
wvs = [w for w in wavelengths]
# plot measured data
meas = [m for m in measuredROfRho]
chart = go.Figure()
chart.add_trace(go.Scatter(x=wvs, y=meas, mode='markers', name='measured data'))
# plot initial guess data
ig = [i for i in initialGuessROfRho]
chart.add_trace(go.Scatter(x=wvs, y=ig, mode='markers', name='initial guess'))
# plot fit
conv = [f for f in fitROfRho]
chart.add_trace(go.Scatter(x=wvs, y=conv, mode='lines', name='converged'))
chart.update_layout( title="ROfRho (inverse solution for chromophore concentrations, multiple wavelengths, single rho)", xaxis_title=xLabel, yaxis_title=yLabel)
chart.show(renderer="browser")
# output results
print("Meas =    [%5.3f %5.3f %5.3f]" % (measuredData[0], measuredData[1], measuredData[2]))
print("IG   =    [%5.3f %5.3f %5.3f] Chi2=%5.3e" % (initialGuess[0], initialGuess[1], initialGuess[2],
                np.dot(measuredROfRho,initialGuessROfRho)))
print("Conv =    [%5.3f %5.3f %5.3f] Chi2=%5.3e" % (fit.x[0], fit.x[1], fit.x[2],
                np.dot(measuredROfRho,fitROfRho)))
print("error =   [%5.3f %5.3f %5.3f]" % (abs((measuredData[0]-fit.x[0])/measuredData[0]),
                abs((measuredData[1]-fit.x[1])/measuredData[1]),
                abs((measuredData[2]-fit.x[2])/measuredData[2])))
