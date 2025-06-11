# This is an example of python code using VTS to provide inverse solution
# for R(rho) to find chromophore concentrations of [Hb HbO2 H2O], with
# fixed single rho=1mm, 13 wavelengths [400:50:1000]nm and scatterer
# Power Law coefficients A=1.2, b=1.42.
# Scaled Monte Carlo with Nurbs forward solver provides the simulated
# measured data and PointSourceSDA provides the model used during the
# inversion.
# The optimization is performed by the Vts library MPFitLevenbergMarquardt
# method Solve.
#
# Import the Operating System so we can access the files for the VTS library
import clr
import os
file = '../libraries/Vts.dll'
clr.AddReference(os.path.abspath(file))
import numpy as np
import plotly.graph_objects as go
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
from System import Array, Object, Func
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
rOfRhoMeasured = measurementForwardSolver.ROfRho(opsMeasured, rho)
# Create a forward solver as a model function for inversion
forwardSolverForInversion = PointSourceSDAForwardSolver()

# Declare local forward reflectance function that computes reflectance from chromophores
# params=[wavelengths, rho, scatterer]
def CalculateReflectanceFuncVsWavelengthFromChromophoreConcentration(
        chromophoreConcentration, params):   
    # Create an array of chromophore absorbers based on values
    chromophoresLocal = Array.CreateInstance(IChromophoreAbsorber, 3)
    chromophoresLocal[0] = ChromophoreAbsorber(ChromophoreType.HbO2, chromophoreConcentration[0])
    chromophoresLocal[1] = ChromophoreAbsorber(ChromophoreType.Hb, chromophoreConcentration[1])
    chromophoresLocal[2] = ChromophoreAbsorber(ChromophoreType.H2O, chromophoreConcentration[2])
    # Compose local tissue to obtain optical properties
    opsLocal = Tissue(chromophoresLocal, params[2], "", n=1.4).GetOpticalProperties(params[0])
    print("iter:[HbO2,Hb,H2O]=[%3.2f %3.2f %3.2f]" % (
       chromophoreConcentration[0],chromophoreConcentration[1],chromophoreConcentration[2]))
    # Compute reflectance for local absorbers
    modelDataLocal = forwardSolverForInversion.ROfRho(opsLocal, params[1]) 
    return modelDataLocal

# Convert the Python function to a .NET Func delegate
forward_func = Func[Array[float], Array[Object], Array[float]](CalculateReflectanceFuncVsWavelengthFromChromophoreConcentration)

# Run the inversion: set up initial guess
initialGuess = [70.0, 30.0, 0.8]
chromophoresInitialGuess = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresInitialGuess[0] = ChromophoreAbsorber(ChromophoreType.HbO2, initialGuess[0])
chromophoresInitialGuess[1] = ChromophoreAbsorber(ChromophoreType.Hb, initialGuess[1])
chromophoresInitialGuess[2] = ChromophoreAbsorber(ChromophoreType.H2O, initialGuess[2])
# Compose tissue for initial guess data to obtain OPs
opsInitialGuess = Tissue(chromophoresInitialGuess, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
rOfRhoInitialGuess = forwardSolverForInversion.ROfRho(opsInitialGuess, rho)
# Run the levenberg-marquardt inversion
optimizer = MPFitLevenbergMarquardtOptimizer()
initialGuessCopy = Array.CreateInstance(float, 3)
initialGuessCopy = initialGuess
parametersToFit = Array.CreateInstance(bool, 3)
parametersToFit = [True, True, True]
measuredDataWeight = Array.CreateInstance(float, len(rOfRhoMeasured))
measuredDataWeight = [1] * len(measuredDataWeight)
params = Array.CreateInstance(Object, 3)
params = [wavelengths, rho, scatterer]

# try calling our LM
fit = optimizer.Solve(initialGuessCopy, parametersToFit, rOfRhoMeasured, measuredDataWeight, 
   forward_func, params)
# Calculate final reflectance from model at fit values
chromophoresFit = Array.CreateInstance(IChromophoreAbsorber, 3)
chromophoresFit[0] = ChromophoreAbsorber(ChromophoreType.HbO2, fit[0])
chromophoresFit[1] = ChromophoreAbsorber(ChromophoreType.Hb, fit[1])
chromophoresFit[2] = ChromophoreAbsorber(ChromophoreType.H2O, fit[2])
opsFit = Tissue(chromophoresFit, scatterer, "", n=1.4).GetOpticalProperties(wavelengths)
rOfRhoFit= forwardSolverForInversion.ROfRho(opsFit, rho)
# plot the results using Plotly
xLabel = "wavelengths [nm]"
yLabel = "R(wavelength) [mm-2]"
wvs = [w for w in wavelengths]
# plot measured data
meas = [m for m in rOfRhoMeasured]
chart = go.Figure()
chart.add_trace(go.Scatter(x=wvs, y=meas, mode='markers', name='measured data'))
# plot initial guess data
ig = [i for i in rOfRhoInitialGuess]
chart.add_trace(go.Scatter(x=wvs, y=ig, mode='markers', name='initial guess'))
# plot fit
conv = [f for f in rOfRhoFit]
chart.add_trace(go.Scatter(x=wvs, y=conv, mode='lines', name='converged'))
chart.update_layout( title="ROfRho (inverse solution for chromophore concentrations, multiple wavelengths, single rho)", xaxis_title=xLabel, yaxis_title=yLabel)
chart.show(renderer="browser")
# output results
print("Meas =    [%5.3f %5.3f %5.3f]" % (measuredData[0], measuredData[1], measuredData[2]))
print("IG   =    [%5.3f %5.3f %5.3f] Chi2=%5.3e" % (
                initialGuess[0], initialGuess[1], initialGuess[2],
                np.dot(np.subtract(rOfRhoMeasured,rOfRhoInitialGuess),
                       np.subtract(rOfRhoMeasured,rOfRhoInitialGuess))))
print("Conv =    [%5.3f %5.3f %5.3f] Chi2=%5.3e" % (fit[0], fit[1], fit[2],
                np.dot(np.subtract(rOfRhoMeasured,rOfRhoFit),
                       np.subtract(rOfRhoMeasured,rOfRhoFit))))
print("error =   [%5.3f %5.3f %5.3f]%%" % (
                100*abs((measuredData[0]-fit[0])/measuredData[0]),
                100*abs((measuredData[1]-fit[1])/measuredData[1]),
                100*abs((measuredData[2]-fit[2])/measuredData[2])))

