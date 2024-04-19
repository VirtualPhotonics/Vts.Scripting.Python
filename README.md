# Using VTS in a Jupyter notebook

This is likely to change once `python` scripting is formally supported by `VTS`.  

## macOS installation details

This is a record of how I got `vts` working in `JupyterLab`.

### Step 1: Install .NET 6

You will need version 6 of .NET which is available from Microsoft below

https://dotnet.microsoft.com/en-us/download/dotnet/6.0

I saved everything to `$HOME/Documents/Code/dotnet6`

Do not forget to update your `~/.bash_profile` or whatever you use so that this directory is in your path.  Also define `DOTNET_ROOT` 

    PATH=$PATH:$HOME/Documents/Code/dotnet6
  
    export DOTNET_ROOT=$HOME/Documents/Code/dotnet6

### Step 2: Install VTS

Follow the guidelines at https://github.com/VirtualPhotonics/VTS/wiki/Getting-Started-on-Mac  Briefly, clone the `.git` repo 

    git clone https://github.com/VirtualPhotonics/vts.git

This will create the directory `vts` that is needed for the next step

Install both `powershell` and `nuget` using [Homebrew](https://brew.sh)

    brew install powershell
    brew install nuget

Now build VTS.  If you don't have `matlab` don't worry, it seemed to work fine without completing the `matlab` tests

    pwsh
    cd vts
    ./BuildTestRelease.ps1 
    exit

### Step 3: Install pythonnet

    pip install pythonnet

Because `pythonnet` under macOS (or linux) defaults to `mono`, two more things need to added to `~/.bash_profile`

    export PYTHONNET_RUNTIME=coreclr
    export PYTHONNET_PYDLL=/usr/local/bin/python3   
    
Obviously use the path for python on your system  (`which python3` will tell you)

Next start a `JupyterLab` notebook to verify that things are installed correctly

    import clr
    
    clr.AddReference("System")
    from System import Console
    Console.WriteLine("Hello from .NET 6!")

The final test is importing from `Vts.dll`

    import clr
    clr.AddReference("/path/to/vts/src/Vts/publish/local/Vts.dll")    
    from Vts import *

where, of course, "/path/to" above has been adapted to your system

### Step 4: Run programs

To run `VTS` programs in `python` include the following the header

    import clr
    clr.AddReference("/path/to/vts/src/Vts/publish/local/Vts.dll")    
    
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