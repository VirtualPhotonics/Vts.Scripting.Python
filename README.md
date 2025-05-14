# Using VTS in a Jupyter notebook

This information will likely change as more support for `python` and `.NET` is introduced.  

## Installation details

### Step 1: Install .NET 8

You will need version 8 of .NET which is available from Microsoft below

https://dotnet.microsoft.com/en-us/download/dotnet/8.0


***On MacOS:***
Save everything to `$HOME/Documents/Code/dotnet8`

Do not forget to update your `~/.bash_profile` or whatever you use so that this directory is in your path.  Also define `DOTNET_ROOT` 

    PATH=$PATH:$HOME/Documents/Code/dotnet8
  
    export DOTNET_ROOT=$HOME/Documents/Code/dotnet8

### Step 2: Clone the scripting repository

    git clone https://github.com/VirtualPhotonics/vts.git

### Step 3: Download the VTS libraries

Get the latest VTS libraries for the specific platform from [releases](https://github.com/VirtualPhotonics/Vts.Scripting.Python/releases) and extract them into the **libraries** folder under **scripting**. 

### Step 4: Install pythonnet

    pip install pythonnet

***Note for MacOS and Linux:*** Because `pythonnet` under macOS (or linux) defaults to `mono`, two more things need to added to `~/.bash_profile`

    export PYTHONNET_RUNTIME=coreclr
    export PYTHONNET_PYDLL=/usr/local/bin/python3   
    
Obviously use the path for python on your system  (`which python3` will tell you)

Next start a `JupyterLab` notebook to verify that things are installed correctly

    import clr
    clr.AddReference("System")
    from System import Console
    Console.WriteLine("Hello from .NET 8!")

The final test is importing from `Vts.dll`
    
    from pythonnet import set_runtime
    set_runtime("coreclr")

    import clr
    clr.AddReference("/path/to/libraries/Vts.dll")    
    
    from Vts import *

where, of course, "/path/to" above has been adapted to your system

### Step 4: Run programs

To run `VTS` programs in `python` include the following the header

```
    from pythonnet import set_runtime
    set_runtime("coreclr")

    import clr
    clr.AddReference("/path/to/libraries/Vts.dll")    
    
    from Vts import *
    from Vts.Common import *
    from Vts.Extensions import *
    from Vts.Modeling.Optimizers import *
    from Vts.Modeling.ForwardSolvers import *
    from Vts.Factories import *
    from Vts.MonteCarlo import *
    from Vts.MonteCarlo.Sources import *
    from Vts.MonteCarlo.Tissues import *
    from Vts.MonteCarlo.Detectors import *
    from Vts.MonteCarlo.Factories import *
    from Vts.MonteCarlo.PhotonData import *
    from Vts.MonteCarlo.PostProcessing import *
    from System import Array, Double
```
