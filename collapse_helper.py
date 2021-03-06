"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 11/08/2014
=============================================================================================
DESCRIPTION
=============================================================================================
Helper functions for MWE_collapse_tree as well as model_combiner
=============================================================================================
CLASSES AND FUNCTIONS
=============================================================================================
Class:
MWE, to facilitate the use of MWE information when processing a tree or dependencies
in a tree
--------------------------------------------------------------------------------------------
Functions:
decollapse() and get_mwe_span_from_coll_leaves()
to retrieve information about MWEs in collapsed leaves of a tree 
"""
import re
import sys

class MWE():
    """
    A class to facilitate the use of MWE information when
    processing the tree
    @todo: find better name for MWEUs and mwe_rep
    @todo: parametrize the + sign
    """
    def __init__(self, mwe):
        self.mweUnits = mwe.split("_")          #a list of its individual units
        self.mwe_rep = "+".join(self.mweUnits)
        self.span = []                          # an empty list which will contain 
                                                # the span in the tree that covers the MWE leaves
        self.MWEUs = []                         # a list of mwe units with their MWE concatenated to them
        for MWEU in self.mweUnits:
            MWEU = MWEU + self.mwe_rep
            self.MWEUs.append(MWEU)
        self.tree_position = ()                 # the tree position that spans all the MWE units
        self.is_just_siblings = None            # the boolean value of whether the tree position dominates
                                                # all and only the MWE units

class leaf_collapser():
    def __init__(self, leaves, wordandpos, MWElist, method="justword"):
        """
        @param: method = justword (default) or wordandpos
        """
        self.leaves = leaves
        self.wordandpos = wordandpos
        self.MWElist = MWElist
        self.method = method
        self.collapsed_sentence = []
        
    def collapse_leaves(self):
        """
        Function: the method looks for MWE units in the tree leaves and collapse
        MWEs in them
        @base: find_mwes_in_leaves but instead of adding info in mwe span, leaves
        are directly collapsed
        --------------------------------------------------------------------------------------
        Input: a list of MWE objects and a list of the tree leaves
        --------------------------------------------------------------------------------------
        Output: a list of collapsed leaves
        """
        leaves = self.leaves
        MWElist = self.MWElist

        ln = -1 #Counter used to get leaves from left to right (+1 = move one to the right)
        i = -1

        while ln < len(leaves) -1:
            ln += 1
            while i < len(MWElist) - 1:
                i += 1
                mwe = MWElist[i]
                # An MWEerror can occur if MWEs are not tokenized in the same way as in the tree
                # e.g: the MWERecognizer finds oakland_a 
                # but 'a' appears as a leaf with 's in the tree to form the a's token
                MWEerror = False
                # Number of MWE units covered
                mwen = -1
                while mwen < len(mwe.mweUnits)-1:
                    mwen += 1
                    # 1/ Check for a matching leaf from left to right
                    try:
                        while (mwe.mweUnits[mwen] != leaves[ln].lower()):
                            #print mwe.mweUnits[mwen], leaves[ln].lower()
                            self.append_leaf(ln)
                            ln +=1
                            
                        # if the coming leaves (if any) correspond to the coming
                        # fill mwe_span
                        if matching_lists(leaves[ln:(ln + len(mwe.mweUnits) - mwen)], \
                                              mwe.mweUnits[mwen:len(mwe.mweUnits)]):
                            mwe.span.append(ln)
                            ln += 1
    
                        else:
                            # otherwise continue with current mwe unit and append current leaf
                            mwen -= 1
                            self.append_leaf(ln)
                            ln += 1
                    
                    except: 
                        # If there's a MWE error: pop the MWE line, continue
                        IndexError
                        #indexerrors += 1
                        MWElist.pop(i)
                        i -= 1
                        MWEerror = True
                        #print IndexError
                        break
                    
                if MWEerror:
                    # and reset the leaf counter
                    # print "MWEerror\n"
                    prev_mwe = MWElist[mwen]
                    ln = prev_mwe.span[len(prev_mwe.span)]
                    continue
                else:
                    #when mwe is found, append it to leaves
                    """
                    @warning: this is not the real pos tag so don't use
                    this method if you need the pos tag
                    """
                    if self.method == "wordandpos":
                        wordAndPos = mwe.mwe_rep, "Fake_Pos"
                        self.collapsed_sentence.append(wordAndPos)
                    else:
                        self.collapsed_sentence.append(mwe.mwe_rep)
            #if there's any remaining leaf
            if ln != len(leaves):
                self.append_leaf(ln)
                
        return self.collapsed_sentence
    
    def append_leaf(self, ln):
        if self.method == "justword":
            self.collapsed_sentence.append(self.leaves[ln])
        else:
            self.collapsed_sentence.append(self.wordandpos[ln])

"""
=========================================================================================
HELPER FUNCTIONS
=========================================================================================
"""
        
def matching_lists(l1, l2):
    """
    Function to check whether lists match:
    If all items are identical it returns True
    Otherwise it returns False
    -------------------------------------------
    Input: 2 lists
    -------------------------------------------
    Output: boolean value of whether they match
    -------------------------------------------
    """
#         if len(l1) != len(l2): #should always be the same length, need to check?
#             return False
#         else:
    for l_i,val in enumerate(l1):
        if val.lower() == l2[l_i].lower():
            True
        else:
            return False
    return True

def decollapse(Cleaves):
    """
    Function to retrieve mwes from the collapsed leaves and to
    decollapse the leaves back to their original indices
    ---------------------------------------------------
    Input:
    a list of collapsed leaves joined by a '+'
    e.g: [mr.+vinken, is, chairman, of, elsevier.+n.v., the, Dutch, publishing, group]
    ---------------------------------------------------
    Output:
    a list of mwe objects and the original leaves
    e.g:
    [mr., vinken, is, chairman, of, elsevier, n.v., the, Dutch, publishing, group]
    ---------------------------------------------------
    """
    Oleaves = []
    MWElist = []
    mwe_join = re.compile(r"\+") 
    """
    @warning: if there are + signs for other reasons in the data this could
    lead to problems
    """
    for leaf in Cleaves:
        m = re.search(mwe_join, leaf)
        if m:
            leaf = re.sub("\+", "_", leaf, sys.maxint)
            mwe = MWE(leaf)
            MWElist.append(mwe)
            for mweUnit in mwe.mweUnits:
                Oleaves.append(mweUnit)
        else:
            Oleaves.append(leaf)
    return MWElist, Oleaves
    

def get_mwe_span_from_coll_leaves(MWElist, Oleaves, Cleaves):
    """
    Function to retrieve the span of the mwe units leaves in the original
    tree
    ---------------------------------------------------
    Input: a list of mwes with empty span
    a list of original leaves
    a list of collapsed leaves
    ---------------------------------------------------
    Output:
    the MWElist with updated information for the mwe spans
    ---------------------------------------------------
    """
    #original leaves counter
    oln = 0
    #collapsed leaves counter
    cln = 0
    mwen = -1
    while mwen < len(MWElist) - 1:
        mwen += 1
        mwe = MWElist[mwen]
        span_filled = False
        while oln < len(Oleaves):
            # when original and collapsed leaves are the same
            # increment the counters
            if Oleaves[oln] == Cleaves[cln]:
                oln += 1
                cln += 1
            else:
                # for each MWE unit: add the next index to the span and 
                # increment original leaves counter
                for item in mwe.mweUnits:
                    mwe.span.append(oln)
                    oln += 1     
                cln += 1
                # Get to the next mwe
                span_filled = True
                break
                             
        if span_filled:
            continue
        
def get_deps_from_parg(lines):
    """
    @todo: move to some file helper or something
    Put dependencies from parg files lines into a data structure usable
    by the collapser: a list of lists
    ------------------------------------------------------------------------
    Input: the lines of a dependency structure of a sentence in .parg format
    -------------------------------------------------------------------------
    Output: a list of lists of dependencies with the structure:
    i j cat_j arg_k word_i word_j
    """
    deps = []
    for x in range(1,len(lines)):
        deps.append([])
        deptuple = lines[x].split("\t")
        if len(deptuple) == 5:
            words = deptuple[4].split(" ")
            for item in deptuple[0:4]:
                item = item.strip()
                deps[x-1].append(item)
            for word in words:
                word = word.strip()
                if word != "":
                    deps[x-1].append(word)
    try:
        deps.pop()
    except:
        IndexError
    return deps
