# This is an example of python code using VTS to provide inverse solution
# for R(rho) to find chromophore concentrations and power law coefficients
#
# Import the Operating System so we can access the files for the VTS library
from pythonnet import load
load('coreclr')
import clr
import os
file = '../libraries/Vts.dll'
print('Does this filepath exist?', os.path.isfile(file))
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
wavelengths = Array.CreateInstance(float, 600)
for i in range(0, len(wavelengths)-1):
    wavelengths[i] = 400.0 + i 
print('wavelengths[0]=',wavelengths[0])
# Define rho
rho = 1.0
# Setup the values for the measured data
chromophoresMeasuredData = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresMeasuredData[0] = ChromophoreAbsorber(ChromophoreType.HbO2, 70)
chromophoresMeasuredData[1] = ChromophoreAbsorber(ChromophoreType.Hb, 30)
chromophoresMeasuredData[2] = ChromophoreAbsorber(ChromophoreType.H2O, 0.8)
opsMeasured = Tissue(chromophoresMeasuredData, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
print('opsMeasured[0]=',opsMeasured[0])
# Create measurements using white Monte Carlo forward solver
measurementForwardSolver = NurbsForwardSolver()
measuredData = measurementForwardSolver.ROfRho(opsMeasured, rho)
print('measuredData[0]=',measuredData[0])
# Create a forward solver as a model function for inversion
forwardSolverForInversion = NurbsForwardSolver()

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
   print('modelDataForReturn[0]=',modelDataForReturn[0])
   return modelDataForReturn

# func for residual
def residual(chromophoreConcentration, wavelengths, rho, scatterer, measuredData, forwardSolver):
   prediction = CalculateReflectanceVsWavelengthFromChromophoreConcentration(
      chromophoreConcentration, wavelengths, rho, scatterer, forwardSolver) 
   difference = Array.CreateInstance(float,len(wavelengths))
   for i in range(0,len(wavelengths)):
       difference[i] = prediction[i] - measuredData[i]
   return difference

# Run the inversion: set up initial guess 
initialGuess = [75.0, 25.0, 0.9]
chromophoresInitialGuess = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresInitialGuess[0] = ChromophoreAbsorber(ChromophoreType.HbO2, initialGuess[0])
chromophoresInitialGuess[1] = ChromophoreAbsorber(ChromophoreType.Hb, initialGuess[1])
chromophoresInitialGuess[2] = ChromophoreAbsorber(ChromophoreType.H2O, initialGuess[2])
# Compose tissue for initial guess data to obtain OPs
opsInitialGuess = Tissue(chromophoresInitialGuess, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
# Run the levenberg-marquardt inversion
from scipy.optimize import least_squares
fit = least_squares(
   residual,
   initialGuess, 
   ftol=1e-9, xtol=1e-9, max_nfev=10000, # max_nfev needs to be integer
   args=(wavelengths, rho, scatterer, measuredData, forwardSolverForInversion), 
   method='lm')
print('fit.x=',fit.x)
# Calculate final reflectance from model at fit values
chromophoresFit = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresFit[0] = ChromophoreAbsorber(ChromophoreType.HbO2, fit.x[0])
chromophoresFit[1] = ChromophoreAbsorber(ChromophoreType.Hb, fit.x[1])
chromophoresFit[2] = ChromophoreAbsorber(ChromophoreType.H2O, fit.x[2])
opsFit = Tissue(chromophoresFit, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
fitReflectanceSpectrum = forwardSolverForInversion.ROfRho(opsFit, rho)
# plot the results using Plotly
xLabel = "wavelengths [nm]"
yLabel = "R(wavelength) [mm-2]"
wvs = [w for w in wavelengths]
print('wvs[0]=',wvs[0])
# plot measured data
meas = [m for m in measuredData]
chart = go.Figure()
chart.add_trace(go.Scatter(x=wvs, y=meas, mode='markers', name='measured data'))
# plot initial guess data
initialGuessR = forwardSolverForInversion.ROfRho(opsInitialGuess, rho) 
ig = [i for i in initialGuessR]
chart.add_trace(go.Scatter(x=wvs, y=ig, mode='markers', name='initial guess'))
# plot fit
fit = [f for f in fitReflectanceSpectrum]
chart.add_trace(go.Scatter(x=wvs, y=fit, mode='markers', name='fit'))
chart.update_layout( title="R(wavelength) [mm-2]", xaxis_title=xLabel, yaxis_title=yLabel)
chart.show(renderer="browser")







