#!/bin/bash -e

###############################################################################
###############################################################################
#
# This script allows a user to download and compile the default PSC programs
# supported by pymcpsc.
#
# Several standard linux utilities are required and as a first step the script
# checks for there presence (check_sanity function). If a program is missing
# the script exits. Subsequently the PSC method software is downloaded and
# built in the order: FAST, GRALIGN, TAMLIGN, CE. Note the '-e' argument to
# bash which will cause this script to terminate at the first error.
#
# FAST and GRALIGN are distributed only in binary format and the latter is
# only available as a binary for 64-bit Linux machines. TMALIGN and CE are
# available in source format and this script downloads and builds them. 
#
# List of utilities required by this script:
#   - wget
#   - tar 
#   - uzip
#   - g++
#   - gfortran
#
# Usage:
#   ./psc_get.sh
#
#
###############################################################################
###############################################################################

###############################################################################
# PROGRAM PARAMETERS
###############################################################################

# Destination directory for program binaries
PRG_DIR='programs'

# Temporary directory for downloads
TMP_DIR='tmp'

# Binary only PSC methods
GRALIGN_LINK='http://www0.cs.ucl.ac.uk/staff/natasa/GR-Align/GR-Align_v1.5.zip'
FAST_LINK='https://biowulf.bu.edu/FAST/download/fast-linux-32.tar.gz'

# PSC methods buildable from source
CE_LINK='https://www.dropbox.com/s/mn9givpemb9v26i/psc-base-ce.zip?dl=0'
TMALIGN_LINK='https://zhanglab.ccmb.med.umich.edu/TM-align/TMalign.f'

###############################################################################
# DOWNLOAD AND INSTALL FUCTIONS
###############################################################################

exit_error() { echo $1; exit; }

check_sanity()
{
  # we need unzip
  command -v unzip >/dev/null 2>&1 || exit_error "Command unzip not found!"
  # we need tar
  command -v tar >/dev/null 2>&1 || exit_error "Command tar not found!"
  # we need wget
  command -v wget >/dev/null 2>&1 || exit_error "Command wget not found!"
  # we need gfortran
  command -v gfortran >/dev/null 2>&1 || exit_error "Command gfortran not found!"
  # we need g++
  command -v g++ >/dev/null 2>&1 || exit_error "Command g++ not found!"
}

get_fast()
{
  wget --no-check-certificate --directory-prefix="$TMP_DIR/" $FAST_LINK
  cd $TMP_DIR
  tar xzvf fast-linux-32.tar.gz
  cp fast-linux/fast ../$PRG_DIR/fast
  cd ..   
}

get_gralign()
{
  wget --directory-prefix="$TMP_DIR/" $GRALIGN_LINK
  cd $TMP_DIR
  unzip GR-Align_v1.5.zip
  cp CMap ../$PRG_DIR/
  cp DCount ../$PRG_DIR/
  cp GR-Align_1.5 ../$PRG_DIR/gralign
  cd ..
}

get_tmalign()
{
  wget --directory-prefix="$TMP_DIR/" $TMALIGN_LINK
  cd $TMP_DIR
  gfortran TMalign.f
  cp a.out ../$PRG_DIR/tmalign
  cd ..
}


get_ce()
{
  wget --directory-prefix="$TMP_DIR/" $CE_LINK
  cd $TMP_DIR
  unzip psc-base-ce.zip?dl=0
  rm psc-base-ce.zip?dl=0
  cd psc-base-ce
  cd pom; rm mkDB; cd ..
  make -C pom
  make -C ce
  cp ce/ce ../../$PRG_DIR/ce
  mkdir ../../$PRG_DIR/pom
  cp pom/mkDB ../../$PRG_DIR/pom/mkDB
  cd ..
  cd ..
}

###############################################################################
# MAIN
###############################################################################

# sanity check the system for required programs
check_sanity
echo "Sanity check satisfied!"

# create folders (program dir, temporary dir)
mkdir $PRG_DIR $TMP_DIR

# download and build the default PSC methods
get_fast
get_gralign
get_tmalign
get_ce

# remove temporary folder
rm -rf $TMP_DIR

echo "Done. Built programs are in $PRG_DIR"
###############################################################################
# END OF SCRIPT
###############################################################################

