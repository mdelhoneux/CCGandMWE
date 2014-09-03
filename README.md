This file contains code created for the following project:
de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
A file inventory with a small description of each program we created for the project as well as a few files we modified for the project

=======================================================================================================
1. FILE INVENTORY
=======================================================================================================

1.1 mwe_recognizer
#######################################################################################################
prerequisites:
*the libraries jMWE (http://projects.csail.mit.edu/jmwe/) and the stanford-postagger in lib/
*A raw version of CCGbank containing sentences ID, e.g.: 
ID=wsj_0001.1 PARSER=GOLD NUMPARSE=1
#######################################################################################################
MWERecognizer.java
	----------------------------------------------------------------------------------------------
	Compiling
	javac -cp lib/*:. MWERecognizer.java
	Usage
	java -cp "bin:lib/*" MWERecognizer.java OUTDIR CCGbank_raw
	----------------------------------------------------------------------------------------------
	Input:
	a sentence
	e.g:
	Mr. Vinken is chairman of Elsevier N.V., the Dutch publishing group
	Output:
	a list of Multiword Expressions
	e.g:
	mr._vinken, elsevier_.n.v.
	----------------------------------------------------------------------------------------------
	Note:
	The recognizer runs with the detector that performed best with our project: the one
	that only detects Proper Nouns. It was difficult to parametrize but it is an intended future 
	change. In the meantime, commented lines show other possibilities
	
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
1.2 CCGandMWE
#######################################################################################################
prerequisites:
NLTK and python 2.6
A CCGbank directory with subdirectories /AUTO and /PARG containing .auto and .parg files
Warning: most files have dependencies and moving files out of it might be problematic
#######################################################################################################
------------------------------------------------------------------------------------------------------
CLASSES AND FUNCTIONS
------------------------------------------------------------------------------------------------------
CCG_nltk_trees.py
	----------------------------------------------------------------------------------------------
	-functions based on ccg_draw_trees.py from openccg
	to load trees from CCGbank .auto files
	-a CCGtree class inheriting from nltk.tree.Tree in which the pprint function is overriden
	and other functions are created
	----------------------------------------------------------------------------------------------
MWE_collapse_tree.py
	----------------------------------------------------------------------------------------------
	-contains the MWE_tree_collapser class
	Script to collapse MWE units in a tree.
	The MWE_collapser is initialised with a binary CCGtree and a list of MWEs. Optionally, the method
	(OnlySiblings by default) can be changed to Rightmost or to Leftmost. 
	The list of MWEs must be a left-to-right list of MWEs in the tree sentence and words cannot 
	appear in more than one MWE.
	----------------------------------------------------------------------------------------------
	-main method: collapse_tree()
	INPUT
	a binary tree and a list of MWEs with all fields filled (see MWE init)
	OUTPUT
	a collapsed tree
	----------------------------------------------------------------------------------------------
MWE_collapse_deps.py
	-Script to collapse MWEs in CCG dependencies
	----------------------------------------------------------------------------------------------
	main method: collapse()
	Input: a list of dependencies, a list of MWEs  a list of leaves of the non-collapsed tree and 
	a list of leaves and their PoS category in the collapsed tree
	Output: collapsed dependencies
	----------------------------------------------------------------------------------------------
	additionally, there is a count_cycles method to check for cyclic dependencies
	----------------------------------------------------------------------------------------------
model_combiner.py
	DESCRIPTION
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
	----------------------------------------------------------------------------------------------
	Main function: combine()
	Input: dependencies A and B, the MWE dictionary and its reversed version and 
        the reversed word index from model B
        Output: combined dependencies
	----------------------------------------------------------------------------------------------
collapse_helper.py
	Helper functions and classes for MWE_collapse_tree, MWE_collapse_deps and model_combiner
	classes:
	*MWE
	A class to facilitate the use of MWE information when processing the tree
	*leaf_collapser
	A class to collapse MWEs in leaves (i.e. a list of words)
	functions:
	*matching_lists
	Check whether lists match: if all items are identical it returns True otherwise it returns 
	False
	*decollapse
	Function to retrieve mwes from the collapsed leaves and to decollapse the leaves back to 
	their original indices
	*get_mwe_span_from_coll_leaves
	Function to retrieve the span of the mwe units leaves in the original tree
	*get_deps_from_parg
	Put dependencies from parg files lines into a data structure usable by the collapser: a list
	of lists
	----------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------
TEXT PROCESSING
------------------------------------------------------------------------------------------------------
CCGbank_collapse.py
	Script to collapse MWEs in CCGbank
	usage:
	$python CCGbank_collapse.py CCGbankdir MWEdir Outdir
	----------------------------------------------------------------------------------------------
	Input: CCGbank directories (.auto and .parg files) and a CCGbank directory of (.mwe) files 
	containing: the ID of each tree and their list of mwes separated by a space and with units 
	joined by an underscore 
	e.g: san_francisco_bay end_up
	Output: a CCGbank with collapsed trees (.auto files) and dependencies (.parg)
	----------------------------------------------------------------------------------------------
CCGbank_to_raw.py
	Script to write a raw version of CCG which matches the leaves of the trees from the .auto files
	usage:
	$python CCGbank_to_raw.py CCGbankdir Outdir
	----------------------------------------------------------------------------------------------
CCG_split.py
	script to split CCGbank data in the tradition way (01-22 for training, 00 for development
	and 23 for testing)
	usage:
	python CCG_split.py CCGdir outdir (MWEdir True (if dealing with collapsed CCGbank)) 
	----------------------------------------------------------------------------------------------
	Output:
	heldout.raw"
    	heldout.gs.auto"
    	training.auto"
    	test.gs.auto"
    	test.gs.parg"
    	test.raw"
    	(test.mwe")
    	----------------------------------------------------------------------------------------------
    	note:
    	if using a collapsed version of CCGbank, it needs a directory /TEST containing files .mwe
    	with sentence IDs and their list of mwes separated by a space and with units 
	joined by an underscore 
	e.g: san_francisco_bay end_up
	----------------------------------------------------------------------------------------------
auto_to_raw.py
	script to write test (section 23) and heldout (section 00) .auto files to a raw equivalent
	usage:
	$python auto_to_raw CCGbankir Outdir
	----------------------------------------------------------------------------------------------
cc_to_parser_tag.py
	Script to turn a .stagged file to a .tag file which will be used to train a generative CCG parser
	input:
	No|RB|S/S ,|,|, it|PRP|NP was|VBD|(S[dcl]\NP)/NP n't|RB|(S\NP)\(S\NP) black_monday|N|N .|.|.
	output:
	No_DT ,_, it_PRP was_VBD n't_RB Black_NNP Monday_NNP ._. 
	usage:
	$python cc_to_parser_tag.py infile outfile
	----------------------------------------------------------------------------------------------
combine_models.py 
	script to combine dependencies of two models as described in model_combiner.py
	usage:
 	python combine_models.py pargA pargB autoB out medEdges
 	medEdges can be fromA, rightmostB or leftmostB
 	----------------------------------------------------------------------------------------------
collapse_pargfile.py
 	Script to collapse MWEs in CCGbank-style parg files
	usage:
	$python collapse_pargfile.py autofile pargfile mwefile outfile
	----------------------------------------------------------------------------------------------
	Input: CCGbank files (.auto) (.parg ) and a (.mwe) files containing:
	the ID of each tree and their list of mwes separated by a space and with
	units joined by an underscore
	e.g:
	san_francisco_bay end_up
	Output: the parg files collapsed
	----------------------------------------------------------------------------------------------
parse_auto_format.py
	script to turn a parsed file from StatOpenCCG to a file closer to the CCGbank format
	and usable for evaluation
	usage:
	$python parse_auto_format infile outfile
	----------------------------------------------------------------------------------------------
	Input:
	a file in .auto style obtained by StatOpenCCG
	Output:
	a file closer to CCGbank format
	----------------------------------------------------------------------------------------------
collapse_raw.py
	script to collapse MWEs in a raw file
	usage:
	$python collapse_raw.py rawfile mwefile outfile
	the mwefile contains:
	the ID of each tree and their list of mwes separated by a space and with
	units joined by an underscore
	e.g:
	san_francisco_bay end_up
	Output: the parg files collapsed
	----------------------------------------------------------------------------------------------
CollapseTreesDemo.py
	script to show a graphical demonstration of our code on a sentence
	usage:
	python CollapseTreesDemo.py
	a picture will appear with a tree and if closed, its collapsed
	version will appear
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
