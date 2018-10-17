pyMCPSC README file
=====================

The pyMCPSC Project is a utility for performing large-scale Multi-criteria
Protein Structure Comparison (MCPSC) on a multi-core CPU with an easy to extend
API for adding and removing PSC methods. It makes use of several relevant python
tools to perform typical associated tasks.

This README file is intended primarily for people interested in working
with the source code.

This pyMCPSC package is open source software made available under generous
terms. Please see the LICENSE file for further details.


Installation
============

From Docker Image
-----------------

First, make sure you have installed Docker on your machine following instructions provided at https://docs.docker.com/install/. Once Docker is installed check it by running 'docker --version' to ensure it is in your path. Note that Windows users with older versions (before 10) will need to follow the install path for Docker-toolbox. 

Locate the docker image of pyMCPSC that you have built or downloaded and load it (the daemon should be running) as follows::

    docker load -i [path_to_docker_image.tar]

Assuming that the name of the docker image is pymcpsc you should now be able to see the image in the docker list by issuing the following command::

    docker images

Test if pyMCPSC can be executed in the image by issuing the following command::

    docker run pymcpsc /usr/src/app/scripts/docker-launch-pymcpsc.sh -h

Executing this command should print the usage help message of pyMCPSC with command line arguments it accepts. 

Building a Docker Image
~~~~~~~~~~~~~~~~~~~~~~~

Assuming the requisite Docker tools are installed it is possible to build the docker image for pyMCPSC. Navigate to the location where you downloaded pyMCPSC (or cloned it) and issue the following command::

    docker build -t pymcpsc .

This process will take a little time, depending on your local machine and network connections, but once successfully completed the pyMCPSC image will appear in the docker images list.

Native installation
-------------------

This installation mode is releveant to developers who wish to extend pyMCPSC and **works only on Linux based systems**. Before pyMCPSC is installed the dependencies of pyMCPSC must be made available. The suggested route is to use the Anaconda/Miniconda platform which has a higher success rate across Linux systems, however, it is certainly possible to install the dependencies independently of the platform. We currently recommend using Python 2.7, Python 3.5 or Python 3.6 as we have only tested with these versions of Python. 


With Miniconda
~~~~~~~~~~~~~~

