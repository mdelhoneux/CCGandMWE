"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 24/07/2014
==================================================================================
DESCRIPTION
==================================================================================
Script to combine two dependency graphs A and B where B has the same leaves as A
but some are collapsed to one unit (called MWE for convenience).
e.g:
sentence A: Mr. Vinken is chairman of Elsevier N.V.
sentence B: mr._vinken is chairman of elsevier_n.v

The combiner needs information about MWEs and leaf indices from sentence A in MWEdict and BWindex
(see MWE_collapse_tree.decollapse and get_mwe_span_from_coll_leaves
and MWE_collapse_deps.get_MWE_dict and get_word_index() for how to do that).

The combiner always takes internal edges from A (e.g. the dependency between Mr. and Vinken),
external edges from B (e.g. dependency between is and chairman) and for mediating edges, it 
depends on the option "medEdges". "fromA" (default) takes them from A, rightmost and 
leftmost take them from B. Rightmost replaces the MWE with its
rightmost unit and leftmost replaces the MWE with its leftmost
unit in the dependency
==================================================================================
Main function
==================================================================================
combine()
----------------------------------------------------------------------------------
Input: dependencies A and B, the MWE dictionary and its reversed version and 
        the reversed word index from model B
----------------------------------------------------------------------------------
Output:
combined dependencies
----------------------------------------------------------------------------------
"""
from MWE_collapse_deps import dependency
"""
@todo: use defaultdict
terminology: 
o_i = original index
n_i = new index
@todo: there's a lot of code deleting potential here, I've been writing a lot to make sure stuff is understandable
but there's quite a bit of repeating
"""

class ModelCombiner():
    def __init__(self, depsA, depsB, MWEdict, BWindex, medEdges = "fromA"):
        """
        Initialisation: dependencies from model A and dependencies from model B
        MWEdict from model B, WordIndex from model B
        ------------------------------------------------------------
        Option: 
        medEdges = 
                    -"fromA" (default): take mediating edges from A
                    -"rightmostB" : take mediating edges from B, choose
                    rightmost MWE unit as dependency head
                    -"leftmostB": take mediating edges from B, choose
                    leftmost MWE unit as dependency head
        ------------------------------------------------------------
        """
        self.depsA = depsA
        self.depsB = depsB
        self.medEdges = medEdges
        self.depsC = []
        self.MWEdict = MWEdict
        self.MWEd_rev = self.reverse_MWEdict(MWEdict)
        self.Windex = self.reverse_Windex(BWindex)
        
    def reverse_MWEdict(self,MWEdict):
        """
        Function: reverse the MWEdict obtained from the deps_collapser
        to obtain a dictionary usable by the combiner
        --------------------------------------------------------------
        Input:
        MWEdict:
        MWE unit (key), original index (key)
        tuple: MWE, original index of the MWE , pos of MWE (value)
        --------------------------------------------------------------
        Output:
        MWEd
        MWE (key) - original index of the MWE (key) - MWE unit (key)
        original index of the MWE unit (value)
        --------------------------------------------------------------
        """
        MWEd = {}
        for mweUnit in MWEdict:
            for o_i in MWEdict[mweUnit]:
                MWE = MWEdict[mweUnit][o_i][0]
                MWE_o_i = MWEdict[mweUnit][o_i][1]
                if MWE not in MWEd:
                    MWEd[MWE] = {}
                if MWE_o_i not in MWEd[MWE]:
                    MWEd[MWE][MWE_o_i] = {}
                MWEd[MWE][MWE_o_i][mweUnit] = o_i
        return MWEd
    
    def reverse_Windex(self,BWindex):
        """
        Function: reverse the Word index obtained from the deps_collapser
        --------------------------------------------------------------
        Input:
        Word index:
        word (key) - original_index (key) - new_index (value)
        --------------------------------------------------------------
        Output:
        reversed word index
        word (key) - new index (key) - original index (value)
        --------------------------------------------------------------
        """
        Windex = {}
        for word in BWindex:
            if word not in Windex:
                Windex[word] = {}
            for o_i in BWindex[word]:
                n_i = BWindex[word][o_i]
                Windex[word][n_i] = o_i
        return Windex
    
    def get_edges_from_A(self):
        """
        Function to get internal edges from A and optionally
        mediating edges
        ------------------------------------------------------------
        Input: nothing
        ------------------------------------------------------------
        Output: an updated dependency list with internal
        edges from A and optionally mediating edges
        ------------------------------------------------------------        
        """
        for depA in self.depsA:
            # internal edges
            #If word_i and word_j are MWE units take the dependency
            if ((depA.word_i.lower() in self.MWEdict and \
                 depA.i in self.MWEdict[depA.word_i.lower()]) and \
                  (depA.word_j.lower() in self.MWEdict and \
                   depA.j in self.MWEdict[depA.word_j.lower()])):
                #print "getting internal edge"
                self.depsC.append(depA)
            # mediating edges
            elif ((depA.word_i.lower() in self.MWEdict and \
                 depA.i in self.MWEdict[depA.word_i.lower()]) \
                 or (depA.word_j.lower() in self.MWEdict and \
                     depA.j in self.MWEdict[depA.word_j.lower()])):
                if self.medEdges == "fromA":
                    self.depsC.append(depA)
                
                
    def get_B_med_edge_i(self, medEdges, depB):
        """
        Function to get the right mediating edge according to option
        when word_i is a mwe
        ------------------------------------------------------------
        Input: option and dependency
        ------------------------------------------------------------
        Output: the right dependency
        ------------------------------------------------------------
        """
        depC = depB 
        mwe_unit, index = self.get_mweUnit(self.MWEd_rev[depB.word_i.lower()][depB.i])
        depC.word_i = mwe_unit
        depC.i = index
        depC.j = self.Windex[depB.word_j][depB.j]
        self.depsC.append(depC)
        
    def get_B_med_edge_j(self, medEdges, depB):
        """
        Function to get the right mediating edge according to option
        when word_j is a mwe
        ------------------------------------------------------------
        Input: option and dependency
        ------------------------------------------------------------
        Output: the right dependency
        ------------------------------------------------------------
        """
        depC = depB
        mwe_unit, index = self.get_mweUnit(self.MWEd_rev[depB.word_j.lower()][depB.j])
        depC.word_j = mwe_unit
        depC.j = index
        depC.i = self.Windex[depB.word_i][depB.i]
        self.depsC.append(depC)
        
    def get_B_med_edges(self, medEdges, depB):
        """
        Function to get the right mediating edge according to option
        when word_i and word_j are mwes
        ------------------------------------------------------------
        Input: option and dependency
        ------------------------------------------------------------
        Output: the right dependency
        ------------------------------------------------------------
        @warning: simplifying assumption that there's only one
        dependency between the two mwes
        """
        depC = depB
        mwe_i , i = self.get_mweUnit(self.MWEd_rev[depB.word_i.lower()][depB.i])
        depC.word_i = mwe_i
        depC.i = i
        mwe_j, j = self.get_mweUnit(self.MWEd_rev[depB.word_j.lower()][depB.j])
        depC.word_j = mwe_j
        depC.j = j
        self.depsC.append(depC)
        
    def get_mweUnit(self, d):
        """
        Function to get the MWE we want to use to replace the mwe in the dependency
        according to option (rightmost or leftmost)
        ------------------------------------------------------------
        Input: option and mwe dictionary
        ------------------------------------------------------------
        Output: MWE unit we're interested in and its index
        """
        if self.medEdges == "rightmostB":
        # get the rightmost MWE unit: the highest original index
            rightmost_unit, rightmost_index = max(d.iteritems(), key=lambda x:x[1])
            return rightmost_unit, rightmost_index
        else:
            # get the leftmost MWE unit: the lowest original index
            leftmost_unit, leftmost_index = min(d.iteritems(), key=lambda x:x[1])
            return leftmost_unit, leftmost_index
        
    def combine(self):
        """
        Function: combining model A and model B
        @parameter: medEdges = "fromA", "rightmostB" or "leftmostB" (see init) 
        --------------------------------------
        Input: dependencies A and B, the MWE dictionry and its reversed version and 
        the reversed word index from model B
        --------------------------------------
        Output: a list of dependencies
        """
        # 1/ Get dependency objects
        for i in range(len(self.depsB)):
            self.depsB[i] = dependency(self.depsB[i])      
        for j in range(len(self.depsA)):
            self.depsA[j] = dependency(self.depsA[j])
            
        # 2/ Get internal edges from model A and optionally mediating edges
        self.get_edges_from_A()
                
            
        for depB in self.depsB:
            # 3.2// infer mediating edges from B
            # both words are a mwe
            if ((depB.word_i.lower() in self.MWEd_rev and \
                 depB.i in self.MWEd_rev[depB.word_i.lower()]) and \
                (depB.word_j.lower() in self.MWEd_rev and \
                 depB.j in self.MWEd_rev[depB.word_j.lower()])):
                if self.medEdges != "fromA":
                    self.get_B_med_edges(self.medEdges, depB)
            # word_i is a mwe
            elif (depB.word_i.lower() in self.MWEd_rev and \
                  depB.i in self.MWEd_rev[depB.word_i.lower()]):
                if self.medEdges != "fromA":
                    self.get_B_med_edge_i(self.medEdges, depB)
            # word_j is a mwe
            elif (depB.word_j.lower() in self.MWEd_rev and \
                  depB.j in self.MWEd_rev[depB.word_j.lower()]):
                if self.medEdges != "fromA":
                    self.get_B_med_edge_j(self.medEdges, depB)
            
            # 4/ Get external edges from model B
            # and change the indices
            else:
                depC = depB
                depC.i = self.Windex[depB.word_i][depB.i]
                depC.j = self.Windex[depB.word_j][depB.j]
                self.depsC.append(depC)
                
        return self.depsC
