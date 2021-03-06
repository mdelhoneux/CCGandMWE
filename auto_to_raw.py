"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 09/06/2014
script to write test and heldout .auto files to a raw equivalent
usage:
$python auto_to_raw CCGbankir Outdir
"""
from ccg_nltk_trees import get_Tree
import os
import re
import sys

# Create a directory for the raw files, unless it already exists

ccgdir = sys.argv[1]
number_dir_heldout = "%s/AUTO/00"%ccgdir  
number_dir_test = "%s/AUTO/23"%ccgdir 

CCGout = sys.argv[2]
try:
    os.mkdir(CCGout)
except:
    OSError
IDpattern = re.compile(r"(ID=(wsj_\d*\.\d*))(.*)\n")


def auto_to_raw(number_dir):
    i = 0
    for ccg_filename in os.listdir(number_dir):
            raw_filename = ccg_filename.strip(".auto")
            outfile = open("%s/%s.raw"%(CCGout,raw_filename), "w")
            treeAutofile = "%s/%s"%(number_dir,ccg_filename)
            text = ''.join(open(treeAutofile, "r").readlines())
            # Find the ID line
            m = re.findall(IDpattern, text)
            for match in m:
                i+=1
                outfile.write("%s%s\n"%(match[0],match[2]))
                treeID = match[1]
                Tree = get_Tree(treeAutofile, treeID)
                sentence = " ".join(Tree.leaves())
                outfile.write("%s\n"%sentence)
            outfile.close()
            
print "converting auto file to raw"
auto_to_raw(number_dir_heldout)
auto_to_raw(number_dir_test)
print "Done!"
