# This is an example of python code using VTS to provide inverse solution
# for R(fx) to find chromophore concentrations and power law coefficients.
# The optimization uses the Vts library MPFitLevenbergMarquardt method Solve
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
# Setup wavelengths in visible and NIR spectral regimes
wavelengths = Array.CreateInstance(float, 8)
for i in range(0, len(wavelengths)):
    wavelengths[i] = 650.0 + 50 * i
# Setup fxs
fxs = [0.0, 0.2]
# Define parameters to fit [Hb,HbO2,A,b]
measuredData = [28.4, 22.4, 1.2, 1.42]
# Construct a scatter
scattererMeasuredData = PowerLawScatterer(measuredData[2], measuredData[3])
# Setup the values for the measured data
chromophoresMeasuredData = Array.CreateInstance(IChromophoreAbsorber, 2)
chromophoresMeasuredData[0] = ChromophoreAbsorber(ChromophoreType.HbO2, measuredData[0])
chromophoresMeasuredData[1] = ChromophoreAbsorber(ChromophoreType.Hb, measuredData[1])
# len(opsMeasured)=8 per number of wavelengths
opsMeasured = Tissue(chromophoresMeasuredData, scattererMeasuredData, "", n=1.4).GetOpticalProperties(wavelengths)
# Create measurements using Nurbs-based white Monte Carlo forward solver
measurementForwardSolver = NurbsForwardSolver()
# len(measuredROfFx)=(#fxs)x(#wavelengths) flattened
measuredROfFx=np.concatenate(
        [np.array(measurementForwardSolver.ROfFx(opsMeasured, fxs[0]), dtype=float), 
         np.array(measurementForwardSolver.ROfFx(opsMeasured, fxs[1]), dtype=float)])
# Create a forward solver as a model function for inversion
forwardSolverForInversion = PointSourceSDAForwardSolver()

# Declare local forward reflectance function that computes reflectance 
# from chromophores and scatterer values
# valuesSought = [Hb, HbO2, A, b]
def CalculateReflectanceVsWavelengthFromChromophoreConcAndScatterer(
    valuesSought, wavelengths, fxs, forwardSolver):
# Create a forward solve model function to solve inverse
   forwardSolverForInversion = PointSourceSDAForwardSolver()
   # Create an array of chromophore absorbers based on values
   chromophoresLocal = Array.CreateInstance(IChromophoreAbsorber, 2)
   chromophoresLocal[0] = ChromophoreAbsorber(ChromophoreType.HbO2, valuesSought[0])
   chromophoresLocal[1] = ChromophoreAbsorber(ChromophoreType.Hb, valuesSought[1])
   # Create a scatterr based on values
   scattererLocal = PowerLawScatterer(valuesSought[2], valuesSought[3])
   # Compose local tissue to obtain optical properties
   opsLocal = Tissue(chromophoresLocal, scattererLocal, "", n=1.4).GetOpticalProperties(wavelengths)
   # Compute reflectance for local absorbers
   modelDataLocal=np.concatenate(
        [np.array(forwardSolver.ROfFx(opsLocal, fxs[0]), dtype=float), 
         np.array(forwardSolver.ROfFx(opsLocal, fxs[1]), dtype=float)])
   modelDataForReturn=Array.CreateInstance(float, len(wavelengths)*len(fxs))
   for i in range(0, len(fxs)*len(wavelengths)-1):
        modelDataForReturn[i] = modelDataLocal[i]
   return modelDataForReturn

# func for residual
def residual(valuesSought, wavelengths, fxs, measuredROfFx, forwardSolver):
   predictedROfFx= CalculateReflectanceVsWavelengthFromChromophoreConcAndScatterer(
      valuesSought, wavelengths, fxs, forwardSolver) 
   difference = Array.CreateInstance(float,len(wavelengths)*len(fxs))
   for i in range(0, len(fxs)*len(wavelengths)-1):
       difference[i] = predictedROfFx[i] - measuredROfFx[i]
   return difference

