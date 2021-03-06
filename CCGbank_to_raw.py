"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 04/06/2014
Script to write a raw version of CCG which matches the leaves of the trees from the
.auto files
"""
from ccg_nltk_trees import get_Tree
import os
import re
import sys


# Create a directory for the raw CCGbank, unless it already exists
CCGbank = "%s/AUTO"%sys.argv[1]
CCGout = sys.argv[2]
try:
    os.mkdir(CCGout)
except:
    OSError


IDpattern = re.compile(r"(ID=(wsj_\d*\.\d*))(.*)\n")

print "creating raw CCGbank"
for number in os.listdir(CCGbank):
    number_dir = "///group/corpora/public/ccgbank/data/AUTO/%s"%number
    try:
        os.mkdir("%s/%s"%(CCGout,number))
    except:
        OSError
    for ccg_filename in os.listdir(number_dir):
            raw_filename = ccg_filename.strip(".auto")
            outfile = open("%s/%s/%s.raw"%(CCGout,number,raw_filename), "w")
            treeAutofile = "///group/corpora/public/ccgbank/data/AUTO/%s/%s"%(number,ccg_filename)
            text = ''.join(open(treeAutofile, "r").readlines())
            # Find the ID line
            m = re.findall(IDpattern, text)
            for match in m:
                outfile.write("%s%s\n"%(match[0],match[2]))
                treeID = match[1]
                Tree = get_Tree(treeAutofile, treeID)
                sentence = " ".join(Tree.leaves())
                outfile.write("%s\n"%sentence)
            outfile.close()
print "Done!\n"
