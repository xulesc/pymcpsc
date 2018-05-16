FROM python:2
#FROM debian:jessie
 
WORKDIR /usr/src/app

RUN apt update
RUN apt install --fix-missing -y xvfb 

## Go with Miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda2-4.0.5-Linux-x86_64.sh
RUN chmod +x Miniconda2-4.0.5-Linux-x86_64.sh
RUN ./Miniconda2-4.0.5-Linux-x86_64.sh -b -p /opt/anaconda2
RUN rm Miniconda2-4.0.5-Linux-x86_64.sh
ENV PATH "/opt/anaconda2/bin:$PATH"

RUN conda install pyqt=4.11 numpy matplotlib pandas scikit-learn scipy seaborn
 
RUN rm -rf /var/lib/apt/lists/

COPY . .

RUN python setup.py install

WORKDIR /usr/shared
