# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Methods for generating the ROC with mixed PSC and MCPSC performances.

Functions:
    - *make*: main entry method
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

    :param outdir: (string) Path to output directory where program data files are written
    :param do_user_mcpsc: (boolean) Include/Exclude user weighting based MCPSC score based ROC charts
    :rtype: None
    """
    print('Generating mixed ROC')
    base_with_tmalign = outdir + os.path.sep

    def reader(name):
        """ Read the flase-positive-rate and true-positive-rate files.

        :param name: (float) Path to the data file
        :rtype: None
        """
        return list(map(lambda x: float(x.replace('\n', '')), open(name)))

    def plot(roc_data, auc_data, colnames, colors, path):
        """ Create a plot for the provided data, write to file and close.

        :param roc_data: (list) ROC (fpr-tpr) for each PSC method
        :param auc_data: (list) AUC for each PSC method
        :param colnames: (list) List of columns to be included in the plot
        :param colors: (list) Color (strings) to use corresponding to each column
        :param path: (string) Path to the output chart file
        :rtype: None
        """
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

    # read the false-positive-rate and true-positive-rate data files and
    # generate for each of the three datasets (original, reduced and imputed)
    for typ in ['full', 'reduced', 'imputed']:
        print('.')
        # read the data
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

        # prepare the pairs of matrices to pass for plotting
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
