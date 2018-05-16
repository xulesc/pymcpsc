# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods for leave-one-out nearest neighbor classification with pairwise
similiarty score matrices.
"""
import os
import pandas as pd
from collections import Counter


def _nnclassifyacc(df, colname):
    p = df.pivot(index='dom1', columns='dom2', values=colname)
    nnidxs = p.idxmax(axis=1)
    scores = []
    for d1, d2 in zip(nnidxs.index, nnidxs):
        scores.append(p[d1][d2])
    return zip(nnidxs.index, nnidxs, scores)


def nnclassifyacc(df, colname, klass):
    try:
        # print df.shape
        dfi = df.dropna(subset=[colname])
        # print dfi.shape
        total = len(dfi['dom1'].unique())
        correct = 0
        for dom1, dom2, s in _nnclassifyacc(dfi, colname):
            correct += klass[dom1] == klass[dom2]
        return correct * 1.0 / total
    except:
        return 0


def multi_nnclassifyacc(df, colnames, klass):
    ret = []
    for colname in colnames:
        r = _nnclassifyacc(df.dropna(subset=[colname]), colname)
        dmap = dict(map(lambda x: (x[0], (x[1], x[2])), r))
        ret.append(dmap)
    dlist = df['dom1'].unique()
    correct = 0
    for q in dlist:
        ds = []
        ss = []
        for e in ret:
            if e.get(q):
                v = e[q]
                ds.append(v[0])
                ss.append(v[1])
        if len(ds) == 0:
            continue
        cnt = Counter(ds)
        cntl = list(cnt.iteritems())
        # if no clear winner pick one with top score
        if len(cnt) > 1 and cntl[0][1] == cntl[1][1]:
            s = sorted(zip(ds, ss), key=lambda x: x[1], reverse=True)
            d = s[0][0]
        else:
            d = Counter(ds).most_common(1)[0][0]
        correct += klass[q] == klass[d]
    return correct * 1.0 / len(dlist)


def make(
    outdir='outdir', do_user_mcpsc=True,
        psc_cols=[]):
    """ Generates leave-one-out nearest neighbor analysis accuracy performances of
    classifiers built with PSC and MCPSC scores.
    """
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

    full_psc_data = pd.read_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))

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
