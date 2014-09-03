"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 16/07/2014
Script to collapse MWEs in a CCGbank .auto style file
usage:
$python collapse_autofile.py autofile mwefile outfile method
-------------------------------------------------------------------------
Input: CCGbank files (.auto ) and a (.mwe) files containing:
the ID of each tree and their list of mwes separated by a space and with
units joined by an underscore
e.g:
san_francisco_bay end_up
-------------------------------------------------------------------------
Output: the same files with collapsed trees (.auto files) 
"""

from MWE_collapse_tree import MWE_tree_collapser
import re
from ccg_nltk_trees import get_Tree
import sys
#from CCGbank_collapse import get_deps_from_parg

"""
Input files
"""
treeAutofile = sys.argv[1]
mwefile = sys.argv[2]
IDpattern = re.compile(r"(ID=(wsj_\d*\.(\d*)))(.*)\n(.*)\n")

"""
Output files
"""
outtreefile = open(sys.argv[3], "w")

"""
Parameters
"""
method = sys.argv[4]
#method = "Rightmost"
#method = "Leftmost"

"""
processing
"""
textT = ''.join(open(treeAutofile, "r").readlines())
textM = ''.join(open(mwefile, "r").readlines()) 

# Find the ID line in the tree file and in the mwe file
mT = re.findall(IDpattern, textT)
mM = re.findall(IDpattern, textM)
"""
@warning: lengths must be same as len(mT) and len(mM)
"""
print "collapsing autofile\n"
for s_i in range(len(mT)):
    matchT = mT[s_i]
    matchM = mM[s_i]     
    outtreefile.write("%s\n"%(matchT[0]))
    #print matchM
    MWElist = matchM[4].split(" ")
    MWElist.pop()
    # get the tree
    treeID = matchT[1]
    try:
        Tree = get_Tree(treeAutofile, treeID)
        TCollapser = MWE_tree_collapser(Tree,MWElist, method = method)
        TCollapser.collapse_tree()
        Tree = TCollapser.Tree
        t = Tree.pprint()
        # write to .auto file
        outtreefile.write("%s\n"%t)
    except:
        ValueError
        outtreefile.write(" no parse: No vit. parse\n")

outtreefile.close()
print "Done\n"
