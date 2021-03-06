"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 16/07/2014
Script to collapse MWEs in CCGbank-style parg files
usage:
$python collapse_pargfile.py autofile pargfile mwefile outfile
-------------------------------------------------------------------------
Input: CCGbank files (.auto) (.parg ) and a (.mwe) files containing:
the ID of each tree and their list of mwes separated by a space and with
units joined by an underscore
e.g:
san_francisco_bay end_up
-------------------------------------------------------------------------
Output: the parg files collapsed
"""

from MWE_collapse_deps import MWE_deps_collapser
import re
from ccg_nltk_trees import get_Tree
import sys
from collapse_helper import leaf_collapser, MWE, get_deps_from_parg

"""
Input files
"""
treeAutofile = sys.argv[1] #"/afs/inf.ed.ac.uk/user/s11/s1160147/Project/EXP/modelA/parses.rf.auto"#
pargfile = sys.argv[2] #"/afs/inf.ed.ac.uk/user/s11/s1160147/Project/EXP/modelA/parses.r.parg"

mwefile = sys.argv[3] #"/afs/inf.ed.ac.uk/user/s11/s1160147/Project/EXP/modelBs/rec_3/test.mwe" #
IDpattern = re.compile(r"(ID=(wsj_\d*\.(\d*)))(.*)\n(.*)\n")
IDpatternB = re.compile(r"<s id=\"(.*)\"> \d*(.*)") 

"""
Output files
"""
pargout = open(sys.argv[4], "w")
#open("/afs/inf.ed.ac.uk/user/s11/s1160147/Project/EXP/modelA/collapsed/rec_3/parses.coll.autom.parg", "w")


"""
processing
"""
textT = ''.join(open(treeAutofile, "r").readlines())
textM = ''.join(open(mwefile, "r").readlines()) 

textD = ''.join(open(pargfile, "r").readlines())
sentencesD = textD.split('<\\s>\n')
sentencesD.pop()

# Find the ID line in the tree file and in the mwe file
mT = re.findall(IDpattern, textT)
mM = re.findall(IDpattern, textM)
"""
@warning: lengths must be same as len(mT) and len(mM)
"""
print "collapsing pargfile"
for s_i in range(len(mT)):
    matchT = mT[s_i]
    matchM = mM[s_i]     
    sentence = sentencesD[s_i]
    lines = sentence.split("\n")            
    # If the tree IDs correspond
    mD = re.findall(IDpatternB,lines[0]) #parg file
    pargout.write("%s\n"%(lines[0]))
    #print matchM
    MWElist = matchM[4].split(" ")
    MWElist.pop()
    for mwe in range(len(MWElist)):
        MWElist[mwe] = MWE(MWElist[mwe])
    # get the tree
    treeID = matchT[1]
    try:
        Tree = get_Tree(treeAutofile, treeID)
        Oleaves = Tree.leaves()
        cwordandpos = Tree.get_word_and_pos()
        lc = leaf_collapser(Oleaves, cwordandpos, MWElist, method="wordandpos")
        CwordAndPos = lc.collapse_leaves()
        deps = get_deps_from_parg(lines)
        Collapser = MWE_deps_collapser(deps, MWElist, Oleaves, CwordAndPos)
        Collapser.collapse()
    
        # write to .parg file
        for dep in deps:
            pargout.write(dep.__str__())
        pargout.write("<\s>\n")
             
            # write to .auto file
            #outtreefile.write("%s\n"%t)
    except:
            ValueError
            pargout.write("<\s>\n")
            #outtreefile.write(" no parse: No vit. parse\n")

#outtreefile.close()
print "Done\n"
