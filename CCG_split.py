"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 03/06/2014
Script to split CCGbank into training and test data
"""
import os
import re
import sys
"""
usage:
python CCG_split.py CCGdir outdir (MWEdir True (if dealing with model B)) 
"""
    
def split(CCGdir, outdir, modelB=False): 
    CCGparg = "%s/PARG"%CCGdir 
    CCGauto = "%s/AUTO"%CCGdir
    testN = {"23":0}
    heldoutN = {"00":0}
    trainingN = {"01":0,"02" : 0,"03":0,"04":0,"05":0,"06":0,"07":0,"08":0,"09":0,"10":0,"11":0,\
                 "12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0}
    
    IDpattern = re.compile(r"(ID=(wsj_\d*\.\d*))(.*)\n")
    
    heldout = "%s/heldout.raw"%outdir
    autoheldout = "%s/heldout.gs.auto"%outdir
    autotraining = "%s/training.auto"%outdir
    autotest = "%s/test.gs.auto"%outdir
    pargtest = "%s/test.gs.parg"%outdir
    rawtest = "%s/test.raw"%outdir
    mwetest = "%s/test.mwe"%outdir
    
    heldout = open(heldout, "w")
    autoheldout = open(autoheldout, "w")
    autotraining = open(autotraining, "w")
    autotest = open(autotest, "w")
    pargtest = open(pargtest, "w")
    rawtest = open(rawtest, "w")
    
    if modelB:
        testdir = "%s/TEST"%outdir
        mwetest = open(mwetest, "w")
    
    for number in os.listdir(CCGparg):
        number_dir = "%s/%s"%(CCGparg,number)
        files = os.listdir(number_dir)
        files.sort()
        for ccg_filename in files:
                pargfile = "%s/%s/%s"%(CCGparg,number,ccg_filename)
                autofilename = ccg_filename.strip(".parg") + ".auto"
                autofile = "%s/%s/%s"%(CCGauto,number,autofilename)
                testfilename = ccg_filename.strip(".parg") + ".raw"
                testfile = "%s/%s"%(testdir,testfilename)
                heldoutfilename = ccg_filename.strip(".parg") + ".raw"
                heldoutfile = "%s/%s"%(testdir,heldoutfilename)
                if modelB:
                    mwefilename = ccg_filename.strip(".parg") + ".mwe"
                    mwefile = "%s/%s/%s"%(CCGMWEs, number, mwefilename)
                if number in trainingN:
                    for linea in open(autofile):
                        autotraining.write(linea)
                elif number in heldoutN:
                    for lineh in open(heldoutfile):
                        mh = re.search(IDpattern, lineh)
                        if not mh:
                            heldout.write(lineh)
                    for lineah in open(autofile):
                        autoheldout.write(lineah)
                elif number in testN:
                    for linep in open(pargfile):
                        pargtest.write(linep)
                    for linet in open(testfile):
                        m = re.search(IDpattern, linet)
                        if not m:
                            rawtest.write(linet)
                    for lineat in open(autofile):
                        autotest.write(lineat)
                    if modelB:
                        for linem in open(mwefile):
                            mwetest.write(linem)
    autotraining.close()
    pargtest.close()
    rawtest.close()
    mwetest.close()
    autoheldout.close()
    autotest.close()
    
if __name__=="__main__":
    CCGdir = sys.argv[1]
    outdir = sys.argv[2] 
    if (len(sys.argv) > 3 and sys.argv[4] == "True"):
        CCGMWEs = sys.argv[3]
        modelB = True
    else: 
        modelB = False
    split(CCGdir, outdir, modelB)