# Run the inversion: set up initial guess 
initialGuess = [18.0, 30.0, 0.8, 1.60]
chromophoresInitialGuess = Array.CreateInstance(IChromophoreAbsorber, 2)
chromophoresInitialGuess[0] = ChromophoreAbsorber(ChromophoreType.HbO2, initialGuess[0])
chromophoresInitialGuess[1] = ChromophoreAbsorber(ChromophoreType.Hb, initialGuess[1])
scattererInitialGuess = PowerLawScatterer(initialGuess[2], initialGuess[3])
# Compose tissue for initial guess data to obtain OPs
opsInitialGuess = Tissue(chromophoresInitialGuess, scattererInitialGuess, "", n=1.4).GetOpticalProperties(wavelengths)
initialGuessROfFx=np.concatenate(
        [np.array(forwardSolverForInversion.ROfFx(opsInitialGuess, fxs[0]), dtype=float), 
         np.array(forwardSolverForInversion.ROfFx(opsInitialGuess, fxs[1]), dtype=float)])
# Run the levenberg-marquardt inversion
from scipy.optimize import least_squares
fit = least_squares(
   residual,
   initialGuess, 
   ftol=1e-9, xtol=1e-9, max_nfev=10000, # max_nfev needs to be integer
   args=(wavelengths, fxs, measuredROfFx, forwardSolverForInversion), 
   method='lm')
# Calculate final reflectance from model at fit values
chromophoresFit = Array.CreateInstance(IChromophoreAbsorber, 2)
chromophoresFit[0] = ChromophoreAbsorber(ChromophoreType.HbO2, fit.x[0])
chromophoresFit[1] = ChromophoreAbsorber(ChromophoreType.Hb, fit.x[1])
scattererFit = PowerLawScatterer(fit.x[2], fit.x[3])
# Compose tissue for fit data to obtain OPs
opsFit= Tissue(chromophoresFit, scattererFit, "", n=1.4).GetOpticalProperties(wavelengths)
fitROfFx=np.concatenate(
        [np.array(forwardSolverForInversion.ROfFx(opsFit, fxs[0]), dtype=float), 
         np.array(forwardSolverForInversion.ROfFx(opsFit, fxs[1]), dtype=float)])
# plot the results using Plotly results flattened so have to unflat
chart = go.Figure()
xLabel = "wavelength [nm]"
yLabel = "R(wavelength)"
wvs = [w for w in wavelengths]
# plot measured data first fx first
meas= [m for m in measuredROfFx]
midpoint=len(meas) // 2
chart.add_trace(go.Scatter(x=wvs, y=meas[:midpoint], mode='markers', name='measured data: fx1'))
chart.add_trace(go.Scatter(x=wvs, y=meas[midpoint:], mode='markers', name='measured data: fx2'))
# plot initial guess data
ig = [i for i in initialGuessROfFx]
chart.add_trace(go.Scatter(x=wvs, y=ig[:midpoint], mode='markers', name='initial guess: fx1'))
chart.add_trace(go.Scatter(x=wvs, y=ig[midpoint:], mode='markers', name='initial guess: fx2'))
# plot fit: need to organize by fx
conv = [f for f in fitROfFx]
chart.add_trace(go.Scatter(x=wvs, y=conv[:midpoint], mode='lines', name='converged: fx1'))
chart.add_trace(go.Scatter(x=wvs, y=conv[midpoint:], mode='lines', name='converged: fx2'))
chart.update_layout( title="ROfFx (inverse solution for chromophore concentrations, multiple wavelengths, multiple fx)", xaxis_title=xLabel, yaxis_title=yLabel)

chart.show(renderer="browser")
# output results
print("Meas =    [%5.3f %5.3f %5.3f %5.3f]" % (measuredData[0], measuredData[1], measuredData[2], measuredData[3]))
print("IG   =    [%5.3f %5.3f %5.3f %5.3f] Chi2=%5.3e" % (
                 initialGuess[0], initialGuess[1], initialGuess[2], initialGuess[3],
                 np.dot(measuredROfFx,initialGuessROfFx)))
print("Conv =    [%5.3f %5.3f %5.3f %5.3f] Chi2=%5.3e" % (fit.x[0], fit.x[1], fit.x[2], fit.x[3],
                 np.dot(measuredROfFx,fitROfFx)))
print("error =   [%5.3f %5.3f %5.3f %5.3f]" % (
                 abs((measuredData[0]-fit.x[0])/measuredData[0]),
                 abs((measuredData[1]-fit.x[1])/measuredData[1]),
                 abs((measuredData[2]-fit.x[2])/measuredData[2]),
                 abs((measuredData[3]-fit.x[3])/measuredData[3])))
