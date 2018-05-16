
import sys

import pandas as pd
import dendropy
try:
    from ete3 import Tree, NodeStyle, TreeStyle
except Exception as e:
    print(
        'ete3 installation does not seem correct. pymcpsc phylogentic tree feature may not work correctly. (%s)' % str(e))
import os


def plot_phylo_tree(rdata, colname, name, workdir, outdir):
    print('\t', colname)
    dist_file = '%s%sdist.csv' % (workdir, os.path.sep)
    dendro_path = '%s%s%s_dendro.nw' % (outdir, os.path.sep, name)
    tree_path = "figures%s%s_ptree.png" % (os.path.sep, name)

    try:
        p = rdata.pivot(index='dom1', columns='dom2', values=colname)
    except:
        print('pivot not generated for %s' % colname)
        return

    for i in range(len(p)):
        p.iloc[i][i] = 1
    # (convert to distance matrix)
    p = 1 - p
    p.to_csv(dist_file)

    # make name to class matrix
    dom_classification = dict(rdata[['dom1', 'cath1']].as_matrix())
    classes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']  # SCOP
    cl = [
        'blue',
        'green',
        'red',
        'cyan',
        'magenta',
        'yellow',
        'black',
        'black',
        'black',
        'black',
        'black',
        'black']
    class_color = dict(list(zip(classes, cl)))

    # make SCOP Class domains
    scop_class_domains = {}
    for k, v in dom_classification.items():
        scop_class = v[:1]
        if scop_class_domains.get(scop_class) is None:
            scop_class_domains[scop_class] = [k]
        else:
            scop_class_domains[scop_class].append(k)

    try:
        pdm1 = dendropy.PhylogeneticDistanceMatrix.from_csv(
            src=open(dist_file), delimiter=",")
    except:
        print('error reading file', dist_file)
        return
    nj_tree = pdm1.nj_tree()
    nj_tree.write(file=open(dendro_path, 'w'), schema='newick')

    # make the tree to visualize
    # open("/tmp/test.tre").readlines()[0].replace('\n','').replace('[&U]','')
    t = Tree(str(nj_tree) + ';')

    # Creates an independent node style for each node, which is
    # initialized with a foreground color depending on node class.
    for n in t.traverse():
        if not n.is_leaf():
            continue
        dom_class = dom_classification[n.name.replace('\'', '')]
        nstyle = NodeStyle()
        nstyle["fgcolor"] = class_color[dom_class[0]]
        nstyle["size"] = 25
        n.set_style(nstyle)

    circular_style = TreeStyle()
    circular_style.mode = "c"
    # circular_style.arc_start = -180 # 0 degrees = 3 o'clock
    # circular_style.arc_span = 180

    t.render(tree_path, tree_style=circular_style)

    # calculate all-to-all distances
    # same class                       different classes
    # total distance, number of nodes, total distance, number of nodes
    f_distances = [[0, 0, 0, 0],  # a
                   [0, 0, 0, 0],  # b
                   [0, 0, 0, 0],  # c
                   [0, 0, 0, 0],  # d
                   [0, 0, 0, 0]]  # e
    class_idx = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
    for n_start in t.traverse():
        if not n_start.is_leaf():
            continue
        n_start_class = dom_classification[n_start.name.replace('\'', '')][0]
        f_distance = f_distances[class_idx[n_start_class]]
        for n_end in t.traverse():
            if not n_end.is_leaf():
                continue
            if n_start == n_end:
                continue
            d = n_start.get_distance(n_end, topology_only=True)
            n_end_class = dom_classification[n_end.name.replace('\'', '')][0]
            if n_start_class == n_end_class:
                f_distance[0] += d
                f_distance[1] += 1
            else:
                f_distance[2] += d
                f_distance[3] += 1
    # print name
    # for f_distance in f_distances:
    #    print ','.join(map(str, f_distance))

    return True


def make(outdir='outdir',
         workdir='work',
         cols=['tmalign_fill_mean', 'ce_fill_mean', 'fast_fill_mean',
                 'gralign_fill_mean', 'usm_fill_mean', 'mcpsc_fill_0',
                 'mcpsc_fill_1', 'mcpsc_fill_2', 'mcpsc_fill_3',
                 'mcpsc_fill_4', 'mcpsc_fill_median'],
         names=['tmalign', 'ce', 'fast', 'gralign', 'usm', 'M1',
                'M2', 'M3', 'M4', 'M5', 'Median_MCPSC']):
    """ Manages creation of Phylogenetic Trees. Reades in pairwise domain
    PSC and MCPSC scores from a file. Trees are then generated for each
    method.
    """
    rdata = pd.read_csv(
        '%s%sprocessed.imputed.mcpsc.csv' %
        (outdir, os.path.sep))
    list(map(lambda x: plot_phylo_tree(rdata, x[0], x[
        1], workdir, outdir), list(zip(cols, names))))
