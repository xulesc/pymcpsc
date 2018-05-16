# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
"""Methods used for calculating the consensus scores.
"""
import os
import pandas as pd
import numpy as np


def get_wv_dataset_size(df, colnames):
    w1 = [len(df[x].dropna()) for x in colnames]
    return 1.0 * np.array(w1) / len(df)


def get_wv_dataset_col_rmsd(df, colnames):
    X = df[colnames].dropna().as_matrix()
    raw_sums = [0.0] * len(colnames)
    for _, i1 in zip(colnames, range(len(colnames))):
        for _, i2 in zip(colnames, range(len(colnames))):
            d = X[:, i1] - X[:, i2]
            raw_sums[i1] += np.dot(d, d)
    np_raw_sums = np.array(raw_sums) / (len(raw_sums) - 1)
    return np_raw_sums / max(np_raw_sums)


def get_weights(dataframe, ws_u, psc_cols):
    # weight vector is average of methods
    wa = np.array([1, 1, 1, 1, 1])
    # weight vector from size of dataset processed
    w1 = get_wv_dataset_size(dataframe, psc_cols)
    # weight vector from mean RMS per PSC method
    w2 = get_wv_dataset_col_rmsd(dataframe, psc_cols)
    # weight vector from main eigenvector
    # df = dataframe[psc_cols]
    # df = df.where((pd.notnull(df)), None)
    # X = csr_matrix(df, dtype=float)
    # u, s, vt = svds(X, k=1)
    # w3 = vt[0]
    # weight vector from size of dataset processed by halving USM influence
    wp = w1 * [1, 1, 1, 1, 0.5]
    # ws = [5.513287455, 2.9339976339, 5.4314202582, 11.8588931514, 0.3673017899] #scop
    # ws = [5.66859730521,2.85204498797,5.7410826929,10.7251782679,-0.508664041092] #cath
    # user supplied weights
    ws = ws_u  # [2.55,1.79,4.23,14.36,-0.38] # for proteus
    return [
        pd.Series(wa),
        pd.Series(w1),
        pd.Series(wp),
        pd.Series(w2),
        # pd.Series(w3),
        pd.Series(ws)]

# the weight vector should be same length as x and be the combined
# weights to be appplied


def wmean(x, w):
    valid_val_idxs = ~np.isnan(x)
    _v = x[valid_val_idxs]
    _w = w[valid_val_idxs]
    _r = np.dot(_v, _w) / sum(_w)
    return _r


def make(
    outdir='outdir',
    weights_u=[
        1,
        1,
        4,
        1,
        1],
        psc_cols=[], do_user_mcpsc=True):
    """The main method for generating the consensus scores. Expects to load
    the imputed data file and writes as output a file with consensus scores
    appended for each protein domain pair.
    """
    imputed_psc_cols = list(map(lambda x: '%s_fill_mean' % x, psc_cols))
    # processing
    full_psc_data = pd.read_csv(
        '%s%sprocessed.imputed.csv' %
        (outdir, os.path.sep), na_values='')
    # full_psc_data = full_psc_data.replace([-1], [None])

    print('.')
    weights = get_weights(full_psc_data, weights_u, psc_cols)
    if not do_user_mcpsc:
        weights = weights[:-1]
    # print weights

    print('.')
    wl = len(weights)

    filled_data = full_psc_data[psc_cols]
    print('.')
    colnames_full = []
    for i in range(wl):
        cname = 'mcpsc_full_%d' % i
        colnames_full.append(cname)
        # print cname
        full_psc_data[cname] = filled_data.apply(
            lambda x: wmean(np.array(x), np.array(weights[i])), axis=1)

    filled_data = full_psc_data[imputed_psc_cols]
    print('.')
    colnames_fill = []
    for i in range(wl):
        cname = 'mcpsc_fill_%d' % i
        colnames_fill.append(cname)
        # print cname
        full_psc_data[cname] = filled_data.apply(
            lambda x: wmean(np.array(x), np.array(weights[i])), axis=1)

    full_psc_data['mcpsc_full_median'] = full_psc_data[
        colnames_full].median(axis=1)
    full_psc_data['mcpsc_fill_median'] = full_psc_data[
        colnames_fill].median(axis=1)

    print('.')
    full_psc_data.to_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))
