# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods for generating performance ROCs and data files for mixed ROC
creation.
"""
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import os
import pandas as pd
import random
import numpy as np
import itertools
import sys
from sklearn import metrics

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def makerocpercol(dataFrame, colname):
    df = dataFrame.dropna(subset=[colname])
    if len(df) == 0:
        return (None, None, None)
    gt = df['klass1'] == df['klass2']
    # print 'ones: ', sum(gt)
    X = df[colname]
    return metrics.roc_curve(gt, X)


def metrics_auc(fpr, tpr):
    try:
        return metrics.auc(fpr, tpr)
    except:
        print('calculation failed')
        return 0


def plot(roc_data, auc_data, colnames, path):
    matplotlib.rc('font', size=22)

    for i in range(len(colnames)):
        lines = plt.plot(
            roc_data[i][0], roc_data[i][1], label='%s (%0.2f)' %
            (colnames[i].upper(), auc_data[i]))
        plt.setp(lines, linewidth=4.0)

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")
    plt.savefig(path)
    plt.close()


def make(
    outdir='outdir', do_user_mcpsc=True,
    psc_cols=[
        'tmalign',
        'ce',
        'gralign',
        'fast',
        'usm']):
    """ Generates ROCs for performance of the PSC methods. Also generates data files
    required for generating mixed ROCs.
    """
    imputed_cols = map(lambda x: '%s_fill_mean', psc_cols)
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

    if not os.path.exists('figures'):
        os.makedirs('figures')

    # ROC/AUC at Topology Level
    full_psc_data['klass1'] = full_psc_data[['cath1']].apply(
        lambda x: '.'.join(x[0].split('.')[:3]), axis=1)
    full_psc_data['klass2'] = full_psc_data[['cath2']].apply(
        lambda x: '.'.join(x[0].split('.')[:3]), axis=1)

    def latex_print(cols, rows, data):
        print(
            '& ' +
            ' & '.join(
                (map(
                    lambda x: '\\textbf{%s}' %
                    x,
                    cols))) +
            '\\\\hline')
        for r, d in zip(rows, data):
            print(r + ' & ' + ' & '.join(map(str, d)) + '\\\\hline')

    def write_fp(col, typ, fpr, tpr):
        if fpr is None or tpr is None:
            return
        f = open('%s%s%s_%s_fpr' % (outdir, os.path.sep, col, typ), 'w')
        for o in fpr:
            f.write('%f\n' % o)
        f.close()
        f = open('%s%s%s_%s_tpr' % (outdir, os.path.sep, col, typ), 'w')
        for o in tpr:
            f.write('%f\n' % o)
        f.close()

    if True:
        f_roc = []
        r_roc = []
        i_roc = []
        f_auc = []
        r_auc = []
        i_auc = []
        for col in psc_cols:
            print('.')
            # full
            fpr, tpr, _ = makerocpercol(full_psc_data, col)
            write_fp(col, 'full', fpr, tpr)
            f_roc.append([fpr, tpr])
            f_auc.append(metrics_auc(fpr, tpr))
            # reduced
            fpr, tpr, _ = makerocpercol(
                full_psc_data.dropna(
                    subset=psc_cols), col)
            write_fp(col, 'reduced', fpr, tpr)
            r_roc.append([fpr, tpr])
            r_auc.append(metrics_auc(fpr, tpr))
            # imputed
            fpr, tpr, _ = makerocpercol(full_psc_data, '%s_fill_mean' % col)
            write_fp(col, 'imputed', fpr, tpr)
            i_roc.append([fpr, tpr])
            i_auc.append(metrics_auc(fpr, tpr))

        plot(f_roc, f_auc, psc_cols, 'figures%spsc_full_roc.png' % os.path.sep)
        plot(
            r_roc,
            r_auc,
            psc_cols,
            'figures%spsc_reduced_roc.png' %
            os.path.sep)
        plot(
            i_roc,
            i_auc,
            psc_cols,
            'figures%spsc_imputed_roc.png' %
            os.path.sep)
        print(psc_cols)
        print(['Original dataset'] + f_auc)
        print(['Common dataset'] + r_auc)
        print(['Imputed dataset'] + i_auc)

    # print 'make MCPSC ROCs/AUCs'
    mf_roc = []
    mr_roc = []
    mi_roc = []
    mf_auc = []
    mr_auc = []
    mi_auc = []
    for col in mcpsc_cols:
        print('.')
        # full
        fpr, tpr, _ = makerocpercol(full_psc_data, col.replace('fill', 'full'))
        write_fp(col, 'full', fpr, tpr)
        mf_roc.append([fpr, tpr])
        mf_auc.append(metrics_auc(fpr, tpr))
        # reduced
        fpr, tpr, _ = makerocpercol(
            full_psc_data.dropna(
                subset=psc_cols), col.replace(
                'fill', 'full'))
        write_fp(col, 'reduced', fpr, tpr)
        mr_roc.append([fpr, tpr])
        mr_auc.append(metrics_auc(fpr, tpr))
        # imputed
        fpr, tpr, _ = makerocpercol(full_psc_data, col)
        write_fp(col, 'imputed', fpr, tpr)
        mi_roc.append([fpr, tpr])
        mi_auc.append(metrics_auc(fpr, tpr))

    # median MCPSC ROC/AUC
    median_roc = []
    median_auc = []
    fpr, tpr, _ = makerocpercol(full_psc_data, 'mcpsc_full_median')
    write_fp('mcpsc_full_median', 'full', fpr, tpr)
    median_roc.append([fpr, tpr])
    median_auc.append(metrics_auc(fpr, tpr))

    fpr, tpr, _ = makerocpercol(
        full_psc_data.dropna(
            subset=psc_cols), 'mcpsc_full_median')
    write_fp('mcpsc_full_median', 'reduced', fpr, tpr)
    median_roc.append([fpr, tpr])
    median_auc.append(metrics_auc(fpr, tpr))

    fpr, tpr, _ = makerocpercol(full_psc_data, 'mcpsc_fill_median')
    write_fp('mcpsc_fill_median', 'imputed', fpr, tpr)
    median_roc.append([fpr, tpr])
    median_auc.append(metrics_auc(fpr, tpr))

    if True:
        if do_user_mcpsc:
            MS = ['M1', 'M2', 'M3', 'M4', 'M5']
        else:
            MS = ['M1', 'M2', 'M3', 'M4']
        plot(
            mf_roc, mf_auc, MS, 'figures%smcpsc_full_roc.png' %
            os.path.sep)
        plot(
            mr_roc, mr_auc, MS, 'figures%smcpsc_reduced_roc.png' %
            os.path.sep)
        plot(
            mi_roc, mi_auc, MS, 'figures%smcpsc_imputed_roc.png' %
            os.path.sep)
        plot(
            median_roc, median_auc, [
                'Median MCPSC (full)', 'Median MCPSC (imputed)'], 'figures%smcpsc_median.png' %
            os.path.sep)
        latex_print(MS,
                    ['Original dataset', 'Common dataset', 'Imputed dataset'],
                    [mf_auc, mr_auc, mi_auc])
        print('Median MCPSC AUCs')
        print(
            'Median MCPSC (full), Median MCPSC (reduced), Median MCPSC (imputed)')
        print(median_auc)
