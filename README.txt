Transform the Spanish MCR 3.0 database so that it can be loaded using the nltk WordNet reader.

This file has a quick user guide to transform and use the Spanish MCR 3.0 files, as well as a description of the overall transformation process and its limitations.

This software was created by Grupo de Procesamiento de Lenguaje Natural from Instituto de Computación, Facultad de Ingeniería, Universidad de la República, Uruguay. Any questions or comments can be addressed at Luis Chiruzzo (luischir@fing.edu.uy).

=================================================
Contents:

i) Transforming the Spanish MCR 3.0 corpus
ii) Using the transformed Spanish MCR 3.0 corpus
iii) Exporting and importing the glosses
iv) Description of the process and limitations

=================================================
i) Transforming the Spanish MCR 3.0 corpus:

You will need:
* The Multilingual Central Repository 3.0 corpus, which can be downloaded from http://adimen.si.ehu.es/web/MCR/
* The NLTK toolkit, which can be downloaded from http://www.nltk.org/
* The WordNet corpus for NLTK, which can be downloaded using nltk.download() after NLTK is installed.

1 - Copy the WordNet 3.0 database files (they can be found in nltk_data/corpora/wordnet) into another directory, e.g. nltk_data/corpora/wordnet_es.
    The location of these files might vary in your installation. We will refer to the WordNet 3.0 database folder as WORDNET_EN_ROOT. We will refer to folder you just created for the Spanish files as WORDNET_ES_ROOT.
2 - Extract the MCR 3.0 files to a folder. This will create a series of folders containing WordNet versions for different languages.
    In particular the mcr30/spaWN contains the Spanish files. We will refer to this folder as SPANISH_MCR_ROOT.
    NOTE: This process has been tested only for the Spanish MCR files, but in theory it should work as well for the other languages. You would only need to change the file name references in the code.
3 - In a Python shell, import the transform module
4 - Execute the following command:
    >> transform.transform(<path to SPANISH_MCR_ROOT>, <path to WORDNET_EN_ROOT>, <path to WORDNET_ES_ROOT>)

After step 4, the data.* and index.* files contained in WORDNET_ES_ROOT will be replaced with new versions containing the Spanish MCR 3.0 information. 

=================================================
ii) Using the transformed Spanish MCR 3.0 corpus:

1 - Open a Python shell.
2 - Import the NLTK library
    >> import nltk
3 - Create a WordNet reader, but use the Spanish files instead of the default one
    >> wn = nltk.corpus.reader.wordnet.WordNetCorpusReader(<path to WORDNER_ES_ROOT>)

Now you can use the object wn to query the contents of WordNet in Spanish, for example:
    >> print wn.synset("entidad.n.01").definition

=================================================
iii) Exporting and importing the glosses:

MCR is a work in progress and not all the contents have been fully translated to Spanish. This is specially true about glosses, because only around 15% of the glosses are in Spanish. For some applications this might be an issue.
However, if you have another source where you can get the Spanish glosses (for example using a machine translation process) you can import that data so it can be merged with the MCR 3.0 during the transformation.

1 - In a Python shell, import the transform module
2 - Execute the following command:
    >> transform.export_glosses(<path to WORDNET_EN_ROOT>, <path to EN_GLOSSES_FILE>)
    This creates the file EN_GLOSSES_FILE, which will contain the English glosses for all synsets. The file format is straightforward. Each line contains the gloss for one synset in this format:
<id> | <gloss>
    Where <id> is a concatenation of the offset in the WordNet 3.0 database file and the part of speech of the synset. For example, the synset corresponding to "entity" in English has this line:
00001740n | that which is perceived...
3 - Translate the glosses using any means you can.
    As long as the format is honored and the identifiers are kept, the process will be able to get the translated glosses and merge them with the rest of the data.
    We will assume that you have created a new file ES_GLOSSES_FILE containing the translated glosses.
4 - In the Python shell, execute the following command:
    >> transform.transform(<path to SPANISH_MCR_ROOT>, <path to WORDNET_EN_ROOT>, <path to WORDNET_ES_ROOT>, <path to ES_GLOSSES_FILE>)
    The tranformation method accepts an optional fourth parameter, where you can specify the translated glosses file to use.

=================================================
iv) Description of the process and limitations:

The transformation process is straightforward. We load the synsets, variants and relations files from MCR. Then we use that information to create data and index files respecting the constraints of the WordNet database files.

In particular, we must respect the constraint that the synset with numeric id XX must start in the offset XX of the data file. This is mandatory in order to use the NLTK WordNet reader, as it uses this fact to speed up the queries. However, this has an unfortunate consequence, which is that the numeric id of the English and Spanish files do not match. For example, the synset for "dog.n.01" has the offset 02084071 but the synset for "perro.n.01" has the offset 01397192. This also means that it is no longer possible to match "perro.n.01" back to its MCR identifier spa-30-02084071-n, which points to the English file offset.

The definition of realtions in MCR and WordNet differ. In MCR there are more relations defined, and it is not always easy to known which corresponds with which. However, the most usual relations (such as hyponym/hypernym and meronym/holonym) have been correctly mapped. The mapping of MCR relations that are transformed to WordNet relations follows (note that some of the mappings could be wrong and change in the future):

MCR									WordNet
Id	Name LR			Name RL			LR	Name LR							RL	Name RL
--------------------------------------------------------------------------------------------------------
1	be_in_state		state_of		=	Attribute						=	Attribute
2	causes			is_caused_by	>	cause
4	has_derived		is_derived_from	\	derived from adjective
6	has_holo_madeof	has_mero_madeof	#s	substance holonym				%s	substance meronym
7	has_holo_member	has_mero_member	#m	member holonym					%m	member meronym
8	has_holo_part	has_mero_part	#p	part holonym					%p	part meronym
12	has_hyponym		has_hyperonym	~	hyponym							@	hypernym
19	has_subevent	is_subevent_of	*	entailment
33	near_antonym	-				!	antonym							!	antonym
34	near_synonym	-				&	similar							&	similar
49	see_also_wn15	-				^	also see
52	verb_group		-				$	verb group						$	verb group
63	category_term	category		-c	member of this domain - topic	;c	domain of synset - region
64	related_to		-				+	derivationally related form		+	derivationally related form
66	region_term		region			-r	member of this domain - region	;r	domain of synset - region
68	usage_term		usage			-u	member of this domain - usage	;u	domain of synset - usage
