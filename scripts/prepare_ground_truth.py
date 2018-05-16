#
"""
This is a utility script for preparing the ground truth file required by
pyMCPSC.

The script expects a file named scop_classifications.csv to exist in the
current working directory. A sample input file (for this scritp) can be
seen at tests/chew_kedem_dataset/scop_classifications.csv.

The output ground truth file is written to the current working directory.
"""


# read classification data
data = []
for inline in open('scop_classifications.csv'):
    dom, scop = inline.replace(' ', '').replace('\n','').split(',')
    data.append([dom, scop])

# create dom to class dict
dom_scop = dict(data)

# prepare all-to-all groundtruth file (triangular)
of = open('ground_truth', 'w')
doms = dom_scop.keys()
for i in range(len(dom_scop)):
    for j in range(i + 1, len(dom_scop)):
        outstr = '%s\t%s\t%s\t%s\n' %(doms[i], doms[j], dom_scop[doms[i]], dom_scop[doms[j]])
        of.write(outstr)
of.close()