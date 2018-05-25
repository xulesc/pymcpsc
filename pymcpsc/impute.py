# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
"""Methods for missing value fill.

Functions:
 - *cmean2*: creates the heatmap files for the data passed
 - *make*: main entry method

A "local average fill" scheme is used to compensate for potentially missing data for each
PSC method.
"""

import os
import pandas as pd
import numpy as np


def cmean2(x, f, mean_v):
    """
    Calculates the mean value for a missing pairwise similarity score.

    :param x:  (dataframe row)   Containing domain 1, domain 2, current similarity value
    :param f:  (dataframe)  Pairwise similarity data from which mean will be calculated
    :param mean_v:  (float)  Global mean similarity score
    :rtype: float
    """
    if x[2] and not np.isnan(x[2]):
        return x[2]
    r = np.mean(f[x[0]] + f[x[1]])
    if np.isnan(r):
        return mean_v
    return r


def make(OUTDIR='outdir'):
    """ Fills missing data per column for the pairwise PSC scores.

    Assuming that pairwise PSC scores were successfully generated for s
    domain pairs (out of the total P pairs in a dataset), the number of missing 
    pairwise scores is P - s, with the value of s being different across PSC 
    methods. To impute the missing data for each PSC method, the following 
    steps are repeated for all domain pairs (d_i , d_j) with a missing score:

    - find the set of PSC scores where d_i is the first domain in the pair
    - find the set of PSC scores where d_j is the second domain in the pair
    - merge the two sets and use the mean value of scores in the set union as the PSC score for that domain pair
    - if the two aforementioned sets are empty then use the global average of scores for that PSC method to supply the missing score's value.

    :param outdir: (string) Path to output directory where processed data files can be found
    :rtype: None    
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

        def f_isnan(x): return filter(lambda i: not np.isnan(i), x)
        for k in np.unique(f1['dom1']):
            # NOTE THE ADDED DROPNA HERE FOR PY3
            f[k] = list(f_isnan(f2.get_group(k)[col].dropna()))
        # print 'going for mean'

        full_psc_data['%s_fill_mean' % col] = full_psc_data[
            ['dom1', 'dom2', col]].apply(lambda x: cmean2(x, f, mean_v), axis=1)

    full_psc_data.to_csv('%s%sprocessed.imputed.csv' % (OUTDIR, os.path.sep))
