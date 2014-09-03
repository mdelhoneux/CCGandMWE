# -*- coding: utf-8 -*-
"""
@author: openccg
@base : https://github.com/OpenCCG/openccg/blob/master/bin/ccg_draw_tree.py
    @author: Miryam de Lhoneux, mdelhoneux@gmail.com
    @date: 04/06/2014 
# Change: .node to .label() under orders of my Terminal
# Only keeping functions I need and making a wrap up function (get_Tree())
# And creating a class CCGTree inheriting from Tree
"""
from nltk.compat import string_types
from nltk import tree

def get_Tree(autofile,deriv_id, idpattern = "IDpattern"):
    """
    @author: Miryam de Lhoneux
    Input: autofile and derivation ID
    @param: idpattern
        Use default if ID looks like:
        ID=wsj_2300.1 PARSER=GOLD NUMPARSE=1
        Use "parsedPattern" if ID looks like:
        Sentence 1:
    ---------------------------------
    Function: get a CCGTree
    ---------------------------------
    Input: autofile and derivation ID
    -----------------------------------
    Output: a CCG Tree
    """
    if idpattern == "IDpattern":
        deriv = get_deriv(autofile, deriv_id)
    elif idpattern == "parsedPattern":
        deriv = get_deriv_testfile(autofile, deriv_id)
    t = parse_ccgbank_tree(deriv)
    return t


def get_deriv(autofile, deriv_id):
    #print 'reading ' + deriv_id + ' from ' + autofile
    found_it = False
    autofile = open(autofile, 'rU')
    for line in autofile:
        if found_it == True:
            return line
        if line[0:2] == 'ID':
            if line.split()[0].split('=')[1] == deriv_id:
                found_it = True
    raise NameError('could not find ' + deriv_id + '!')

def get_deriv_testfile(autofile, deriv_id):
    """
    @author: Miryam de Lhoneux
    (modification of get_deriv)
    """
    found_it = False
    autofile = open(autofile, 'rU')
    for line in autofile:
        if found_it == True:
            return line
        if line[0:8] == 'Sentence':
            if line.split()[1].split(":")[0] == deriv_id:
                found_it = True
    raise NameError('could not find ' + deriv_id + '!')


# nb: the parents around leaves ends up creating blank nodes above leaves
def parse_ccgbank_node(s):
    """
    Get the information needed from the node: node label, index and number
    of daughters
    -------------------------------------------------------------------------------
    Input: a node CCGbank pattern
    -------------------------------------------------------------------------------
    Output: a node label
    """
    if s =='': return ''
    #s.split(' ') = [<T, node_label, index, number of daughters]
    return s.split(' ')[1:4].__str__() 

def parse_ccgbank_leaf(s):
    """
    Get the information needed from the leaf node: node is CCGcat, PoS-mod, PoS-orig
    and leaf is the word
    -------------------------------------------------------------------------------
    Input: a leaf CCGbank pattern
    -------------------------------------------------------------------------------
    Output: a CCGtree with a node and leaf
    """
    tokens = s.split(' ') #tokens = ['<L, CCGcat, PoS-mod, PoS-orig, word, PredArgCat]
    # ==> tokens[5] could be useful
    return CCGTree(tokens[1:4], [tokens[4]]) 
    
    #return CCGTree(tokens[1:6].__str__())

def excise_empty_nodes(t):
    if not isinstance(t,CCGTree): return t
    if t.label() == '': return excise_empty_nodes(t[0])
    return CCGTree(t.label(), [excise_empty_nodes(st) for st in t])

# nb: returns tree with blank nodes excised
def parse_ccgbank_tree(s):
    ccgbank_node_pattern = r'<T.*?>'
    ccgbank_leaf_pattern = r'<L.*?>'
    t = CCGTree.parse(s, 
                   parse_node=parse_ccgbank_node, 
                   parse_leaf=parse_ccgbank_leaf, 
                   node_pattern=ccgbank_node_pattern, 
                   leaf_pattern=ccgbank_leaf_pattern)
    return excise_empty_nodes(t)

