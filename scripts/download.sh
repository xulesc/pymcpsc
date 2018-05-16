#!/bin/sh

#
# This script downloads PDB structure files. It expects a file
# named 'domains_list' to be present in the CWD and contain the
# PDB structure names.
#
# The script will create a directory 'pdb_files' in the CWD and
# place the downloaded structure files in the directory.
# 
# For example of a domains_list file see: 
#   test/chew_kedem_dataset/domains_list
#

# create pdb files directory
mkdir pdb_files

# download pdb files
while read dom; do
	wget -P pdb_files https://files.rcsb.org/download/$dom.pdb
done <domains_list
