"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 10/06/2014
Script to turn a .stagged file to a .tag file which will be used to train a generative CCG parser
input:
No|RB|S/S ,|,|, it|PRP|NP was|VBD|(S[dcl]\NP)/NP n't|RB|(S\NP)\(S\NP) black_monday|N|N .|.|.
output:
No_DT ,_, it_PRP was_VBD n't_RB Black_NNP Monday_NNP ._. 
usage:
$python cc_to_parser_tag.py infile outfile
"""
import sys

infile = sys.argv[1] 
outfile = open(sys.argv[2], "w")
"""
@todo: add possibility of having preface lines
"""
print "converting file\n"
for line in open(infile):
    try:
        tokens = line.split(" ")
        for token in tokens:
            word, tag = token.split("|")
            token = "%s_%s "%(word,tag)
            outfile.write(token)
    # So preface is safely skipped
        """
        @warning: I hope it doesn't mess with stuff
        """
    except:
        ValueError
    
outfile.close()
print "Done!"
