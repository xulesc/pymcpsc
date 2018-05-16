# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods for generating the ROC with mixed PSC and MCPSC performances.
"""
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import os
from sklearn import metrics

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def make(outdir='outdir', do_user_mcpsc=True):
    """ Generates mixed PSC and MCPSC ROCs.
    """
    print('Generating mixed ROC')
    base_with_tmalign = outdir + os.path.sep

    def reader(name):
        return list(map(lambda x: float(x.replace('\n', '')), open(name)))

    def plot(roc_data, auc_data, colnames, colors, path):
        matplotlib.rc('font', size=12)
        plt.figure(figsize=(5.5, 4))

        for i in range(len(colnames)):
            lines = plt.plot(
                roc_data[i][0],
                roc_data[i][1],
                label='%s (%.2f)' %
                (colnames[i].upper(), auc_data[i]),
                color=colors[i])
            plt.setp(lines, linewidth=4.0)

        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

    for typ in ['full', 'reduced', 'imputed']:
        print('.')
        fpr_tm = reader('%stmalign_%s_fpr' % (base_with_tmalign, typ))
        tpr_tm = reader('%stmalign_%s_tpr' % (base_with_tmalign, typ))
        fpr_ce = reader('%sce_%s_fpr' % (base_with_tmalign, typ))
        tpr_ce = reader('%sce_%s_tpr' % (base_with_tmalign, typ))
        fpr_gralign = reader('%sgralign_%s_fpr' % (base_with_tmalign, typ))
        tpr_gralign = reader('%sgralign_%s_tpr' % (base_with_tmalign, typ))
        fpr_fast = reader('%sfast_%s_fpr' % (base_with_tmalign, typ))
        tpr_fast = reader('%sfast_%s_tpr' % (base_with_tmalign, typ))
        fpr_usm = reader('%susm_%s_fpr' % (base_with_tmalign, typ))
        tpr_usm = reader('%susm_%s_tpr' % (base_with_tmalign, typ))

        # fpr_m4_w = reader('%smcpsc_fill_3_%s_fpr' % (base_with_tmalign, typ))
        # tpr_m4_w = reader('%smcpsc_fill_3_%s_tpr' % (base_with_tmalign, typ))
        # fpr_m3_w = reader('%smcpsc_fill_2_%s_fpr' % (base_with_tmalign, typ))
        # tpr_m3_w = reader('%smcpsc_fill_2_%s_tpr' % (base_with_tmalign, typ))
        if typ == 'imputed':
            fpr_m_w = reader(
                '%smcpsc_fill_median_%s_fpr' %
                (base_with_tmalign, typ))
            tpr_m_w = reader(
                '%smcpsc_fill_median_%s_tpr' %
                (base_with_tmalign, typ))
        else:
            fpr_m_w = reader(
                '%smcpsc_full_median_%s_fpr' %
                (base_with_tmalign, typ))
            tpr_m_w = reader(
                '%smcpsc_full_median_%s_tpr' %
                (base_with_tmalign, typ))

    # b: blue
    # g: green
    # r: red
    # c: cyan
    # m: magenta
    # y: yellow
    # k: black
    # w: white

        fprs = [
            fpr_m_w,
            # fpr_m4_w,
            fpr_tm,
            fpr_ce,
            fpr_gralign,
            fpr_fast,
            fpr_usm]
        tprs = [
            tpr_m_w,
            # tpr_m4_w,
            tpr_tm,
            tpr_ce,
            tpr_gralign,
            tpr_fast,
            tpr_usm]
        zip_fpr_tpr = []
        for i in range(len(fprs)):
            zip_fpr_tpr.append((fprs[i], tprs[i]))
        aucs = list(map(lambda x: metrics.auc(x[0], x[1]), zip_fpr_tpr))
        plot(
            zip_fpr_tpr, aucs, [
                'Median MCPSC', 'TMALIGN', 'CE', 'GRALIGN', 'FAST', 'USM'], [
                'm', 'b', 'g', 'k', 'c', 'y'], 'figures%s%s_mcpsc_psc_roc_with.png' %
            (os.path.sep, typ))
