"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 04/06/2014
@todo: rename MWE_collapse_trees.py or MWE_collapser to MWE_tree_collapser
@bug: rightmost collapsing and leftmost collapsing seem to be doing something wrong:
using either makes the data non-usable with StatOpenCCG
=============================================================================================
DESCRIPTION
=============================================================================================
Script to collapse MWE units in a tree.
The MWE_collapser is initialised with a binary CCG tree and a list of MWEs. Optionally, the method
(OnlySiblings by default) can be changed to Rightmost or to Leftmost. 
The list of MWEs must be a left-to-right list of MWEs in the tree sentence and words cannot 
appear in more than one MWE.
=============================================================================================
MAIN METHOD of main class: MWE_tree_collapser.collapse_tree()
=============================================================================================
FUNCTION
Collapse the MWEs in the tree.
When MWE units are siblings, it replaces their parent node with the collapsed MWE as leaf
and the parent node label as label.
When MWE units are not sibling, they are discarded by the OnlySiblings method, they are 
collapsed to the rightmost MWE unit with the Rightmost method or to the leftmost MWE unit 
(Leftmost method) and the individual node labels are deleted.
--------------------------------------------------------------------------------------------
INPUT
a binary tree and a list of MWEs with all fields filled (see MWE init)
--------------------------------------------------------------------------------------------
OUTPUT
a collapsed tree
--------------------------------------------------------------------------------------------
NOTE:
alternatively, the tree leaves can be directly collapsed
=============================================================================================
"""

from ccg_nltk_trees import CCGTree
from collapse_helper import matching_lists, MWE
            

class MWE_tree_collapser():
    """
    Initialisation: a binary CCGtree (see ccg_nltk_trees.CCGTree() and a list of MWEs. 
    Optionally, method="Leftmost" or method = "Rightmost" (the default is OnlySiblings)
    """
    def __init__(self, Tree, MWElist, method = "OnlySiblings"):
        assert type(Tree) == CCGTree
        self.Tree = Tree
        self.leaves = self.Tree.leaves()
        self.leavesTreePos = self.Tree.treepositions("leaves")
        self.MWElist = self.get_MWE_info(MWElist)
        self.method = method
        self.dummytree = self.get_dummytree()   
        self.number_of_siblings = 0
        self.number_of_non_siblings = 0
        self.indexerrors = 0
        
    def get_MWE_info(self,MWElist):
        for n, mwe in enumerate(MWElist):
            if type(mwe) == str:
                mwe_obj = MWE(mwe)
                MWElist[n] = mwe_obj
        return MWElist
    
    def get_dummytree(self):
        return CCGTree('DummyNode', ['DummyWord'])
    
    def sibling_label(self, tree):
        """
        Function to format the label of the collapsed sibling MWEs
        The parent node CCGcat is used three times to match
        the CCGbank data structure:
        CCGcat mod_PoS orig_PoS
        """
        labelitems = tree.label().split("\', \'")
        label = labelitems[0]
        label = label.strip("\[\'")
        label = label, label, label
        return label
    
    
    def mark_matching_leaves(self, Tree, mwe):
        """
        Function to mark the matching leaves of the MWE units in a tree
        ---------------------------------------------------------------
        Input: the tree and the mwe
        ---------------------------------------------------------------
        Output: a tree with MWE units leaves marked with their corresponding
        mwe
        """
        for ln in mwe.span:
            Tree[self.leavesTreePos[ln]] = Tree[self.leavesTreePos[ln]] + mwe.mwe_rep
            
    def find_mwes_in_leaves(self, MWElist, leaves):
        """
        Function: the method looks for MWE units in the tree leaves and updates
        the span of the MWE: it adds the index of each MWE unit to the span
        --------------------------------------------------------------------------------------
        Input: a list of MWE objects and a list of the tree leaves
        --------------------------------------------------------------------------------------
        Output: an updated span for each mwe in the MWE list
        """
        ln = 0 #Counter used to get leaves from left to right (+1 = move one to the right)
        i = -1

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
                        ln +=1
                        
                    # if the coming leaves (if any) correspond to the coming
                    # MWE units, add to span
                    if matching_lists(leaves[ln:(ln + len(mwe.mweUnits) - mwen)], \
                                          mwe.mweUnits[mwen:len(mwe.mweUnits)]):
                        mwe.span.append(ln)
                        ln += 1

                    else:
                        # otherwise continue with current mwe unit
                        mwen -= 1
                        ln += 1
                
                except: 
                    # If there's a MWE error: pop the MWE line, continue
                    IndexError
                    self.indexerrors += 1
                    MWElist.pop(i)
                    i -= 1
                    MWEerror = True
                    break
                
            if MWEerror:
                # and reset the leaf counter
                ln = 0
                continue
            
    def get_mwe_tree_info(self, MWElist, Tree):
        """
        Function to get information about each MWE's position in the tree
        -----------------------------------------------------------------------------
        Input: a list of MWEs with information about their span (see find_mwes_in_leaves())
        and the Tree
        -----------------------------------------------------------------------------
        Output:
        *the position of the node that spans all the MWEs
        *the boolean value of whether this position spans all and only the MWE units
        in the tree
        -----------------------------------------------------------------------------
        """
        for mwe in MWElist:
            # Get the tree position that spans the MWEunits leaves
            mwe.tree_position = Tree.treeposition_spanning_leaves(mwe.span[0],\
                                                   mwe.span[len(mwe.span)-1]+1)
            # get the boolean value of whether this node position 
            # spans all and only the MWE leaves
            mwe.is_just_siblings = len(Tree[mwe.tree_position].leaves()) == len(mwe.mweUnits)
        
    def collapse_tree(self):
        # If the MWE list is empty: do nothing and return
        if len(self.MWElist) == 0:
            return self.Tree
        else:
            return self._collapse_tree(self.MWElist,self.Tree)
        

    def _collapse_tree(self,MWElist,Tree):
        """
        Function: collapse a tree given a list of MWEs.
        For subtrees that span all and only the MWE leaves, it collapses the  MWE units to one 
        node with the label of their common dominating node.
        For other subtrees, it recurses the subtree and collapses the MWEs according to the method
        (Rightmost or Leftmost) or does nothing (OnlySiblings)
        ------------------------------------
        Input: a binary tree and a list of MWEs with all fields filled (see MWE init)
        ------------------------------------
        Output: a tree with collapsed MWEs.
        ------------------------------------
        """
        # 1/ Find MWEs in the leaves and then in the tree and update MWElist 
        #(see MWE_collapser.find_mwes_in_leaves() and get mwe_tree_info())
        self.find_mwes_in_leaves(MWElist, self.leaves)
        self.get_mwe_tree_info(MWElist, Tree)

        # 2/ Collapse each subtree
        mwe_i = -1
        while mwe_i < len(MWElist) - 1:
            mwe_i += 1
            mwe = MWElist[mwe_i]
            # Collapse the sibling nodes (the ones where the node position spans
            # all and only the MWE units): the leaf is the collapsed MWE and the label
            # is the parent label
            if mwe.is_just_siblings: 
                self.number_of_siblings += 1

                if mwe.tree_position == (): #In case the tree position of spanning leaves is the whole tree
                    Tree = CCGTree(self.sibling_label(Tree), [mwe.mwe_rep])
                else:
                    Tree[mwe.tree_position] = \
                    CCGTree(self.sibling_label(Tree[mwe.tree_position]), [mwe.mwe_rep])

            # Collapse the non-sibling nodes if method requires
            else:
                self.number_of_non_siblings += 1
                if self.method == "OnlySiblings":
                    MWElist.pop(mwe_i)
                    mwe_i -= 1
                    continue
                else:
                    self.mark_matching_leaves(Tree, mwe)
                    if mwe.tree_position == (): # In case the tree position of spanning leaves is the whole tree
                        #Tree.draw()
                        Tree = self.collapse_subtree(Tree,mwe)
                    else:
                        #Tree[mwe.tree_position].draw()
                        Tree[mwe.tree_position] = self.collapse_subtree(Tree[mwe.tree_position], mwe)
                        
        # 3/Get rid of the dummy nodes and/or return tree
        if self.method != "OnlySiblings":
            self.Tree = self.del_dummy_nodes(Tree)
        else:
            self.Tree = Tree
        
    
    def collapse_subtree(self, tree, mwe):
        """
        ============================================================
        @bug: This function never returns an error but using it makes
        the data non-usable with StatOpenCCG parsing so it is probably
        doing something quite wrong
        ============================================================
        (Function adapted from geoparser.py written for NLU assignment 1)
        Function: recursively collapses MWE units to their rightmost/leftmost
        node and replaces any other node with a dummy tree (which can be replaced with the 
        MWE_collapser.del_dummmy_nodes() method).
        The default method is the rightmost method.
        The leftmost method can be used by specifying method = "Leftmost" when instantiating
        the collapser.
        -----------------------------------------------------
        Input: a subtree
        Output: a subtree with collapsed MWEs and dummy trees
        -----------------------------------------------------
        """
        children = self.get_children(tree)
        
        #Base decision on the number of children
        
        """
        1/No children, it's a lexical item
        With the rightmost method, MWEs are collapsed to the rightmost leaf
        With the leftmost method, MWEs are collapsed to the leftmost leaf
        """
        
        if len(children) == 0:
            # Check if the item corresponds to rightmost or leftmost MWE according to method
            if (self.method == "Rightmost" and \
                 tree[0].lower() == mwe.MWEUs[len(mwe.mweUnits)-1])\
            or (self.method == "Leftmost" and \
                tree[0].lower() == mwe.MWEUs[0]):
                    #Replace it with the collapsed MWE
                    tree[0] = mwe.mwe_rep
                    return tree
            # else, if it's part of the MWE, return a dummy tree
            elif tree[0].lower() in mwe.MWEUs:
                return self.dummytree
            # Otherwise return the tree
            else:
                return tree
        
            """
            2/One|Two children: recurse child(ren)
            """
        elif len(children) == 1:
            tree[0] = self.collapse_subtree(children[0],mwe)
            return tree

        else:
            tree[0] = self.collapse_subtree(children[0],mwe)
            tree[1] = self.collapse_subtree(children[1],mwe)
            
            return tree
        
        
    def del_dummy_nodes(self,tree):
        """
        (Function adapted from geoparser.py written for the NLU assignment)
        Function : recursively delete dummy nodes in a tree.
        ----------------------------------
        Input: a tree with dummy trees
        Output: a tree without dummy trees
        ----------------------------------
        """
        
        #Get children
        children = self.get_children(tree)
        
        #Base next decision on the number of children
        """
        0 : return
        """
        if len(children) == 0:
            return tree
            """
            1: replace parent of dummy trees by dummy trees
            """
        
        elif len(children) == 1:
            tree[0] = self.del_dummy_nodes(children[0])
            if tree[0] == self.dummytree:
                return self.dummytree
            return tree
        
            """
            3/ Two children: recurse each child, check for dummy trees and get rid of them
            """
        else:
            tree[0] = self.del_dummy_nodes(children[0])
            tree[1] = self.del_dummy_nodes(children[1])
            
            # if both children are dummy trees, replace the tree by a dummy tree
            if (tree[0] == self.dummytree) and (tree[1] == self.dummytree):
                return self.dummytree
            
            #Get rid of dummy trees
            # Left-branching dummy trees
            elif tree[0] == self.dummytree: 
                tree[0] = tree[1]
                tree.pop()   
            # Right-branching dummy trees
            else:
                try:
                    if tree[1] == self.dummytree: 
                        tree[1] = tree[0]
                        tree.pop()
                except:
                    IndexError
            return tree
        
    def get_children(self,tree):
        """
        Method borrowed from geolib.py
        @author: Siva Reddy
        (Version made available to students for the assignment 1 of the course
        Natural Language Understanding @The University of Edinburgh, academic year 2013-2014)
        Function: get children of a tree
        -------------------------------
        Input: a tree
        Output: the tree's children
        -------------------------------
        """
        subtrees = self.get_subtrees(tree)
        children = []
        i = 1
        while i < len(subtrees):
            children.append(subtrees[i])
            subsubtrees = self.get_subtrees(subtrees[i])
            i = i + len(subsubtrees)
        return children
    
    def get_subtrees(self,tree):
        """
        @note: comment from MWE_collapse.get_children() applies.
        returns all the subtrees including the main tree of a tree. 
        """
        subtrees = [subtree for subtree in tree.subtrees()]
        return subtrees
