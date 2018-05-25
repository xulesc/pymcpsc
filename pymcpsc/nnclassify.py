# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods for leave-one-out nearest neighbor classification with pairwise
similiarty score matrices.

Functions:
    - *_nnclassifyacc*: Calculates the nearest neighbor for each domain by creating a pivot table.
    - *nnclassifyacc*: Calculates the performance of nearest neighbor classifier.
    - *multi_nnclassifyacc*:
    - *make*: main entry method
    
Leave-one-out nearest neighbor analysis accuracy performances of classifiers built with PSC and MCPSC scores.
"""
import os
import pandas as pd
from collections import Counter


def _nnclassifyacc(df, colname):
    """Calculates the nearest neighbor for each domain by creating a pivot table.

    :param df: (dataframe) Dataframe containing pairwise similarity scores of domains
    :param colname: (list) PSC method for which the nearest neighbors are to be calculated
    :rtype: (list) Domain pairs and corresponding scores where the pairs are nearest neighbors
    """
    # create pivot table from domain pairs
    p = df.pivot(index='dom1', columns='dom2', values=colname)
    # find the column with max value for each row
    nnidxs = p.idxmax(axis=1)
    # find the score corresponding to nearest neighbor pairs
    scores = []
    for d1, d2 in zip(nnidxs.index, nnidxs):
        scores.append(p[d1][d2])
    return zip(nnidxs.index, nnidxs, scores)


def nnclassifyacc(df, colname, klass):
    """Calculates the performance of nearest neighbor classifier.

    :param df: (dataframe) Dataframe containing pairwise similarity scores of domains
    :param colname: (list) PSC method for which the nearest neighbors are to be calculated
    :param klass: (dict) Key-value pair of domain and their classifications.
    :rtype: (float) Accuracy
    """
    try:
        dfi = df.dropna(subset=[colname])
        total = len(dfi['dom1'].unique())
        correct = 0
        for dom1, dom2, s in _nnclassifyacc(dfi, colname):
            correct += klass[dom1] == klass[dom2]
        return correct * 1.0 / total
    except:
        return 0


def make(
    outdir='outdir', do_user_mcpsc=True,
        psc_cols=[]):
    """ Generates leave-one-out nearest neighbor analysis accuracy performances of
    classifiers built with PSC and MCPSC scores.

    :param outdir: (string) Path to output directory where processed data files can be found
    :param do_user_mcpsc: (boolean) Include/Exclude user weights based consensus scores
    :param psc_cols: (list) List of psc method names to be included in mean calculations
    :rtype: None
    """

    # define column names for which nn performance is to be calculated
    imputed_cols = map(lambda x: '%s_fill_mean' % x, psc_cols)
    if do_user_mcpsc:
        mcpsc_cols = [
            'mcpsc_fill_0',
            'mcpsc_fill_1',
            'mcpsc_fill_2',
            'mcpsc_fill_3',
            'mcpsc_fill_4']
    else:
        mcpsc_cols = [
            'mcpsc_fill_0',
            'mcpsc_fill_1',
            'mcpsc_fill_2',
            'mcpsc_fill_3']

    # read the similarity scores data
    full_psc_data = pd.read_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))

    # create the domain-classification maps
    d2l1 = {}
    d2l2 = {}
    d2l3 = {}
    d2l4 = {}
    for d, k in full_psc_data[['dom1', 'cath1']].as_matrix():
        s = k.split('.')
        d2l1[d] = s[0]
        d2l2[d] = '.'.join(s[:2])
        d2l3[d] = '.'.join(s[:3])
        d2l4[d] = '.'.join(s[:4])

    # build NNs for the three datasets and all PSC methods and calculate
    # performance
    print('Nearest Neighbor Performances')
    print('\% original psc methods')
    for method in psc_cols:
        perfs = [method]
        for dmap in [d2l1, d2l2, d2l3, d2l4]:
            perfs.append('%0.2f' % nnclassifyacc(full_psc_data, method, dmap))
        print(' & '.join([method] + perfs) + ' \\\hline')
    print('\% common subset psc methods')
    for method in psc_cols:
        perfs = [method]
        for dmap in [d2l1, d2l2, d2l3, d2l4]:
            perfs.append(
                '%0.2f' %
                nnclassifyacc(
                    full_psc_data.dropna(
                        subset=psc_cols),
                    method,
                    dmap))
        print(' & '.join([method] + perfs) + ' \\\hline')
    print('\% imputed psc methods')
    for method in imputed_cols:
        perfs = [method]
        for dmap in [d2l1, d2l2, d2l3, d2l4]:
            perfs.append('%0.2f' % nnclassifyacc(full_psc_data, method, dmap))
        print(' & '.join([method] + perfs) + ' \\\hline')

    print('\% original mcpsc methods')
    for method in map(lambda x: x.replace('fill', 'full'), mcpsc_cols):
        perfs = [method]
        for dmap in [d2l1, d2l2, d2l3, d2l4]:
            perfs.append('%0.2f' % nnclassifyacc(full_psc_data, method, dmap))
        print(' & '.join([method] + perfs) + ' \\\hline')
    print('\% common subset mcpsc methods')
    for method in map(lambda x: x.replace('fill', 'full'), mcpsc_cols):
        perfs = [method]
        for dmap in [d2l1, d2l2, d2l3, d2l4]:
            perfs.append(
                '%0.2f' %
                nnclassifyacc(
                    full_psc_data.dropna(
                        subset=psc_cols),
                    method,
                    dmap))
        print(' & '.join([method] + perfs) + ' \\\hline')
    print('\% imputed mcpsc methods')
    for method in mcpsc_cols:
        perfs = [method]
        for dmap in [d2l1, d2l2, d2l3, d2l4]:
            perfs.append('%0.2f' % nnclassifyacc(full_psc_data, method, dmap))
        print(' & '.join([method] + perfs) + ' \\\hline')
