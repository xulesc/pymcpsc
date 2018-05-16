#!/usr/bin/env python

# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
"""
Script to be executed for running pyMCPSC. The software must first have been
installed on the system. On load the script looks for run_gui-args.json file
to find and load user specified parameters from a previous run. On execution
start a copy of the user parameters are written to the run_gui-args.json file.
"""
import os
import sys
import pymcpsc
import argparse

from pymcpsc.run import RunPairwisePSC
from pymcpsc.postprocessing import PostProcessor
from pymcpsc.impute import make as impute
from pymcpsc.mcpsc import make as mcpsc
from pymcpsc.nnclassify import make as nnclassify
from pymcpsc.rocauc import make as rocauc
from pymcpsc.mixedroc import make as mixedroc
from pymcpsc.visualize2 import make as mdsclust
from pymcpsc.heatmaps import make as heatmap
from pymcpsc.phylo import make as phylotree

# default values for program arguments
_base_dir = os.path.dirname(pymcpsc.__file__)
__def_PDBEXTN__ = "ent"
__def_THREADS__ = 6
__def_WEIGHTS__ = "2.55,1.79,4.23,14.36,-0.38"
__def_DATADIR__ = os.path.join(_base_dir, 'testdata', 'proteus')
__def_PROGDIR__ = os.path.join(_base_dir, 'ext', 'x86_64', 'linux')
__def_GTIN__ = os.path.join(_base_dir, 'testdata', 'ground_truth_proteus')


class CONF:

    def __init__(self):
        self.WORKDIR = 'work'
        self.OUTDIR = 'outdir'

    def set_data_dir(self, datadir):
        self.DATADIR = datadir

    def set_gtin(self, gtin):
        self.GTIN = gtin

    def set_pdb_extn(self, pdbextn):
        self.PDBEXTN = pdbextn

    def set_threads(self, threads):
        self.THREADS = threads

    def set_weights(self, weights):
        self.WEIGHTS = weights

    def set_prog_dir(self, progdir):
        self.PROGDIR = progdir

    def __repr__(self):
        return str(self.__dict__)


def process():
    """ The main method of the utility.
    """

    # program arguments
    print('initializing parser')
    parser = argparse.ArgumentParser(description='Run pyMCPSC.')
    help_text = 'Extension of the PDB files (default: %s)' % __def_PDBEXTN__
    parser.add_argument(
        '-e',
        '--pdbextn',
     default=__def_PDBEXTN__,
     help=help_text)
    help_text = 'Directory containing the PDB files (default: proteus dataset)'
    parser.add_argument(
        '-d',
        '--datadir',
     default=__def_DATADIR__,
     help=help_text)
    help_text = 'Ground truth file (default: proteus dataset)'
    parser.add_argument('-g', '--gtin', default='', help=help_text)
    help_text = 'Number of threads to use (default: %d)' % __def_THREADS__
    parser.add_argument(
        '-t',
        '--threads',
     default=__def_THREADS__,
     type=int,
     help=help_text)
    help_text = 'Weights assigned to PSC methods (default: %s)' % __def_WEIGHTS__
    parser.add_argument(
        '-w',
        '--weights',
     default=__def_WEIGHTS__,
     help=help_text)
    help_text = 'Directory containing the PSC binaries (default: pre packed)'
    parser.add_argument(
        '-p',
        '--progdir',
     default=__def_PROGDIR__,
     help=help_text)

    args = parser.parse_args()

    conf = CONF()
    conf.set_pdb_extn(args.pdbextn)
    conf.set_data_dir(args.datadir)
    # if user supplied dataset check if the ground truth was supplied else display warning
    # if proteus dataset set ground truth to proteus and display warning
    if args.datadir != __def_DATADIR__:
        if len(args.gtin) == 0:
            print('No ground-truth data supplied!')
            args.gtin = None
    else:
        print('Setting ground-truth data for proteus dataset')
        args.gtin = __def_GTIN__
    conf.set_gtin(args.gtin)
    conf.set_threads(args.threads)
    conf.set_weights(args.weights)
    conf.set_prog_dir(args.progdir)

    # End of configuration
    print(conf)

    psc_methods = ['ce', 'fast', 'gralign', 'tmalign', 'usm']
    psc_method_names = ['ce', 'fast', 'gralign', 'tmalign', 'usm']

    print("Running pairwise PSC jobs")
    if not RunPairwisePSC().run(conf):
        return

    print("Running post processing")
    PostProcessor().run(conf)
    print("Imputing")
    impute(conf.OUTDIR)
    print("Making MCPSC consensus scores")
    if conf.WEIGHTS is None:
        mcpsc(conf.OUTDIR, psc_cols=psc_methods)
    else:
        mcpsc(
            conf.OUTDIR,
            map(float,
                conf.WEIGHTS.split(',')),
            psc_cols=psc_methods)

    if conf.GTIN is None:
        print(
            'Not performing performance benchmarking because no ground-truth file supplied')
        return

    print("Nearest-neighbor classification")
    nnclassify(conf.OUTDIR, conf.WEIGHTS is not None, psc_cols=psc_methods)
    print("Making ROC curves")
    rocauc(conf.OUTDIR, conf.WEIGHTS is not None, psc_cols=psc_methods)
    mixedroc(conf.OUTDIR, conf.WEIGHTS is not None)
    print("Running MDS and clustering")
    mdsclust(conf.OUTDIR, conf.THREADS, psc_cols=psc_methods)
    print("Making Heatmaps")
    heatmap(conf.OUTDIR, psc_cols=psc_methods)
    print("Making Phylogenetic Trees")
    phylotree(conf.OUTDIR, conf.WORKDIR, psc_cols=psc_methods, psc_names=psc_method_names)
    print("Done")


def onexit(param):
    print('exiting ', param)


def main():
    try:
        process()
        print('Done')
    except (KeyboardInterrupt, SystemExit):
        sys.exit(-1)


if __name__ == '__main__':
    main()
