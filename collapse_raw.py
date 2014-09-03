"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 05/08/2014
usage:
python collapse_raw.py rawfile mwefile outfile
"""
from MWE_collapse_tree import MWE
from collapse_helper import leaf_collapser
import re
import sys
            
test = open(sys.argv[1], "r")
mwefile = sys.argv[2]
IDpattern = re.compile(r"(ID=(wsj_\d*\.(\d*)))(.*)\n(.*)\n")
#could use gold_test -->decollapse, get_mwe_span_from_coll_leaves
textM = ''.join(open(mwefile, "r").readlines()) 
mM = re.findall(IDpattern, textM)
test = [line for line in test]
out = open(sys.argv[3], "w")

"""
@todo: parametrise mwefile
"""

for line, matchM in zip(test, mM):
    leaves = line.split()
    MWElist = matchM[4].split(" ")
    MWElist.pop()
    for i in range(len(MWElist)):
        MWElist[i] = MWE(MWElist[i])
    lc = leaf_collapser(MWElist, leaves)
    collapsed_leaves = lc.collapse_leaves(MWElist, leaves)
    out.write(" ".join(collapsed_leaves))
    out.write("\n")
out.close()
