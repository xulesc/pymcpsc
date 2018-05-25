# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods used for performing Multi-dimensional Scaling and generating
scatter plots from the resulting coordinates.

Functions:
    - *cmdscale*: Classical multidimensional scaling (MDS)
    - *mdsscatter*: Perform MDS followed by generating scatter plots
"""
from __future__ import division

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os.path
import pandas as pd
import numpy as np

from sklearn.manifold import MDS

_s = 20 * 2

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def cmdscale(D):
    """ Classical multidimensional scaling (MDS)

    :param D: array (n, n) Symmetric distance matrix
    :rtype: array (n, p) Configuration matrix. Each column represents a dimension. Only the p dimensions corresponding to positive eigenvalues of B are returned. Note that each dimension is only determined up to an overall sign, corresponding to a reflection.
    :rtype: arry (n, ) Eigenvalues of B
    """
    # Number of points
    n = len(D)

    # Centering matrix
    H = np.eye(n) - np.ones((n, n)) / n

    # YY^T
    B = -H.dot(D**2).dot(H) / 2

    # Diagonalize
    evals, evecs = np.linalg.eigh(B)

    # Sort by eigenvalue in descending order
    idx = np.argsort(evals)[::-1]
    evals = evals[idx]
    evecs = evecs[:, idx]

    # Compute the coordinates using positive-eigenvalued components only
    w, = np.where(evals > 0)
    L = np.diag(np.sqrt(evals[w]))
    V = evecs[:, w]
    Y = V.dot(L)

    return Y, evals


def mdsscatter(
        raw_data,
        classes,
        cl,
        classes_dict,
        cath_c_dict,
        colname,
        fill,
        thresh=0.0,
        outdir='outdir',
        n_jobs=16):
    """ Performs MDS on pairwise similarity of a psc method in 2-dimensions
    and generates scatter plot for it.

    :param raw_data: (dataframe) Similarity scores data
    :param classes: (list) SCOP classes     
    :param cl: (list) Colors corresponding to the SCOP classes to be used in the plots
    :param classes_dict: (dict) Mapping of class to index
    :param cath_c_dict: (dict) Top level class to domain mapping
    :param fill: (boolean) Value to use for missing data
    :param thresh: (float) Threshold for similarity to exclude domain pairs
    :param outdir: (string) Path to output directory where processed data files can be found
    :param n_jobs: (int) Parallel processing for MDS calculation
    :rtype: None
    """
    matplotlib.rc('font', size=22)

    ODIR = 'figures'
    print('.')

    dataDf = raw_data[['dom1', 'dom2', colname]]
    dataDf = dataDf[dataDf[colname] >= thresh]
    #
    dom_dist = 1 - dataDf.pivot(index='dom1', columns='dom2', values=colname)

    Y_c = list(map(lambda x: int(cath_c_dict[x]), dom_dist.index))
    f = '%s%s%s.coord.%d.%f.txt' % (ODIR, os.path.sep, colname, fill, thresh)
    if os.path.isfile(f):
        o = np.loadtxt(f)
    else:
        X = dom_dist.replace(np.nan, fill).as_matrix()
        np.fill_diagonal(X, 0)
        mds = MDS(
            n_components=2,
            n_jobs=n_jobs,
            max_iter=90,
            dissimilarity='precomputed')
        o = mds.fit_transform(X)
        print('Stress (MDS minimizes this) of 2D emedding for %s: %f' %
              (colname, mds.stress_))

    plt.scatter(o[:, 0], o[:, 1], c=list(map(lambda x: cl[x], Y_c)), s=_s)
    plt.savefig('%s%s%s_mds_scatter.png' %
                (ODIR, os.path.sep, colname))
    plt.close()


def make(
    outdir='outdir',
    n_jobs=16,
        psc_cols=[]):
    """ Manages creation of MDS based scatter plots. Reades in pairwise domain
    PSC and MCPSC scores from a file. MDS followed by scatter plots are then
    generated for each PSC method.

    :param outdir: (string) Path to output directory where processed data files can be found
    :param n_jobs: (int) Number of parallel threads that can be used for the MDS step
    :param psc_cols: (list) List of psc method names to be included in mean calculations
    :rtype: None
    """
    raw_data = pd.read_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))

    cl = list('bgrcmykkkkk')
    classes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']  # SCOP

    classes_dict = dict(zip(classes, range(len(classes))))
    cath_c_dict = dict()
    idx = 0
    cath_a_dict = dict()
    for line in open(
        '%s%sprocessed.imputed.mcpsc.csv' %
            (outdir, os.path.sep)):
        idx += 1
        if idx == 1:
            continue
        data = line.split(',')
        d = data[4].split('.')
        cath_c_dict[data[2]] = classes_dict[d[0]]
        cath_a_dict[data[2]] = '.'.join(d[:2])

    print('Make MDS scatter plots')
    for x in list(map(lambda x: '%s_fill_mean' %
                      x, psc_cols)) + list(map(lambda x: 'mcpsc_fill_%d' %
                                               x, range(5))) + ['mcpsc_fill_median']:
        try:
            mdsscatter(
                raw_data,
                classes,
                cl,
                classes_dict,
                cath_c_dict,
                x,
                1,
                0,
                outdir,
                int(n_jobs))
        except:
            pass
