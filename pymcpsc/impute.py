# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods for missing value fill.
"""
import os
import pandas as pd
import numpy as np


def cmean2(x, f, mean_v):
    if x[2] and not np.isnan(x[2]):
        return x[2]
    r = np.mean(f[x[0]] + f[x[1]])
    if np.isnan(r):
        return mean_v
    return r


def make(OUTDIR='outdir'):
    """ Fills missing data per column for the pairwise PSC scores.
    """
    full_psc_data = pd.read_csv('%s%sprocessed.csv' % (OUTDIR, os.path.sep))
    full_psc_data = full_psc_data.replace([-1], [None])

    for col in full_psc_data.columns[8:]:
        print('.')
        # print col, len(full_psc_data[col].dropna())
        mean_v = full_psc_data[col].mean()

        # local mean fill
        f1 = full_psc_data[['dom1', col]]
        f2 = f1.groupby(by='dom1', as_index=True)
        f = {}
        # print 'making map'
        f_isnan = lambda x: filter(lambda i: not np.isnan(i), x)
        for k in np.unique(f1['dom1']):
            # NOTE THE ADDED DROPNA HERE FOR PY3
            f[k] = list(f_isnan(f2.get_group(k)[col].dropna()))
        # print 'going for mean'

        full_psc_data['%s_fill_mean' % col] = full_psc_data[
            ['dom1', 'dom2', col]].apply(lambda x: cmean2(x, f, mean_v), axis=1)

    full_psc_data.to_csv('%s%sprocessed.imputed.csv' % (OUTDIR, os.path.sep))

if __name__ == '__main__':
    make()
