"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 04/06/2014
Script to collapse MWEs in CCGbank
usage:
python CCGbank_collapse.py CCGbankdir MWEdir Outdir method 
@todo: do more sophisticated parametrising
-------------------------------------------------------------------------
Input: CCGbank directories (.auto and .parg files) and a CCGbank directory 
of (.mwe) files containing:
the ID of each tree and their list of mwes separated by a space and with
units joined by an underscore
e.g:
san_francisco_bay end_up
-------------------------------------------------------------------------
Output: a CCGbank with collapsed trees (.auto files) and dependencies 
(.parg)
"""

from MWE_collapse_tree import MWE_tree_collapser
from MWE_collapse_deps import MWE_deps_collapser
from collapse_helper import get_deps_from_parg
import os
import re
import time
from ccg_nltk_trees import get_Tree
import sys

def make_dir(dirpath):
    try:
        os.mkdir(dirpath)
    except:
        OSError

"""
Converting CCGbank
"""
start = time.clock()
indexerrors = 0
number_of_siblings = 0
number_of_non_siblings = 0
"""
Input data
@todo: parametrise
"""
CCGbankdir = sys.argv[1]
CCGparg = "%s/PARG"%CCGbankdir
CCGauto = "%s/AUTO"%CCGbankdir
CCGMWEs = sys.argv[2]
detectorDescription = "%s/description.txt"%CCGMWEs

"""
Output data
"""
#Create a description files and output directories
CCGout = sys.argv[3]
make_dir(CCGout)
CCGoutparg = "%s/PARG"%CCGout
CCGoutauto = "%s/AUTO"%CCGout
descriptionfile = "%s/description.txt"%CCGout
make_dir(CCGoutparg)
make_dir(CCGoutauto)

"""
ID patterns
"""
IDpattern = re.compile(r"(ID=(wsj_\d*\.\d*))(.*)\n(.*)\n")
IDpatternB = re.compile(r"<s id=\"(.*)\"> \d*(.*)") # just the id pattern

"""
Parameters
@todo: make this an optional parameter when other functions work
"""
#method = sys.argv[4]
method = "OnlySiblings"
#method = "Rightmost"
#method = "Leftmost"

"""
Write parameters to description file
"""
outfile = open(descriptionfile, "w")
for line in open(detectorDescription):
    outfile.write(line)
outfile.write("Collapsing method: \n%s\n"%method)

i = 0
print "collapsing CCGbank"
for number in os.listdir(CCGparg):
    number_dir = "%s/%s"%(CCGparg,number)
    make_dir("%s/%s"%(CCGoutparg,number))
    make_dir("%s/%s"%(CCGoutauto,number))
    for ccg_filename in os.listdir(number_dir):
        # join all files as text strings
        outdepsfile = open("%s/%s/%s"%(CCGoutparg,number,ccg_filename), "w")
        treefilename = ccg_filename.strip(".parg") + ".auto"
        outtreefile = open("%s/%s/%s"%(CCGoutauto,number,treefilename), "w")
        mwefilename = ccg_filename.strip(".parg") + ".mwe"
        mwefile = "%s/%s/%s"%(CCGMWEs,number,mwefilename)
        textM = ''.join(open(mwefile, "r").readlines())     
        
        treefilename = ccg_filename.strip(".parg") + ".auto"
        treeAutofile = "%s/%s/%s"%(CCGauto,number,treefilename)
        textT = ''.join(open(treeAutofile, "r").readlines())
        
        depsfile = "%s/%s/%s"%(CCGparg,number,ccg_filename)
        textD = ''.join(open(depsfile, "r").readlines())
        sentences = textD.split('<\\s>\n')
        sentences.pop()
        
        
        # Find the ID line in the tree file and in the mwe file
        mT = re.findall(IDpattern, textT) #treefile
        mM = re.findall(IDpattern, textM) #mwefile
        """
        @warning: lengths must be same as len(mT) and len(mM)
        """
        for s_i in range(len(sentences)): 
            matchT = mT[s_i]
            matchM = mM[s_i]
            sentence = sentences[s_i]
            lines = sentence.split("\n")            
            # If the tree IDs correspond
            mD = re.findall(IDpatternB,lines[0]) #parg file
            if matchT[1] == matchM[1] == mD[0][0]:
                #write the sentence ID
                outdepsfile.write("%s\n"%(lines[0]))
                outtreefile.write("%s%s\n"%(matchT[0],matchT[2]))
                i+=1
                # get the list of mwes
                MWElist = matchM[3].split(" ")
                MWElist.pop()
                
                # get the tree
                treeID = matchT[1]
                Tree = get_Tree(treeAutofile, treeID)
                #Original leaves
                Oleaves = Tree.leaves()
                #Collapse the tree and get collapser information
                TCollapser = MWE_tree_collapser(Tree,MWElist, method = method)
                TCollapser.collapse_tree()
                Tree = TCollapser.Tree
                t = Tree.pprint()
                indexerrors += TCollapser.indexerrors
                number_of_siblings += TCollapser.number_of_siblings
                number_of_non_siblings += TCollapser.number_of_non_siblings
                
                # write to .auto file
                outtreefile.write("%s\n"%t)
                
                #get the dependencies
                deps = get_deps_from_parg(lines)
                # Get the collapsed leaves and pos
                CwordAndPos = Tree.get_word_and_pos()
                Collapser = MWE_deps_collapser(deps, MWElist, Oleaves, CwordAndPos)
                Collapser.collapse()

                # write to .parg file
                for dep in deps:
                    outdepsfile.write(dep.__str__())
                outdepsfile.write("<\s>\n")
                outdepsfile.flush()
        outtreefile.close()
        outdepsfile.close()
end = time.clock()
totaltime = end - start
outfile.write("Total number of index errors: %d\n"%indexerrors)
outfile.write("Total number of MWEs that are sibling in the tree: %d\n"%number_of_siblings)
outfile.write("Total number of MWEs that are not sibling in the tree: %d\n"%number_of_non_siblings)
pecentage_of_siblings = number_of_siblings/float(number_of_siblings + number_of_non_siblings)
outfile.write("Percentage of MWEs that are sibling in the tree: %0.4f\n"%pecentage_of_siblings)
outfile.write("Total processing time:%.2gs \n"%(end-start))
outfile.close()
print "Done!"
