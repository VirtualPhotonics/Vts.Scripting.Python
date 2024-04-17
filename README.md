# Jupyter notebooks to call the VTS using Python

This is likely to change once `python` scripting is formally supported by `VTS`.  

## Getting things working on a Mac

I did not have a .NET installation and do most things from the command line.  This is a record of how I got `vts` working in `JupyterLab`.

### Step 1: Install .NET 6

You will need version 6 of .NET which is available from Microsoft below

https://dotnet.microsoft.com/en-us/download/dotnet/6.0

I saved everything to `$HOME/Documents/Code/dotnet6`

Do not forget to update your `.bash_profile` or whatever you use so that this directory is in your path.  Also define `DOTNET_ROOT` 

    PATH=$PATH:$HOME/Documents/Code/dotnet6
  
    export DOTNET_ROOT=$HOME/Documents/Code/dotnet6

### Step 2: Install VTS

Follow the guidelines at https://github.com/VirtualPhotonics/VTS/wiki/Getting-Started-on-Mac  Briefly, clone the `.git` repo 

    git clone https://github.com/VirtualPhotonics/vts.git

This will create the director `vts` that we will use in the next step

When you are using `brew` you might as well install `nuget` at the same time

    brew install powershell
    brew install nuget

Now build VTS.  If you don't have `matlab` don't worry, it seemed to work fine without completing the `matlab` tests

    pwsh
    cd vts
    ./BuildTestRelease.ps1 
    exit
    
### Step 3: Install .NET dlls

Navigate to the release version of vts.dll

    cd vts/src/Vts/bin/Release/net6.0

Now use `nuget` to install the extra required libraries

    nuget install MathNet.Numerics.dll
    nuget install Newtonsoft.Json.dll
    nuget install Nlog.dll
    nuget install System.Reactive.dll

rummage through all the folders and move the net6.0 `*.dll` to  `vts/src/Vts/bin/Release/net6.0` .  Doing `ls` in this directory should show

    MathNet.Numerics.dll
    Newtonsoft.Json.dll
    Nlog.dll
    System.Reactive.dll
    Vts.dll

### Step 4: Install pythonnet

    pip install pythonnet

Now because `pythonnet` assumes that you're using `mono` and not `.NET`, we need to update a few more things in .bash_profile

    export PYTHONNET_RUNTIME=coreclr
    export PYTHONNET_PYDLL=/usr/local/bin/python3   
    
Change the path for python to that for your system  (try `which python3` if you don't know)

Start a `JupyterLab` notebook and verify that things are installed correctly

    import clr
    
    clr.AddReference("System")
    from System import Console
    Console.WriteLine("Hello from .NET 6!")

Once this works the next step will be to add the `Vts.dll`

    import sys
    
    dll_directory = "/path/to/vts/src/Vts/bin/Release/net6.0"
    sys.path.append(dll_directory)
    clr.AddReference("Vts")

Once this is working, verify that the other dlls you downloaded load properly

    clr.AddReference("Newtonsoft.Json")
    clr.AddReference("Mathnet.Numerics")
    clr.AddReference("NLog")
    clr.AddReference("System.Reactive");

And now you should be able to run `VTS` programs in `python` with the header

    import sys
    dll_directory = "/path/to/vts/src/Vts/bin/Release/net6.0"
    sys.path.append(dll_directory)
    
    import clr
    clr.AddReference("Vts")
    clr.AddReference("Newtonsoft.Json")
    clr.AddReference("Mathnet.Numerics")
    clr.AddReference("NLog")
    clr.AddReference("System.Reactive")
    
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


