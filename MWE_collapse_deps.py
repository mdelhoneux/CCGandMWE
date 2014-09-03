"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 02/07/2014
Script to collapse MWEs in CCG dependencies
The main method is collapse()
----------------------------------------------------
Input: a list of dependencies, a list of MWEs  a list
of leaves of the non-collapsed tree and a list of leaves and their
PoS category in the collapsed tree
----------------------------------------------------
Output: collapsed dependencies
"""

class dependency():
    """
    Class to turn a parg style list into a dependency object
    functions: initialise and write back to parg format
    --------------------------------------------------------
    Input of init: a list of lists containing the dependency information
    in the CCGbank .parg format:
    i, j, cat_j, arg_k, word_i, word_j
    --------------------------------------------------------
    Output of init:
    an object dependency containing this information
    --------------------------------------------------------
    """
    def __init__(self, dependency):
        self.i = dependency[0]
        self.j = dependency[1]
        self.cat_j = dependency[2]
        self.arg_k = dependency[3]
        self.word_i = dependency[4]
        self.word_j = dependency[5]
        if len(dependency) > 6:
            self.word_j_bis = ' '.join(dependency[5:len(dependency)+1])
        else:
            self.word_j_bis = self.word_j
            
    def __str__(self):
        return "%s\t%s\t%s\t%s\t%s\t%s\n"%(self.i,self.j,self.cat_j,\
                                           self.arg_k,self.word_i,self.word_j_bis)

class MWE_deps_collapser():
    def __init__(self, deps, MWElist, Oleaves, CwordAndPos):
        """
        Initialisation: a list of dependencies, a list of MWE objects
        (see MWE_collapse.MWE()), a list of leaves of the non-collapsed tree 
        and a list of leaves and their PoS category in the collapsed tree
        -----------------------------------------------------------------
        MWE information is put into a multilayered dictionary.
        MWE unit (key), original index (key)
        tuple: MWE, original index of the MWE , pos of MWE (value)
        ------------------------------------------------------------------
        In addition, there is a words index dictionary containing all 
        non-mwe words with their index in the original and in the 
        collapsed version:
        word (key) - original_index (key) - new_index (value)
        """
        self.deps = deps
        self.MWEdict = self.get_MWE_dict(MWElist,Oleaves,CwordAndPos)
        self.WordsIndex = self.get_word_index(Oleaves,CwordAndPos,self.MWEdict)
        self.cyclenumbers = 0
        
    def get_MWE_dict(self,MWElist,Oleaves,CwordAndPos):
        """
        Function to get the MWE_dict described in initialisation
        Deal with MWEs from left to right
        -Find the index of the collapsed MWE in the collapsed leaves
        -Find the index of the MWE unit in the non-collapsed leaves
        -----------------------------------------------------------
        Input: the list of MWEs, the leaves of the original tree and
        the leaves of the collapsed tree with their PoS
        -----------------------------------------------------------
        Output: a dictionary with information about MWEs described
        in initialisation
        """
        MWEdict = {}
        #original leaves counter
        oln = 0
        #collapsed leaves counter
        cln = 0
        for mwe in MWElist:
            # Find the index of the collapsed MWE in the collapsed leaves
            while (mwe.mwe_rep != CwordAndPos[cln][0]):
                #print mwe.mwe_rep, CwordAndPos[cln][0], "\n"
                cln +=1
            #Find the index of the MWE unit in the non-collapsed leaves
            for mwen, MWEU in enumerate(mwe.mweUnits):
                while (oln != mwe.span[mwen]):
                        """
                        @warning: this may cause infinite loop
                        if there's a problem in the data
                        """
                        oln +=1
                if MWEU not in MWEdict:
                    MWEdict[MWEU] = {}
                # Add to dictionary
                MWEdict[MWEU][oln.__str__()] = mwe.mwe_rep, cln.__str__(), CwordAndPos[cln][1]
            #once dealt with an mwe
            cln += 1
        return MWEdict

    def get_word_index(self,Oleaves,CwordAndPos,MWEdict):
        """
        Function: get a word index of original and changed leaf position 
        of all words which are not MWEs
        ---------------------------------------------------------------
        Input: a list of original leaves, a list of collapsed leaves
        and a dictionary of MWEs
        -------------------------------------------------------------
        Output: a dictionary containing a key for each non-mwe leaf
        containing a dictionary with a key for its position and
        the new position as value
        ---------------------------------------------------------------
        """
        WIndex = {}
        #collapsed leaves counter
        cln = 0
        
        #Look at each original leaf from left to right
        for oln, Oleaf in enumerate(Oleaves):
            # If it is not in the MWE dictionary or if its position is not in the dictionary
            if ((Oleaf.lower() in MWEdict and oln.__str__() not in MWEdict[Oleaf.lower()]) \
                or (Oleaf.lower() not in MWEdict)):
                    if Oleaf not in WIndex:
                        WIndex[Oleaf] = {} 
                        """
                        @todo: catch error?
                        """
                    while (Oleaf != CwordAndPos[cln][0]):
                        cln += 1
                    # add it to the word index with its position in the collapsed tree
                    WIndex[Oleaf][oln.__str__()] = cln.__str__()
                    # increment collapsed leaves counter
                    cln += 1
        return WIndex
    
    def collapse(self):
        """
        Function to collapse dependencies of MWEs in a sentence
        --------------------------------------------------------
        Input: a list of dependencies, a list of MWEs, a list of
        leaves in their original position and a list of leaves and
        their category in their collapsed position
        --------------------------------------------------------
        Output: collapsed dependencies
        """
        MWEd = self.MWEdict
        deps = self.deps
        # get dependency objects
        for i in range(len(deps)):
            self.deps[i] = dependency(deps[i])
        WIndex = self.WordsIndex
            
        n = -1
        while n < len(deps)-1:
            n += 1
            dep = deps[n]

            # If word_i and word_j are MWE units: pop the line
            if ((dep.word_i.lower() in MWEd and dep.i in MWEd[dep.word_i.lower()]) \
                 and (dep.word_j.lower() in MWEd and dep.j in MWEd[dep.word_j.lower()])):
                # if they are units of the same MWE
                if MWEd[dep.word_i.lower()][dep.i] == MWEd[dep.word_j.lower()][dep.j]:
                    #print "same mwe\n"
                    deps.pop(n)
                    n -= 1
                else:
                    #change i
                    mwe_i = MWEd[dep.word_i.lower()][dep.i][0]
                    dep.i = MWEd[dep.word_i.lower()][dep.i][1]
                    dep.word_i = mwe_i
                    #change j
                    mwe_j = MWEd[dep.word_j.lower()][dep.j][0]
                    # change cat_j
                    dep.cat_j = MWEd[dep.word_j.lower()][dep.j][2]
                    # change indices
                    dep.j = MWEd[dep.word_j.lower()][dep.j][1]
                    dep.word_j = mwe_j
                    
                # otherwise change the dependency
            # If word_i is a MWE unit: replace it with its MWE and change indices    
            elif (dep.word_i.lower() in MWEd and dep.i in MWEd[dep.word_i.lower()]):
                # get mwe
                mwe = MWEd[dep.word_i.lower()][dep.i][0]
                dep.i = MWEd[dep.word_i.lower()][dep.i][1]
                dep.j = WIndex[dep.word_j][dep.j]
                
                #change mwe
                dep.word_i = mwe
            
            # If word_j is a MWE unit: replace it with its MWE, change cat_j
            # and change indices       
            elif (dep.word_j.lower() in MWEd and dep.j in MWEd[dep.word_j.lower()]):
                # change MWE unit  to MWE
                mwe = MWEd[dep.word_j.lower()][dep.j][0]
                
                # change cat_j
                dep.cat_j = MWEd[dep.word_j.lower()][dep.j][2]
                # change indices
                dep.j = MWEd[dep.word_j.lower()][dep.j][1]
                dep.i = WIndex[dep.word_i][dep.i]
                dep.word_j = mwe
                
            # else: just change the other words indices
            else:
                dep.j = WIndex[dep.word_j][dep.j]
                dep.i = WIndex[dep.word_i][dep.i]

    
    def get_deps_dict(self):
        """
        Get dependency of dictionaries in both directions
        @return: two dictionaries, one with left_to_right
        dependencies, one with right_to_left dependencies
        """
        deps = self.deps
        #left to right and right to left dependencies
        ltr_dep = {}
        rtl_dep = {}
        # Dictionaries of relations
        for dep in deps:
            word_i = dep.word_i,dep.i
            if word_i not in  ltr_dep:
                ltr_dep[word_i] = {}
                word_j = dep.word_j_bis, dep.j
                if word_j not in ltr_dep[word_i]:
                    ltr_dep[word_i][word_j] = 0
            if word_j not in rtl_dep:
                rtl_dep[word_j] = {}
                if word_i not in rtl_dep[word_j]:
                    rtl_dep[word_j][word_i] = 0
        return ltr_dep, rtl_dep
    
    def count_cycles(self):
        """
        Count cyclic dependencies
        """
        ltr_dep, rtl_dep = self.get_deps_dict()
        # check for each relation whether there is another reversed one
        # in which case increment
        for word in ltr_dep:
            for rel in ltr_dep[word]:
                if word in rtl_dep:
                    if rel in rtl_dep[word]:
                        self.cyclenumbers += 1
