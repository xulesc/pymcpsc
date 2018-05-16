# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
"""Methods used for generating heatmaps.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import seaborn as sb
import os


def generate_heatmaps(
        folds,
        dom_classification,
        rdata,
        colname,
        outdir,
        make_images):
    fold_pair_distances = []
    for fold1 in folds:
        for fold2 in folds:
            x = rdata[
                np.logical_and(
                    rdata['fold1'] == fold1,
                    rdata['fold2'] == fold2)]
            d = x[colname].mean()
            fold_pair_distances.append([fold1, fold2, d])

    sorted_dom = sorted(dom_classification, key=dom_classification.get)
    dom_color = {'a': 'b', 'b': 'g', 'c': 'r', 'd': 'c', 'e': 'b'}

    fold_pair_distances_df = pd.DataFrame(fold_pair_distances)
    fold_pair_distances_df.columns = ['fold1', 'fold2', 'd']
    p1 = fold_pair_distances_df.pivot(
        index='fold1', columns='fold2', values='d')
    if make_images and len(p1) <= 300:
        fig, ax = plt.subplots(figsize=(8, 6))
        sb.heatmap(p1, ax=ax, cmap="YlGnBu")
        _ = [i.set_color(dom_color[j.split('.')[0]])
             for i, j in zip(plt.gca().get_xticklabels(), p1.index)]
        _ = [
            i.set_color(
                dom_color[
                    j.split('.')[0]]) for i, j in zip(
                plt.gca().get_yticklabels(), reversed(
                    p1.columns))]
        plt.tight_layout()
        fig.savefig('figures%s%s_fold_heatmap.png' % (os.path.sep, colname))
        plt.close(fig)
    p1.to_csv('%s%s%s_fold_heatmap.csv' % (outdir, os.path.sep, colname))

    similarity_map = dict(map(lambda x: [(x[0], x[1]), x[2]], rdata[
                          ['dom1', 'dom2', colname]].as_matrix()))
    for dom1 in sorted_dom:
        similarity_map[(dom1, dom1)] = 1

    p = [list(map(lambda x: similarity_map.get((dom1, x)), sorted_dom))
         for dom1 in sorted_dom]
    p_df = pd.DataFrame(p)
    p_df.columns = sorted_dom
    p_df.index = sorted_dom
    if make_images and len(p_df) <= 300:
        fig, ax = plt.subplots(figsize=(40, 40))
        sb.heatmap(p_df, ax=ax, cmap="YlGnBu")
        _ = [i.set_color(dom_color[dom_classification[j][0]])
             for i, j in zip(plt.gca().get_xticklabels(), sorted_dom)]
        _ = [
            i.set_color(
                dom_color[
                    dom_classification[j][0]]) for i, j in zip(
                plt.gca().get_yticklabels(), reversed(sorted_dom))]
        plt.tight_layout()
        fig.savefig('figures%s%s_dom_heatmap.png' % (os.path.sep, colname))
        plt.close(fig)
    p_df.to_csv('%s%s%s_dom_heatmap.csv' % (outdir, os.path.sep, colname))


def make(
    outdir='outdir',
    make_images=True,
    psc_cols=[
        'ce',
        'fast',
        'gralign',
        'tmalign',
        'usm']):
    """ Manages creation of Heatmaps. Reades in pairwise domain
    PSC and MCPSC scores from a file. Heatmaps are then generated for each
    method.
    """
    rdata = pd.read_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))

    # set class values for domains
    rdata['fold1'] = rdata.apply(
        lambda x: '.'.join(
            x['cath1'].split('.')[
                :2]), axis=1)
    rdata['fold2'] = rdata.apply(
        lambda x: '.'.join(
            x['cath2'].split('.')[
                :2]), axis=1)

    # make name to class matrix
    dom_classification = dict(rdata[['dom1', 'cath1']].as_matrix())

    # get unique folds
    folds = list(rdata['fold1'].unique())

    for colname in ['%s_fill_mean' % x for x in psc_cols]:
        generate_heatmaps(
            folds,
            dom_classification,
            rdata,
            colname,
            outdir,
            make_images)
    for colname in ['mcpsc_fill_%d' % x for x in range(5)] + ['mcpsc_fill_median']:
        generate_heatmaps(
            folds,
            dom_classification,
            rdata,
            colname,
            outdir,
            make_images)