def format_label(label):
    """
    @author: Miryam de Lhoneux
    """
    labelitems = label.split("\', \'")
    node = labelitems[0]
    head = labelitems[1]
    dtrs = labelitems[2]
    node = node.strip("\[\'")
    dtrs = dtrs.strip("\'\]")
    label = "%s %s %s"%(node,head,dtrs)
    return label

class CCGTree(tree.Tree):
    """
    @author: Miryam de Lhoneux
    """
    
    def get_word_and_pos(self):
        """
        Get the word and pos and put them into
        a left to right list
        """
        CwordAndPosA = self.pos()
        CwordAndPos = []
        for word, pos in CwordAndPosA:
            word, pos = word, pos[0]
            wordandpos = word, pos
            CwordAndPos.append(wordandpos)
        return CwordAndPos
    
    def pprint(self, margin=70, indent=0, nodesep='', parens='()', quotes=False):
            """
            Function: Overriding of the method pprint and __pprint_flat in NLTK.tree.Tree
                so as to write trees in .auto format
                The output contains garbage but is usable by the generative parser
            Node pattern:
                <T label head_index number of daughters> 
            Leaf pattern:
                <L CCGcat mod_PoS orig_PoS word CCGcat > 
                with the second CCGcat replacing PredArgCat
            --------------------------------
            Input: an CCGTree
            Output: a tree in .auto format
            --------------------------------
            Copyright (C) 2001-2013 NLTK Project
            Author: Edward Loper <edloper@gmail.com>
                     Steven Bird <stevenbird1@gmail.com>
                     Peter Ljungloef <peter.ljunglof@gu.se>
                     Nathan Bodenstab <bodenstab@cslu.ogi.edu> (tree transforms)
            URL: <http://nltk.org/>
            -------------------------------------------------------------
             :return: A pretty-printed string representation of this tree.
             :rtype: str
             :param margin: The right margin at which to do line-wrapping.
             :type margin: int
             :param indent: The indentation level at which printing
                 begins.  This number is used to decide how far to indent
                 subsequent lines.
             :type indent: int
             :param nodesep: A string that is used to separate the node
                 from the children.  E.g., the default value ``':'`` gives
                 trees like ``(S: (NP: I) (VP: (V: saw) (NP: it)))``.
                 """
    
        # I'm not entirely sure what this part of the function was supposed to do in 
        # the original nltk function but this simple modification seems to work
            s = self._pprint_flat(nodesep, parens, quotes)
            # remove double spaces
            s = " ".join(s.split())
            s += " "
            # remove double backslash
            s = s.replace('\\\\', '\\')
            return s

    def _pprint_flat(self, nodesep, parens, quotes):

        childstrs = []
        for child in self:
            if isinstance(child, CCGTree):
                childstrs.append(child._pprint_flat(nodesep,parens,quotes))

            elif isinstance(child, tuple):
                childstrs.append("/".join(child))
                
            elif isinstance(child, string_types) and not quotes:
                label  = self.label()
                CCGcat = label[0]
                or_pos = label[1]
                mod_pos = label[2]
                childstrs.append('<L %s %s %s %s %s>' %(CCGcat, or_pos, mod_pos, child, CCGcat))
                
            else:
                label  = self.label()
                CCGcat = label[0]
                or_pos = label[1]
                mod_pos = label[2]
                childstrs.append('<L %s %s %s %s %s>' %(CCGcat, or_pos, mod_pos, child, CCGcat))
 

        if isinstance(self._label, string_types):
#             print '%s<T %s%s %s%s ' % (parens[0], format_label(self._label), nodesep,
#                                     " ".join(childstrs), parens[1]), "\n"
            return '%s<T %s%s %s%s ' % (parens[0], format_label(self._label), nodesep,
                                    " ".join(childstrs), parens[1])
        else:
            #print ('%s%s%s '%(parens[0]," ".join(childstrs), parens[1])), "\n"
            return ('%s%s%s '%(parens[0]," ".join(childstrs), parens[1]))
