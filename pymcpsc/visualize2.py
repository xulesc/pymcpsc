# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods used for performing Multi-dimensional Scaling and generating
scatter plots from the resulting coordinates.
"""
from __future__ import division

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import sys
import os.path
import pandas as pd
import numpy as np
from collections import defaultdict

from sklearn.manifold import MDS
from sklearn.metrics import explained_variance_score
from sklearn.decomposition import PCA

import numpy.linalg as la
import numpy as np

_s = 20 * 2

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def cmdscale(D):
    """
    Classical multidimensional scaling (MDS)

    Parameters
    ----------
    D : (n, n) array
        Symmetric distance matrix.

    Returns
    -------
    Y : (n, p) array
        Configuration matrix. Each column represents a dimension. Only the
        p dimensions corresponding to positive eigenvalues of B are returned.
        Note that each dimension is only determined up to an overall sign,
        corresponding to a reflection.

    e : (n,) array
        Eigenvalues of B.

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


def nnclassify(p, colname, dom_class):
    nnidxs = p.idxmin(axis=1)
    return map(lambda x: int(dom_class[x]), nnidxs)


def get_eig(A):
    # square it
    A = A**2

    # centering matrix
    n = A.shape[0]
    J_c = 1. / n * (np.eye(n) - 1 + (n - 1) * np.eye(n))

    # perform double centering
    B = -0.5 * (J_c.dot(A)).dot(J_c)

    # find eigenvalues and eigenvectors
    eigen_val = la.eig(B)[0]
    eigen_vec = la.eig(B)[1].T

    idx = np.argsort(eigen_val)[::-1]
    evals = eigen_val[idx]
    evecs = eigen_vec[:, idx]

    return evals[:2], evec[:, :2]


def dNNClassify(
        raw_data,
        classes,
        cl,
        classes_dict,
        cath_c_dict,
        cath_a_dict,
        cath_t_dict,
        cath_h_dict,
        rev_cath_t,
        rev_cath_c,
        rev_cath_a,
        colname,
        fill,
        thresh=0.0,
        outdir='outdir',
        n_jobs=16):
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
        # print get_eig(X)
        # Y, evals = cmdscale(X)
        # print o
        # print Y
        # print evals
        # o = Y[:,:2]
        # o1 = PCA(n_components=2)
        # o1.fit(X)
        # print 'Variance explained by 2D emedding for %s: %f (variance explained)' %(colname, sum(o1.explained_variance_ratio_))
    # p_Y_c = nnclassify(dom_dist, colname, cath_c_dict)
    # print sum(np.absolute(np.array(Y_c) - np.array(p_Y_c)))
    # plt.scatter(o[:, 0], o[:, 1], c=map(lambda x: cl[x], p_Y_c), s=_s)
    # plt.savefig(
    #    '%s%s%s_mds_scatter_nn.png' %
    #    (ODIR, os.path.sep, colname))
    # plt.close()
    plt.scatter(o[:, 0], o[:, 1], c=list(map(lambda x: cl[x], Y_c)), s=_s)
    plt.savefig('%s%s%s_mds_scatter.png' %
                (ODIR, os.path.sep, colname))
    plt.close()
#


def make(
    outdir='outdir',
    n_jobs=16,
    psc_cols=[]):
    """ Manages creation of MDS based scatter plots. Reades in pairwise domain
    PSC and MCPSC scores from a file. MDS followed by scatter plots are then
    generated for each PSC method.
    """
    raw_data = pd.read_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))

    # print raw_data.shape

    ptex = lambda x: x.replace(
        '\n ',
        "\\\hline\n").strip().replace(
        '  ',
        ' & ').replace(
            '[',
            '').replace(
                ']',
        '')

    # Make dicts
    # print 'make dicts'
    cl = list('bgrcmykkkkk')
    classes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']  # SCOP
    # classes = ['1','2','3','4'] # CATH
    classes_dict = dict(zip(classes, range(len(classes))))
    cath_c_dict = dict()
    idx = 0
    cath_a_dict = dict()
    cath_t_dict = dict()
    cath_h_dict = dict()
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
        cath_t_dict[data[2]] = '.'.join(d[:3])
        cath_h_dict[data[2]] = data[4]

    # print 'reverse topology map'
    rev_cath_t = defaultdict(list)
    for k, v in cath_t_dict.items():
        rev_cath_t[v].append(k)
    # print len(rev_cath_t)

    rev_cath_a = defaultdict(list)
    for k, v in cath_a_dict.items():
        rev_cath_a[v].append(k)
    # print len(rev_cath_t)

    # print 'reverse class map'
    rev_cath_c = defaultdict(list)
    for k, v in cath_c_dict.items():
        rev_cath_c[v].append(k)
    # print len(rev_cath_c)

    print('Make MDS scatter plots')
    for x in list(map(lambda x: '%s_fill_mean' %
                      x, psc_cols)) + list(map(lambda x: 'mcpsc_fill_%d' %
                                               x, range(5))) + ['mcpsc_fill_median']:
        try:
            dNNClassify(
                raw_data,
                classes,
                cl,
                classes_dict,
                cath_c_dict,
                cath_a_dict,
                cath_t_dict,
                cath_h_dict,
                rev_cath_t,
                rev_cath_c,
                rev_cath_a,
                x,
                1,
                0,
                outdir,
                int(n_jobs))
        except:
            pass
