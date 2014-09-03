"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 24/07/2014
Script to combine model A and model B
dependencies to have gold standard to compare to
gold standard A
@todo: comment with understandable stuff
"""
from collapse_helper import decollapse, get_mwe_span_from_coll_leaves
from MWE_collapse_deps import MWE_deps_collapser, get_deps_from_parg
import re
from ccg_nltk_trees import get_Tree
from model_combiner import ModelCombiner
import sys

#usage:
# python combine_models.py pargA pargB autoB out medEdges
"""
INPUT
"""
modelA = sys.argv[1]
modelB = sys.argv[2] 
modelBauto = sys.argv[3] 
out = open(sys.argv[4], "w") 
"""
ID PATTERNS
"""
IDpattern = re.compile(r"(ID=(wsj_\d*\.\d*))(.*)\n(.*)\n")
IDpatternB = re.compile(r"<s id=\"(.*)\"> \d*(.*)") # just the id pattern

"""
Parameters
"""
#medEdges = "fromA"
#medEdges = "rightmostB"
medEdges = sys.argv[5] #"leftmostB"

"""
Combining
"""

textA = ''.join(open(modelA, "r").readlines())
sentencesA = textA.split('<\\s>\n')
sentencesA.pop()

textB = ''.join(open(modelB, "r").readlines())
sentencesB = textB.split('<\\s>\n')
sentencesB.pop()

autoB = ''.join(open(modelBauto, "r").readlines())
mTB = re.findall(IDpattern, autoB)

valerrors = 0
"""
@warning: sentencesA and sentencesB must be same length
"""
print "combining models"
for s_i, (senA, senB) in enumerate(zip(sentencesA, sentencesB)): 
    matchTB = mTB[s_i]

    linesA = senA.split("\n")          
    linesB = senB.split("\n")  
    # If the tree IDs correspond
    mDA = re.findall(IDpatternB,linesA[0]) #parg file
    mDB = re.findall(IDpatternB,linesB[0])
    out.write("%s\n"%(linesB[0]))
    
    # get the tree
    treeIDB = matchTB[1]
    
    try:
        TreeB = get_Tree(modelBauto, treeIDB)
        Cleaves = TreeB.leaves()
    except:
        # parse failure
        ValueError
        out.write("<\\s>\n")
        continue
        
    # Get mwes from collapsed and guess original leaves
    MWElist, Oleaves = decollapse(Cleaves)
    get_mwe_span_from_coll_leaves(MWElist, Oleaves, Cleaves)

    #get the dependencies
    depsA = get_deps_from_parg(linesA)
    depsB = get_deps_from_parg(linesB)
    
    CwordAndPos = TreeB.get_word_and_pos()
    Collapser = MWE_deps_collapser(depsB, MWElist, Oleaves, CwordAndPos)
    MWEdict = Collapser.get_MWE_dict(MWElist, Oleaves, CwordAndPos)
    BWindex = Collapser.get_word_index(Oleaves, CwordAndPos, MWEdict)
    Combiner = ModelCombiner(depsA, depsB, MWEdict, BWindex, medEdges = medEdges)
   
    # combine the dependencies
    depsC = Combiner.combine()

    # write to file
    for dep in depsC:
        out.write(dep.__str__())
    out.write("<\s>\n")
out.close()

print "Done!"
