# Welcome to the top-level repo of Accel-Sim

The [ISCA 2020 paper](https://conferences.computer.org/isca/pdfs/ISCA2020-4QlDegUf3fKiwUXfV0KdCm/466100a473/466100a473.pdf)
describes the goals of Accel-Sim and introduces the tool. This readme is meant to provide tutorial-like details on how to use the Accel-Sim
framework. If you use any component of Accel-Sim, please cite:

```
Mahmoud Khairy, Zhensheng Shen, Tor M. Aamodt, Timothy G. Rogers,
Accel-Sim: An Extensible Simulation Framework for Validated GPU Modeling,
in 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA)
```

## Dependencies

This package is meant to be run on a modern linux distro.
A docker image that works with this repo can be found [here](https://hub.docker.com/repository/docker/accelsim/ubuntu-18.04_cuda-11).
There is nothing special here, just Ubuntu 18.04 with the following commands
run:

```bash
sudo apt-get install  -y wget build-essential xutils-dev bison zlib1g-dev flex \
      libglu1-mesa-dev git g++ libssl-dev libxml2-dev libboost-all-dev git g++ \
      libxml2-dev vim python-setuptools python-dev build-essential python-pip
pip install pyyaml==5.1 plotly psutil
wget http://developer.download.nvidia.com/compute/cuda/11.0.1/local_installers/cuda_11.0.1_450.36.06_linux.run
sh cuda_11.0.1_450.36.06_linux.run --silent --toolkit
rm cuda_11.0.1_450.36.06_linux.run
```

Note, that all the python scripts have more detailed options explanations when run with "--help"


## Accel-Sim Repo Overview

The code for the Accel-Sim framework is in this repo. Accel-Sim 1.0 uses the
GPGPU-Sim 4.0 performance model, which was released as part of the original
Accel-Sim paper. Building the trace-based Accel-Sim will pull the right version of
GPGPU-Sim 4.0 to use in Accel-Sim.

There is an additional repo where we have collected a set of common GPU applications and a common infrastructure for building
them with different versions of CUDA. If you use/extend this app framework, it makes Accel-Sim easily usable
with a few simple command lines. The instructions in this README will take you through how to use Accel-Sim with
the apps in from this collection as well as just on your own, with your own apps.

[GPU App Collection](https://github.com/accel-sim/gpu-app-collection)

## Accel-Sim Components

![Accel-Sim Overview](https://accel-sim.github.io/assets/img/accel-sim-crop.svg)

1. **Accel-Sim Tracer**: An NVBit tool for generating SASS traces from CUDA applications. Code for the tool lives in ./util/tracer\_nvbit/. To make the tool:  
  
    ```bash  
    export CUDA_INSTALL_PATH=<your_cuda>  
    export PATH=$CUDA_INSTALL_PATH/bin:$PATH  
    ./util/tracer_nvbit/install_nvbit.sh  
    make -C ./util/tracer_nvbit/  
    ```  
    ---
    *A simple example*  
      
    The following example demonstrates how to trace the simple rodinia functional tests  
    that get run in our travis regressions:  
      
    ```bash  
    # Make sure CUDA_INSTALL_PATH is set, and PATH includes nvcc  
      
    # Get the applications, their data files and build them:  
    git clone https://github.com/accel-sim/gpu-app-collection  
    source ./gpu-app-collection/src/setup_environment  
    make -j -C ./gpu-app-collection/src rodinia_2.0-ft  
    make -C ./gpu-app-collection/src data  
      
    # Run the applications with the tracer (remember you need a real GPU for this):  
    ./util/tracer_nvbit/run_hw_trace.py -B rodinia_2.0-ft -D <gpu-device-num-to-run-on>  
    ```  
      
    That's it. The traces for the short-running rodinia tests will be generated in:  
    ```bash  
    ./hw_run/traces/  
    ```  
      
    To extend the tracer, use other apps and understand what, exactly is going on, read [this](https://github.com/accel-sim/accel-sim-framework/blob/dev/util/tracer_nvbit/README.md).  
      
    ---
    For convience, we have included a repository of pre-traced applications - to get all those traces, simply run:  
    ```bash  
    ./get-accel-sim-traces.py  
    ```  
    and follow the instructions.  

2. **Accel-Sim SASS Frontend**: A simulator frontend that consumes SASS traces and feeds them into a performance model. The intial release of Accel-Sim coincides with the release of GPGPU-Sim 4.0, which acts as the detailed performance model. To build the Accel-Sim simulator that uses the traces, do the following:
    ```bash
    source ./gpu-simulator/setup_environment.sh
    make -j -C ./gpu-simulator/
    ```
    This will prodice an executable in:
    ```bash
    ./gpu-simulator/bin/release/accel-sim.out
    ```

    *Running the simple example from bullet 1*
    ```bash
    ./util/job_launching/run_simulations.py -B rodinia_2.0-ft -C QV100 -T ./hw_run/traces/device-<device-num>/<cuda-version>/ -N myTest
    ```
    You can monitor the tests using:
    ```
    ./util/job_launching/monitor_func_test.py -v -N myTest
    ```
    After the jobs finish - you can collect all the stats using:
    ```
    ./util/job_launching/get_stats.py -N myTest | tee stats.csv
    ```

    To understand what is going on and how to just run the simulator in isolation without the framework, read [this](https://github.com/accel-sim/accel-sim-framework/tree/dev/util/job_launching/README.md).  

3. *Accel-Sim Correlator*: A tool that matches, plots and correlates statistics from the performance model with real hardware statistics generated by profiling tools.
4. *Accel-Sim Tuner*: An automated tuner that automates configuration file generation from a detailed microbenchmark suite.



### How do I quickly just run what Travis runs?

Install docker, then simply run:

```
docker run --env CUDA_INSTALL_PATH=/usr/local/cuda-11.0 -v `pwd`:/accel-sim:rw accelsim/ubuntu-18.04_cuda-11:latest /bin/bash travis.sh
```

If something is dying and you want to debug it - you can always run it in interactive mode:

```
docker run -it --env CUDA_INSTALL_PATH=/usr/local/cuda-11.0 -v `pwd`:/accel-sim:rw accelsim/ubuntu-18.04_cuda-11:latest /bin/bash
```

Then from within the docker run:
```
./travis.sh
```

You can also play around and do stuff inside the image (even debug the
simulator) - if you want to do this, installing gdb will help:
```
apt-get install gdb
```

Don't want to install docker?
Just use a linux ditro with the packages detailed in dependencies, set
CUDA\_INSTALL\_PATH, the run ./travis.sh.

### Running test generally

The scripts here provide a set of defaults that make it relatively painless to run the default regression test.
Remember, the following things should be setup:

1. CUDA toolkit installed
2. nvcc is in the path
3. Torque is installed (even if you are not on a cluster, installing this locally is required).
4. You have sourced the `setup_environment` file inside the GPGPU-Sim dev branch (and built the simulator).

If all this is true, then running the following commands will verify that the configs that ship in GPGPU-Sim are finishing and functionally correct:

```
git checkout travis-regress
cd ./benchmarks/src
make all -j
# All the apps will be output to: ./benchmarks/bin/4.2/release
# Now that everything is built, lets run the tests:
cd ../../util/job_launching

# This actually runs the tests
./run_simulations.py -N travis-test
# This will probe all the tests you just ran and will inform you once they pass or fail
./monitor_func_test.py -N travis-test
```

If you see `Congratulations! All tests pass!` then everything is good to go.
If you see anything else, look at the error log indicated and debug what is wrong. The scripts will print out the error logs for every run that failed as well at the last 10 lines of the stdout.
If you need more than that, you can do to the benchmark's directory and run gdb manually.

### The Benchmarks

The initial iteration of this repository contains a set of functional tests based on Rodinia 2.0 created by Andrew Boktor from UBC.
Over time, we will add workloads to this tree for other updated benchmarks suites.
It is also a long-term goal that papers published using GPGPU-Sim can submit their workloads here as a centralized place where people looking to reproduce work can gather them.
The SDK is conspicuously absent due to the lengthy license agreement associated with the SDK code. It might be alright to post it here, but we don't have time to make sure.

#### ./benchmarks/data_dirs

The repo itself has no data (since git is bad with big files). git-lfs is one option that could be explored, but since the public, free version of github limits the
capacity and bandwidth using git-lfs, the data is simply retrieved via wget form a tarball hosted on Purdue's servers.

#### ./benchmarks/src/

This is where all the code for the apps go.
A top-level makefile  is here for allowing all of these to be built easily. In the initial commit, only rodinia-2.0-ft apps are included, but more will be added later.
It should also be noted that the common.mk file from the CUDA 4.2 SDK is included here, since the rodinia benchmarks rely on it.

### The simulation scripts

Everybody doing any serious research with GPGPU-Sim wants to do a few things:

1. Run a bunch of benchmarks on a bunch of different configs
2. Make sure that all their test actually finished correctly and if they didn't, debug them quickly.
3. Once you are sure everything worked, you want to collect a grid of statistics for plotting in papers, which typically look like:
```
IPC:
    , Config1, Config2, ...
App1,     X  ,   Y    , ...
App2,     A  ,   B    , ...
...
```

This repo provides a standardized, flexible way of doing all this very quickly.

#### ./util/job_launching

There are 3 core scripts in here:

1. `run_simulations.py # Launches jobs`
2. `job_status.py # Checks if jobs pass and get errors when they don't`
3. `get_stat.py # Collects the data you need to publish :)`

`run_simulations.py`:

This file handles everything that needs to be done to launch jobs.
It is configured by two yaml scripts, one for benchmarks and one for configs.
The default files here are in `./util/job_launching/regression_recipies/rodinia_2.0-ft/`.
The comments in these files should be self-explanatory. The overall intent here is that you point run_simulations.py at different benchmark.yml and configs.yml files for whatever you want to run.
run_simualtions.py does all the following:

1. Copies the .so file already compiled in gpgpu-sim root into the "running directory" (explained below) inside `<running_directory>/gpgpu-sim-builds/<gpgpu-sim-git-commit-#>`. This is a nice feature because if you rebuilt the simulator while tests are running, you will not be changing the .so that the tests are actually using (when torque runs, it adds this new directory to the LD_LIBRARY_PATH).
2. It creates the right directory structure for running multiple benchmarks, with multiple arguments over multiple configs.
3. It copies all the files GPGPU-Sim needs to run into the newly created directories (interconnect files, gpuwattch files, any pre-generated PTX files, etc...)
4. It copies and (symbolically linking all the data) that each benchmark needs into the directories the apps are running from.
5. It applies any benchmark-specific options to the config files (you might want to do this if some apps require old sm versions for example).
6. After everything is setup it launches the jobs via torque. The core command here is `qsub` - if you need to modify these scripts for use with another job manager, look for `qsub` in this file.
7. It creates a log of all the jobs you launch this time so you can collect stats and status for just these jobs if you so choose.

`job_status.py`


`get_stats.py`


### The Running directory:

These scripts create a directory structure for all the jobs that they launch.

The format is:
./running_directory/app_name/dirsafe_app_args/config/
Inside each of these directories is where GPGPU-Sim is run by the launched torque jobs.
The default running directory is `sim_run_<toolkit_version>` for example `sim_run_4.2`.
If you ever need to debug specific runs interactively, you can `cd` to the right directory then run:

`gdb --args `tail -1 torque.sim``

This works because the last line of the torque.sim file contains the commandline for running the program with these arguments.
When jobs complete in torque, they output a .o<jobId> and .e<jobId> file. This is what all the stat collection scripts parse when collecting statistics.
It is intended that there will be multiple such output files in each of these directories, as you change GPGPU-Sim to fix bugs and model additional features.
Everything in the running directory is recreated when you launch new jobs, so as long as you are fine loosing all your job outputs, this directory is safe to delete.