First, Download and install Miniconda 4.0.5 (https://www.continuum.io/archives).

Python 2 users on Linux may use::

    wget https://repo.continuum.io/miniconda/Miniconda2-4.0.5-Linux-x86_64.sh

Python 3 users on Linux may use::

    wget https://repo.continuum.io/miniconda/Miniconda3-4.0.5-Linux-x86_64.sh

Once Miniconda has been installed and is in the user path install the dependencies as follows::

    conda install pyqt=4.11 numpy matplotlib pandas scikit-learn scipy seaborn

Without Anaconda
~~~~~~~~~~~~~~~~

This requires installation of all the dependencies individually. You will need admin / sudo rights on your system depending on how you choose to install the dependencies. On a Ubuntu / Debian based system the users should run the following commands to install the required packages::

    sudo apt install python−pyqt4 python−lxml python−numpy \
                     python−scipy python−matplotlib python−seaborn


Finally, navigate to the location where you have downloaded pyMCPSC source and execute the following commands::

    python setup.py build
    python setup.py install

Test if pyMCPSC has installed correctly by issuing the following command::

    run-pymcpsc -h

The output should be the help message showing the arguments accepted by the utility.

Configuring an experiment
=========================

pyMCPSC supports multiple usage modes. For those that are only interested in
running the utility a Docker image may be the best place to start. For those interested in 'natively' deploying the utility it is also possible to do so, however, this route will work only on Linux based systems.

Preparing the dataset
---------------------

In order to run pyMCPSC the user must have protein (domain) structure files available locally on the machine where pyMCPSC will be run. A useful script to download structure files from the PDB has been included scripts/download.sh. The script creates a directory pdb files in the CWD and downloads the structure files into this directory. pyMCPSC includes structure files for the Chew Kedem dataset in tests/chew kedem dataset/pdb files.

Preparing the ground truth file
-------------------------------

The next step is to prepare the ground truth file which provides the list of protein domain pairs to be included in the PSC and their SCOP/CATH classification. The ground truth file is a tab separated value file with 4 columns: protein 1, protein 2, classification of protein 1 and classification of protein 2. A sample ground truth file included in pyMCPSC is tests/chew kedem dataset/ground truth ck. A useful script to prepare the ground truth file
from a listing of domains and their classifications is included scripts/prepare ground truth.py. The script writes out the ground truth file in the CWD.

Setting up the experiment
-------------------------

pyMCPSC supports several parameters to control the experiment these are as follows

- **DATADIR**: The value should be the full path to the directory with the PDB structure files.
- **GTIN**: The value should be the full path to the ground-truth data file
- **PDBEXTN**: The value should be the extension of the PDB structure files
- **THREADS**: The value should be the number of threads pyMCPSC is allowed to launch.
- **WEIGHTS**: The value should be a comma separated string with weights for the PSC methods (in order - ce,fast,gralign,TM-align,usm).
- **PROGDIR**: The value should be the full path to the directory with the PSC binaries.


Typically the user will not supply this value unless the PSC binaries have been compiled to some custom location. The program parameters can be specified on the CLI. pyMCPSC provides a set of sensible default fallback values for the optional arguments. If no value is specified for the Datadir, the pre-packaged proteus dataset is automatically selected. If no value is specified for Progdir, the default set of five PSC methods is used. If no value is specified for the Gtin and the proteus dataset is used, the default ground truth data is automatically selected. Note that if the proteus dataset is not used then then the user must provide a ground truth file for the performance benchmarking to be performed. If no values are specified by the user pyMCPSC runs the experiment described in the original paper.

Running an experiment
=====================

A key aspect of pyMCPSC that is relevant to the exerimental setup is that pyMCPSC generates several output Figures and data files (that the user may wish to analyze with other tools). The outputs are written to subfolders in the CWD it is therefore important to ensure this is a writeable location especially when running in Docker mode. 

From Docker
-----------

The simplest way to run an experiment with pyMCPSC (recreating the results of the original paper on Proteus_300 dataset) is to issue the following command::

    docker run -v [absolute_path]:/usr/shared pymcpsc:latest \
                  /usr/src/app/scripts/docker-launch-pymcpsc.sh

Note that we are mounting a path on the local filesystem to a specfic location in the docker which is where pyMCPSC expects to write its output. This path must be absolute and not relative.

In order to use your own dataset of domains and ground truth (see previous sections on how to generate this data) the user must place these in the same directory that will be mounted to /usr/shared. For instance, create a subdirectory data in the 'absolute_path' and place the PDB files (with pdb extension) in the directory and place the corresponding ground truth data in a file 'ground_truth'. Then issue the following command to run pyMCPSC with the custom data::

    docker run -v [absolute_path]:/usr/shared pymcpsc:latest \
                  /usr/src/app/scripts/docker-launch-pymcpsc.sh \
                  -e pdb -d /usr/shared/data \
                  -g /usr/shared/ground_truth

Note that both, directory data and file ground_truth, reside at [absolute_path] on the local filesystem but are passed to pyMCPSC as arguments in the location where they are expected to be found in the Docker.

We have included a small dataset (Chew-Kedem) dataset in pyMCPSC sources (tests/chew_kedem_dataset).

From native installation
------------------------

To run a MCPSC experiment with pyMCPSC create a directory, TEST_DIR, where the experiment outputs will be written. We refer to the location where pyMCPSC was cloned (unpacked from zip) as CLONE_DIR. Running pyMCPSC is as easy as invoking
the run-pymcpsc command with the appropriate parameters::
    
    cd $TEST_DIR$
    run−pymcpsc [−h ] [−e PDBEXTN] [−d DATADIR] [−g GTIN ] [−t THREADS]
                [−w WEIGHTS] [−p PROGDIR]

Results generated by pyMCPSC are placed in the work and outdir directories located in the current working directory (CWD), i.e. the one from where the program is launched. Moreover, figures generated by pyMCPSC are placed in the figures directory in the CWD. To run pyMCPSC with the Proteus_300 dataset (prepacked) and generate the results reported in the original paper use the command::

    cd $TEST_DIR$
    run-pymcpsc

Sample dataset for experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We include in pyMCPSC the Chew-Kedem dataset and associated ground truth file as a test dataset. To configure pyMCPSC to run with this dataset point pyMCPSC to run with with the tests/chew kedem dataset/pdb files folder (as DATADIR) and tests/chew kedem dataset/ground truth ck (as GTIN). The parameter PDBEXTN should be set as PDB. A minimal commnand for using this dataset is listed below (INSTALL_DIR is the location where pyMCPSC was extracted)::

    cd $TEST DIR$
    run−pymcpsc −e pdb \
                −d $INSTALL_DIR$/pymcpsc/tests/chew_kedem_dataset/pdb_files \
                −g $INSTALL_DIR$/pymcpsc/tests/chew_kedem_dataset/groundtruth_ck

Python Requirements
===================

We currently recommend using Python 2.7, Python 3.5 or Python 3.6 as we have only 
tested with these versions of Python. Please **make sure that Python is installed 
correctly** and in the system path if you intend to locally develop and deploy
pyMCPSC.

Dependencies
============

- NumPy, see http://www.numpy.org 
  This package is only used in the computationally-oriented modules.

- Matplotlib, see http://matplotlib.org
  All plots generated by the module use this library.

- Pandas, see http://pandas.pydata.org
  This package is required for loading and manipulating the results
  data used in the process of generating the consensus scores as well
  as data for ploting.

- Scikit, see http://scikit-learn.org/stable/
  This package is required for matrix operations performed during consensus
  scores calculation. It is also used to carry out the Multi-dimensional
  Scaling operations.

- Seaborn, see https://seaborn.pydata.org
  This package is required for the heatmaps.

- Dendropy, see https://www.dendropy.org
  This package is required for generating the dendrograms.

- Ete3, see http://etetoolkit.org
  This package is required for generating the phylogenetic trees.

Using pyMCPSC as a library
==========================

It is entirely possible for advanced programmers to use pyMCPSC as a
library. This can be achieved by importing its modules after installation,
directly in the application script which needs it. Note that at the time of
this writing the API of the modules is not very clean and will be improved
over time to support this functionality more elegantly.

Distribution Structure
======================

- README.rst -- This file.
- LICENSE    -- What you can do with the code.
- setup.py   -- Installation file.
- pymcpsc/   -- The main code base sources.
- tests/     -- Unit test cases (Proteus).
- docs/      -- Additional documentation including results of Proteus experiments
- scripts/   -- Useful scripts for allied tasks

Known Issues
============

- Sometimes the GR-align preprocessing binary does not build any contact maps (look for Running pairwise PSC jobs - signature file count: 0 - on the pyMCPSC console output. Rerunning typically resolves this problem.

- Sometimes when running from docker image, the final message is a Segmentation fault. This does not mean any error in processing of pyMCPSC, in fact it is a result of an error in the xvfb-run program termination, which in no way affects the results generated by pyMCPSC.

Acknowledgements
================

This work was supported by a research grant, European Union (European Social Fund ESF) and Greek national funds, through the Operational Program "Education and Lifelong Learning" of the National Strategic Reference Framework (NSRF) - Research Funding Program "Heracleitus II" (grant number: 70/3/10929) under the supervision of Prof. Elias S. Manolakos (PI), Information Technologies in Medicine and Biology Dept. of Informatics and Telecommunications, University of Athens.

References
==========
- If you use pyMCPSC please cite: Sharma A, Manolakos ES (2018) Multi-criteria protein structure comparison and structural similarities analysis using pyMCPSC. PLoS ONE 13(10): e0204587. https://doi.org/10.1371/journal.pone.0204587
