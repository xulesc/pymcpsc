###############################################################################
#
# This Dockerfile is to automate the build process of pyMCPSC or to at least
# simplify it on systems where the docker build and execution environments
# are available.
#
# 
#
###############################################################################
FROM python:2

# Set the working directory where pyMCPSC sources will be copied. This is done
# for in order to ensure that we know the path where the executable script
# to run pyMCPSC in the docker image resides 
WORKDIR /usr/src/app

# Update the repositories (debian) and install a key component necessary for
# running pyMCPSC inside a docker. This is a result of the dependence of
# ete3 on qt which in turn depends on availability of an X server!!! In order
# to avoid requiring all that cruft inside the docker image and retain the
# ete3 library the frame buffer workaround is used to load pyMCPSC inside the
# docker image.
RUN apt update
RUN apt install --fix-missing -y xvfb 

# Install the python run-time under which we want to execute. We use Miniconda
# since it is lightweight (27.2 MB) and makes it easy to install the python
# dependencies of pyMCPSC
RUN wget https://repo.continuum.io/miniconda/Miniconda2-4.0.5-Linux-x86_64.sh
RUN chmod +x Miniconda2-4.0.5-Linux-x86_64.sh
RUN ./Miniconda2-4.0.5-Linux-x86_64.sh -b -p /opt/anaconda2
RUN rm Miniconda2-4.0.5-Linux-x86_64.sh
ENV PATH "/opt/anaconda2/bin:$PATH"

# Install the python dependencies of pyMCPSC
RUN conda install pyqt=4.11 numpy matplotlib pandas scikit-learn scipy seaborn
 
# Drop apt cache just to make the image a little smaller than it would be
# without doing so
RUN rm -rf /var/lib/apt/lists/

# Copy pyMCPSC contents to the present working directory in the image
COPY . .

RUN python setup.py install

WORKDIR /usr/shared
