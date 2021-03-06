"""
@author: Miryam de Lhoneux, mdelhoneux@gmail.com
@note: feel free to send me an email if you have any question
This code is not copyrighted but if used, please cite
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
@date: 04/06/2014
Script to collapse MWEs in CCG trees.
Implementation of MWE_collapser on 3 different trees from CCGbank
"""
from ccg_nltk_trees import *
import MWE_collapse_tree
from nltk import ccg
from nltk import tree


"""
@summary:  This is what I worked on for sibling MWEUnits
"Mr Vinken is chairman of Elsevier N.V the Dutch publishing group"
"""
treeAutofile = "///group/corpora/public/ccgbank/data/AUTO/00/wsj_0001.auto"
treeID = "wsj_0001.2"
MWElist = ["mr._vinken", "elsevier_n.v."]

"""
@summary: this is what I worked with for non sibling MWEs
"""
#treeAutofile = "///group/corpora/public/ccgbank/data/AUTO/00/wsj_0004.auto"
#treeID = "wsj_0004.4"
#MWElist = ["according_to"]


"""
@summary: this is what I worked with to make sure everything fits together
"""
#treeAutofile = "///group/corpora/public/ccgbank/data/AUTO/00/wsj_0012.auto"
#treeID = "wsj_0012.10" 
#MWElist = ["mr._spoon", "shore_up", "a_drop_of", "according_to", "publishers_information_bureau"]


"""
Testing
"""

Tree = get_Tree(treeAutofile, treeID)
Tree.draw()
Collapser = MWE_collapse_tree.MWE_tree_collapser(Tree,MWElist, method = "OnlySiblings")
Collapser.collapse_tree()
Tree = Collapser.Tree
Tree.draw()
