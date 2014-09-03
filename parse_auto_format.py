"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 22/07/2014
====================================================================================
DESCRIPTION
====================================================================================
script to turn a parsed file from StatOpenCCG to a file closer to the CCGbank format
and usable for evaluation
------------------------------------------------------------------------------------
usage:
$python parse_auto_format infile outfile
------------------------------------------------------------------------------------
Input:
a file in .auto style obtained by StatOpenCCG
------------------------------------------------------------------------------------
Output:
a file closer to CCGbank format
------------------------------------------------------------------------------------
"""
import re
import sys
print "converting parse to auto format"
infile = open(sys.argv[1],"r")
outfile = open(sys.argv[2], "w")
parsedPattern = re.compile(r"(Sentence (\d*):(.*)\n)")
failedparse = re.compile(r"(Sentence (\d*): no parse: No vit. parse\n)")
for line in infile:
    if not line.startswith("#"):
        fm = re.search(failedparse, line)
        if fm:
            outfile.write("ID=wsj_23.%s PARSER=GOLD NUMPARSE=1\n"%fm.group(2))
            outfile.write(" no parse: No vit. parse\n")
        else:
            m = re.search(parsedPattern, line)
            if not m:
                outfile.write(line)
            else:
                outfile.write("ID=wsj_23.%s PARSER=GOLD NUMPARSE=1\n"%m.group(2))
print "Done!"
